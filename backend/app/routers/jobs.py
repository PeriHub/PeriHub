# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import json
import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.base import get_db

# db/models.py's JobQueueEntry powers all run-status tracking now (see
# support/solver_backend.py's module docstring) - this router looks
# entries up directly rather than only going through job_queue.py's
# helpers, for the "does this user already have this model running" and
# "what's my most recent submission of this model" lookups below.
#
# Model *configuration* (which model/model_folder_name combinations exist,
# whether their input deck/mesh has been written) still lives on local
# disk - models are generated into a shared volume mount and only the
# resulting files are submitted to the PeriLab API, so that part of this
# router keeps using FileHandler as before. Everything about a job's
# actual run - submitted/running, progress, result files, logs, cancel,
# delete - now goes exclusively through the PeriLab API (support/
# perilab_api_client.py) plus the JobQueueEntry rows that record which
# PeriLab job_id a submission became; there is no more cluster/sftp path.
from ..db.models import JOB_QUEUED, JOB_RUNNING, JobQueueEntry
from ..support import audit_log, usage_metering
from ..support.api_key_auth import get_user_name_with_api_key
from ..support.base_models import Jobs, ModelData, Status
from ..support.db_auth import resolve_user
from ..support.file_handler import FileHandler
from ..support.globals import dev, log, max_concurrent_local_jobs
from ..support.job_concurrency import count_active_local_jobs, has_capacity
from ..support.job_cost import estimate_job_cost
from ..support.job_queue import cancel_running, enforce_user_quota, submit_job
from ..support.solver_backend import get_solver_backend

router = APIRouter(prefix="/jobs", tags=["Jobs Methods"])


def _job_run_status(db: Session, request: Request, model_name: str, model_folder_name: str) -> dict:
    """Run status for a model folder - submitted/running, result files,
    and progress - sourced entirely from the DB (JobQueueEntry) and the
    PeriLab API (support/perilab_api_client.py). No filesystem or cluster
    access: whether a job has produced result files is answered by GET
    /jobs/{job_id}/files, not by looking at disk. Returns all-false/None
    if there's no logged-in DB user or no matching JobQueueEntry."""
    empty = {
        "submitted": False,
        "results": False,
        "csvResults": False,
        "progress": None,
        "currentStep": None,
        "totalSteps": None,
    }

    identity = resolve_user(request, dev, db)
    if identity.user is None:
        return empty

    entry = db.scalar(
        select(JobQueueEntry)
        .where(
            JobQueueEntry.user_id == identity.user.id,
            JobQueueEntry.model_name == model_name,
            JobQueueEntry.model_folder_name == model_folder_name,
        )
        .order_by(JobQueueEntry.submitted_at.desc())
    )
    if entry is None:
        return empty

    result = dict(empty)
    result["submitted"] = entry.status in (JOB_QUEUED, JOB_RUNNING)

    if not entry.perilab_job_id:
        return result

    client = get_solver_backend().client()
    # A comma-separated perilab_job_id (batch submission, see
    # PeriLabSolverBackend.submit) reports progress for its first job
    # only - good enough for a single progress bar.
    job_ids = [jid.strip() for jid in entry.perilab_job_id.split(",") if jid.strip()]
    if not job_ids:
        return result

    if entry.status == JOB_RUNNING:
        try:
            job = client.get_job(job_ids[0])
            result["progress"] = job.progress
            result["currentStep"] = job.current_step
            result["totalSteps"] = job.total_steps
        except HTTPException:
            pass

    # Result files only mean something once the job has actually started -
    # skip the API call while it's still sitting in the queue.
    if entry.status != JOB_QUEUED:
        for job_id in job_ids:
            try:
                for filename in client.list_files(job_id):
                    if filename.endswith(".e"):
                        result["results"] = True
                    if filename.endswith(".csv"):
                        result["csvResults"] = True
            except HTTPException:
                continue

    return result


@router.post("/run", operation_id="run_model")
async def run_model(
    model_data: ModelData,
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    verbose: bool = False,
    job_ids: Optional[str] = "-1",
    request: Request = "",
    db: Session = Depends(get_db),
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)
    username = get_user_name_with_api_key(request, dev, username)

    # ModelData.discretization doesn't currently carry a node count field,
    # so this is best-effort and usually falls back to
    # CostEstimate(tier="unknown") - see job_cost.py.
    node_count = getattr(model_data.discretization, "nodeCount", None)
    cost_estimate = estimate_job_cost(node_count)

    # Fair-share queueing requires knowing which DB user is submitting -
    # every submission now requires a database-backed account (see the
    # 501 below), so this is always resolvable.
    identity = resolve_user(request, dev, db)
    db_user = identity.user
    if db_user is not None:
        try:
            enforce_user_quota(db, db_user)
        except ValueError as exc:
            audit_log.record(username, "run_model", model_name, request, result="rejected_quota")
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc

    # Submitting a simulation always requires a database-backed account
    # (DATABASE_URL configured, and a real login rather than an API
    # key/trial session) - status, log streaming and cancel are tracked
    # per-account, with no filesystem-only fallback.
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=(
                "Submitting a simulation requires a database-backed account "
                "(DATABASE_URL configured, and a real login rather than an API key/trial "
                "session)."
            ),
        )

    # Instance-wide back-pressure: jobs run through the PeriLab API, so cap
    # how many can be in flight at once instead of silently piling them
    # all on.
    if not has_capacity(db):
        active = count_active_local_jobs(db)
        log.warning(
            "Rejecting %s: %d/%d jobs already active",
            model_name,
            active,
            max_concurrent_local_jobs,
        )
        audit_log.record(username, "run_model", model_name, request, result="rejected_capacity")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"{active}/{max_concurrent_local_jobs} simulation slots are in use. "
                "Please retry once a running job finishes."
            ),
        )

    # The model/mesh files themselves are written to the shared volume
    # mount by model.py/generate.py before this endpoint is called; this
    # router no longer copies anything anywhere - the PeriLab API reads
    # (or is handed, on submit) whatever already lives at remotepath.
    remotepath = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)

    usage_metering.record_job_submission(username, model_name, model_folder_name, False, False, node_count)
    audit_log.record(username, "run_model", model_name, request)

    existing = db.scalar(
        select(JobQueueEntry).where(
            JobQueueEntry.user_id == db_user.id,
            JobQueueEntry.model_name == model_name,
            JobQueueEntry.model_folder_name == model_folder_name,
            JobQueueEntry.status.in_((JOB_QUEUED, JOB_RUNNING)),
        )
    )
    if existing is not None:
        log.warning("%s already submitted", model_name)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=model_name + " already submitted",
        )

    args = "-v" if verbose else ""

    # No queue: submit straight to the PeriLab API. If this fails (API
    # unreachable, bad input deck, etc.) submit_job marks the entry FAILED
    # and re-raises - let that propagate (HTTPException -> 502, or whatever
    # the solver backend raised) rather than pretending the job is running.
    try:
        entry = submit_job(
            db,
            db_user,
            model_name,
            model_folder_name,
            remotepath,
            project_id=None,
            node_count=node_count,
            solver_args=args,
            num_procs=model_data.job.tasks,
            job_ids=job_ids,
        )
    except Exception as exc:
        audit_log.record(username, "run_model", model_name, request, result="rejected_submit_failed")
        raise

    log.info("%s has been submitted", model_name)
    return {
        "status": "running",
        "job_id": entry.id,
        "perilab_job_id": entry.perilab_job_id,
        "cost_estimate": cost_estimate.__dict__,
    }


@router.put("/cancel", operation_id="cancel_job")
def cancel_job(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    request: Request = "",
    db: Session = Depends(get_db),
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)
    username = get_user_name_with_api_key(request, dev, username)

    usage_metering.record_job_cancellation(username, model_name, model_folder_name, False)
    audit_log.record(username, "cancel_job", model_name, request)

    # Cancelling a running job means telling the PeriLab API to cancel the
    # job_id it gave us at submit time (see support/solver_backend.py) -
    # which means finding the JobQueueEntry that holds that id.
    identity = resolve_user(request, dev, db)
    if identity.user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required.")

    entry = db.scalar(
        select(JobQueueEntry).where(
            JobQueueEntry.user_id == identity.user.id,
            JobQueueEntry.model_name == model_name,
            JobQueueEntry.model_folder_name == model_folder_name,
            JobQueueEntry.status.in_((JOB_QUEUED, JOB_RUNNING)),
        )
    )
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=model_name + " is not running")

    cancel_running(db, entry)
    log.info("Job has been canceled")


@router.get("/getJobFolders", operation_id="get_job_folders")
def get_job_folders(
    model_name: str = "Dogbone",
    request: Request = "",
) -> List[str]:
    """Model-folder discovery: which model_folder_name variants exist for
    this model. This is local model *configuration*, generated onto the
    shared volume mount ahead of submission - the PeriLab API has no
    concept of it, so it stays filesystem-based."""
    username = FileHandler.get_user_name(request, dev)

    localpath = FileHandler.get_local_model_path(username, model_name)

    if not os.path.exists(localpath):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No jobs")

    job_folders = next(os.walk(localpath))[1]

    return job_folders


@router.get("/getJobs", operation_id="get_jobs")
def get_jobs(
    model_name: str = "Dogbone",
    request: Request = "",
    db: Session = Depends(get_db),
) -> List[Jobs]:
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    jobs = []

    localpath = FileHandler.get_local_model_path(username, model_name)

    if not os.path.exists(localpath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LogFile can't be found in " + localpath,
        )

    for _, dirs, _ in os.walk(localpath):
        for model_folder_name in dirs:
            modelpath = os.path.join(localpath, model_folder_name)

            if os.path.exists(modelpath):
                job = Jobs(
                    id=len(jobs) + 1,
                    name=model_name,
                    sub_name=model_folder_name,
                    cluster=False,
                    created=True,
                    submitted=False,
                    results=False,
                )

                # Model configuration (still local disk - see module
                # docstring): pick up the saved model JSON if present.
                remotepath = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)
                if os.path.exists(remotepath):
                    for filename in os.listdir(remotepath):
                        if filename.endswith(".json"):
                            filepath = os.path.join(remotepath, filename)
                            with open(filepath) as f:
                                data = json.load(f)
                                job.model = data

                # Actual run status - DB + PeriLab API only.
                run_status = _job_run_status(db, request, model_name, model_folder_name)
                job.submitted = run_status["submitted"]
                job.results = run_status["results"]
                job.progress = run_status["progress"]
                job.currentStep = run_status["currentStep"]
                job.totalSteps = run_status["totalSteps"]
                jobs.append(job)

    return jobs


@router.get("/getStatus", operation_id="get_status")
def get_status(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    meshfile: Optional[str] = None,
    request: Request = "",
    db: Session = Depends(get_db),
) -> Status:
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    job_status = Status()

    # Model configuration existence (has this model_folder_name been
    # generated onto the shared volume mount yet) - local disk, since the
    # PeriLab API has no notion of it.
    localpath = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)

    if os.path.exists(localpath):
        job_status.created = True

    if meshfile is None or os.path.exists(os.path.join(localpath, meshfile)):
        job_status.meshfileExist = True

    # Everything about the actual run - submitted/running, result files,
    # progress - comes only from the DB + PeriLab API now. No more
    # cluster/sbatch/sftp branch.
    run_status = _job_run_status(db, request, model_name, model_folder_name)
    job_status.submitted = run_status["submitted"]
    job_status.results = run_status["results"]
    job_status.csvResults = run_status["csvResults"]
    job_status.progress = run_status["progress"]
    job_status.currentStep = run_status["currentStep"]
    job_status.totalSteps = run_status["totalSteps"]

    return job_status
