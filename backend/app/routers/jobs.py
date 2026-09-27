# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import json
import os
from datetime import datetime, timezone
from typing import Iterator, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db.base import get_db

# db/models.py's JobQueueEntry powers all run-status tracking now (see
# support/solver_backend.py's module docstring). A model_name/
# model_folder_name pair is *not* a 1:1 stand-in for "the job" any more -
# a folder can be resubmitted, and each submission gets its own durable
# JobQueueEntry.id ("run_id"). That id, not the folder name, is what
# GET /jobs/{run_id} and PUT /jobs/{run_id}/cancel key off; getJobs/
# getStatus below still take a folder and summarize its *latest* run for
# convenience, but GET /jobs/{model_name}/{model_folder_name}/runs exposes
# the full history so nothing about an older run is lost once a folder is
# resubmitted.
#
# Model *configuration* (which model/model_folder_name combinations exist,
# whether their input deck/mesh has been written) still lives on local
# disk - models are generated into a shared volume mount and only the
# resulting files are submitted to the PeriLab API, so that part of this
# router keeps using FileHandler as before. Everything about a job's
# actual run - submitted/running, progress, result files, logs, cancel,
# delete - goes exclusively through the PeriLab API (support/
# perilab_api_client.py) plus the JobQueueEntry rows that record which
# PeriLab job_id a submission became; there is no cluster/sftp path.
from ..db.models import JOB_CANCELLED, JOB_DONE, JOB_FAILED, JOB_QUEUED, JOB_RUNNING, JobQueueEntry
from ..support import audit_log
from ..support.api_key_auth import get_user_name_with_api_key
from ..support.base_models import Jobs, ModelData, RunStatus, Status
from ..support.db_auth import ResolvedIdentity, resolve_user
from ..support.file_handler import FileHandler
from ..support.globals import dev, log, max_concurrent_local_jobs
from ..support.job_concurrency import count_active_local_jobs
from ..support.job_queue import cancel_running, enforce_user_quota, submit_job
from ..support.perilab_api_client import PeriLabJob
from ..support.solver_backend import get_solver_backend

router = APIRouter(prefix="/jobs", tags=["Jobs Methods"])


def _perilab_job_ids(entry: JobQueueEntry) -> List[str]:
    return [jid.strip() for jid in (entry.perilab_job_id or "").split(",") if jid.strip()]


def _sync_status(db: Session, entry: Optional[JobQueueEntry]) -> Optional[PeriLabJob]:
    """Moves an active entry to done/failed/cancelled once the PeriLab API
    reports its job(s) finished - nothing else ever does, so without this a
    run would stay "running" forever. Returns the first PeriLab job (for
    progress), or None if the entry isn't active or the API is unreachable."""
    if entry is None or entry.status not in (JOB_QUEUED, JOB_RUNNING):
        return None
    job_ids = _perilab_job_ids(entry)
    if not job_ids:
        return None

    client = get_solver_backend().client()
    try:
        jobs = [client.get_job(job_id) for job_id in job_ids]
    except HTTPException:
        return None

    # A batch submission is only finished once every one of its jobs is.
    if not any(job.is_active for job in jobs):
        failed = [job for job in jobs if job.is_failed]
        if not failed:
            entry.status = JOB_DONE
        elif all(job.status.lower() == "cancelled" for job in failed):
            entry.status = JOB_CANCELLED
        else:
            entry.status = JOB_FAILED
            error = failed[0].raw.get("error")
            entry.error = str(error)[:1000] if error else f"PeriLab job {failed[0].job_id} {failed[0].status}"
        entry.finished_at = datetime.now(timezone.utc)
        db.commit()
    return jobs[0]


def _run_status_dict(
    entry: Optional[JobQueueEntry], job: Optional[PeriLabJob] = None, check_files: bool = True
) -> dict:
    """Progress and result-file presence for one specific JobQueueEntry,
    sourced entirely from the PeriLab API (support/perilab_api_client.py) -
    no filesystem/cluster access. `job` is the entry's already-fetched
    PeriLab job (see _sync_status), used for progress. With
    check_files=False the result-file lookup (one API call per job) is
    skipped and `results` just means the run finished successfully.
    Returns all-false/None if `entry` is None or has no perilab_job_id yet
    (not submitted, or submission failed before the API accepted it)."""
    empty = {
        "results": False,
        "csvResults": False,
        "progress": None,
        "currentStep": None,
        "totalSteps": None,
    }
    if entry is None or not entry.perilab_job_id:
        return empty

    result = dict(empty)
    job_ids = _perilab_job_ids(entry)
    if not job_ids:
        return result

    # A comma-separated perilab_job_id (batch submission, see
    # PeriLabSolverBackend.submit) reports progress for its first job
    # only - good enough for a single progress bar.
    if entry.status == JOB_RUNNING and job is not None:
        result["progress"] = job.progress
        result["currentStep"] = job.current_step
        result["totalSteps"] = job.total_steps

    if not check_files:
        result["results"] = entry.status == JOB_DONE
        return result

    client = get_solver_backend().client()
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


def _to_run_status(entry: JobQueueEntry, job: Optional[PeriLabJob] = None, check_files: bool = True) -> RunStatus:
    run = _run_status_dict(entry, job, check_files)
    return RunStatus(
        id=entry.id,
        model_name=entry.model_name,
        model_folder_name=entry.model_folder_name,
        status=entry.status,
        perilab_job_id=entry.perilab_job_id,
        submitted_at=entry.submitted_at,
        started_at=entry.started_at,
        finished_at=entry.finished_at,
        error=entry.error,
        results=run["results"],
        csvResults=run["csvResults"],
        progress=run["progress"],
        currentStep=run["currentStep"],
        totalSteps=run["totalSteps"],
    )


def _can_view_entry(identity: ResolvedIdentity, entry: JobQueueEntry) -> bool:
    """Owner, or an org admin over the same org - the same owner-or-org-
    admin pattern support.rbac.can_edit uses elsewhere for shared
    resources."""
    if entry.user_id == identity.user.id:
        return True
    return identity.user.role == "admin" and identity.user.org_id == entry.org_id


def _latest_entry(db: Session, user_id: str, model_name: str, model_folder_name: str) -> Optional[JobQueueEntry]:
    """The most recently submitted run for this folder, or None if it's
    never been submitted. A folder can have many runs over time (see
    module docstring) - this is only ever used for the folder-level
    "quick glance" summary and the already-submitted duplicate guard, not
    as a stand-in for "the" job."""
    return db.scalar(
        select(JobQueueEntry)
        .where(
            JobQueueEntry.user_id == user_id,
            JobQueueEntry.model_name == model_name,
            JobQueueEntry.model_folder_name == model_folder_name,
        )
        .order_by(JobQueueEntry.submitted_at.desc())
    )


def _folder_summary(db: Session, request: Request, model_name: str, model_folder_name: str) -> dict:
    """Latest-run snapshot for a model folder, plus run_id/run_count so
    callers can go fetch full detail/history instead of assuming this
    snapshot is the only run that ever existed. Returns all-false/None
    (run_count 0) if there's no logged-in DB user or no run has ever been
    submitted for this folder."""
    empty = {
        "submitted": False,
        "results": False,
        "csvResults": False,
        "progress": None,
        "currentStep": None,
        "totalSteps": None,
        "run_id": None,
        "run_count": 0,
    }

    identity = resolve_user(request, dev, db)
    if identity.user is None:
        return empty

    run_count = (
        db.scalar(
            select(func.count())
            .select_from(JobQueueEntry)
            .where(
                JobQueueEntry.user_id == identity.user.id,
                JobQueueEntry.model_name == model_name,
                JobQueueEntry.model_folder_name == model_folder_name,
            )
        )
        or 0
    )
    if run_count == 0:
        return empty

    entry = _latest_entry(db, identity.user.id, model_name, model_folder_name)
    job = _sync_status(db, entry)
    result = dict(empty)
    result["run_count"] = run_count
    result["run_id"] = entry.id
    result["submitted"] = entry.status in (JOB_QUEUED, JOB_RUNNING)
    result.update(_run_status_dict(entry, job))
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
    active = count_active_local_jobs(db)
    if active >= max_concurrent_local_jobs:
        log.warning("Rejecting %s: %d/%d jobs already active", model_name, active, max_concurrent_local_jobs)
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

    audit_log.record(username, "run_model", model_name, request)

    # Only one *active* run per folder at a time - not one run ever, just
    # one currently queued/running. Older, finished runs for this same
    # folder stay in its history (see GET .../runs) rather than being
    # overwritten or blocking a fresh submission.
    existing = _latest_entry(db, db_user.id, model_name, model_folder_name)
    if existing is not None and existing.status in (JOB_QUEUED, JOB_RUNNING):
        log.warning("%s already submitted", model_name)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=model_name + " already submitted")

    args = "-v" if verbose else ""

    # Fail fast while the PeriLab API is down, before submit_job records a
    # FAILED run for what is only an outage.
    if not get_solver_backend().client().health():
        audit_log.record(username, "run_model", model_name, request, result="rejected_perilab_offline")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The PeriLab API is not online. Please try again later.",
        )

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
            solver_args=args,
            num_procs=model_data.job.tasks,
            job_ids=job_ids,
        )
    except Exception:
        audit_log.record(username, "run_model", model_name, request, result="rejected_submit_failed")
        raise

    log.info("%s has been submitted (run_id=%s)", model_name, entry.id)
    return {
        "status": "running",
        "run_id": entry.id,
        "perilab_job_id": entry.perilab_job_id,
    }


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
    """Folder-level overview: one row per model_folder_name variant that
    exists on disk, each carrying only its *latest* run's status plus
    run_id/run_count. For full run history or a specific past run, use
    GET .../runs or GET /jobs/{run_id}."""
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

                # Latest-run snapshot - DB + PeriLab API only.
                summary = _folder_summary(db, request, model_name, model_folder_name)
                job.submitted = summary["submitted"]
                job.results = summary["results"]
                job.progress = summary["progress"]
                job.currentStep = summary["currentStep"]
                job.totalSteps = summary["totalSteps"]
                job.run_id = summary["run_id"]
                job.run_count = summary["run_count"]
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
    """Folder-level summary: model-config existence plus the *latest*
    run's status for this model_name/model_folder_name. Carries run_id so
    callers can switch to GET /jobs/{run_id} for authoritative detail on
    that specific run, or GET .../runs for the full history, rather than
    assuming this is "the" run."""
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
    summary = _folder_summary(db, request, model_name, model_folder_name)
    job_status.submitted = summary["submitted"]
    job_status.results = summary["results"]
    job_status.csvResults = summary["csvResults"]
    job_status.progress = summary["progress"]
    job_status.currentStep = summary["currentStep"]
    job_status.totalSteps = summary["totalSteps"]
    job_status.run_id = summary["run_id"]

    return job_status


def _saved_model(username: str, model_name: str, model_folder_name: str) -> Optional[dict]:
    """The input deck (ModelData JSON) last written into a model folder, if any."""
    filepath = os.path.join(
        FileHandler.get_local_model_folder_path(username, model_name, model_folder_name), model_name + ".json"
    )
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


# Declared before GET /{run_id} so "runs" isn't captured as a run id.
@router.get("/runs", operation_id="list_all_runs", response_model=List[RunStatus])
def list_all_runs(request: Request, db: Session = Depends(get_db)):
    """Every run the logged-in user has submitted, across all models,
    ordered by model_name, model_folder_name and newest first. Each carries
    its model folder's saved input deck (`model`) so the frontend can load
    it back into the editor. Result files aren't looked up per run here -
    `results` just means the run finished successfully."""
    identity = resolve_user(request, dev, db)
    if identity.user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required.")
    username = FileHandler.get_user_name(request, dev)

    # Materialized up front: _sync_status commits mid-loop.
    entries = list(
        db.scalars(
            select(JobQueueEntry)
            .where(JobQueueEntry.user_id == identity.user.id)
            .order_by(
                JobQueueEntry.model_name,
                JobQueueEntry.model_folder_name,
                JobQueueEntry.submitted_at.desc(),
            )
        )
    )

    models = {}
    runs = []
    for entry in entries:
        run = _to_run_status(entry, _sync_status(db, entry), check_files=False)
        key = (entry.model_name, entry.model_folder_name)
        if key not in models:
            models[key] = _saved_model(username, *key)
        run.model = models[key]
        runs.append(run)
    return runs


@router.get("/{model_name}/{model_folder_name}/runs", operation_id="list_runs", response_model=List[RunStatus])
def list_runs(
    model_name: str,
    model_folder_name: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Full run history for a model folder - every JobQueueEntry ever
    submitted for it, newest first. Use this (or GET /jobs/{run_id} for
    one specific run) instead of assuming getJobs/getStatus's latest-run
    snapshot is the only run that ever existed."""
    identity = resolve_user(request, dev, db)
    if identity.user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required.")

    entries = list(
        db.scalars(
            select(JobQueueEntry)
            .where(
                JobQueueEntry.user_id == identity.user.id,
                JobQueueEntry.model_name == model_name,
                JobQueueEntry.model_folder_name == model_folder_name,
            )
            .order_by(JobQueueEntry.submitted_at.desc())
        )
    )
    return [_to_run_status(entry, _sync_status(db, entry)) for entry in entries]


@router.get("/{run_id}", operation_id="get_run", response_model=RunStatus)
def get_run(run_id: str, request: Request, db: Session = Depends(get_db)):
    """Authoritative detail for one specific run, keyed by its own id -
    independent of whether its model folder has since been resubmitted."""
    identity = resolve_user(request, dev, db)
    if identity.user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required.")

    entry = db.get(JobQueueEntry, run_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found.")
    if not _can_view_entry(identity, entry):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your run.")

    return _to_run_status(entry, _sync_status(db, entry))


@router.get("/{run_id}/log", operation_id="get_run_log")
def get_run_log(
    run_id: str,
    request: Request,
    tail: Optional[int] = None,
    debug: bool = False,
    db: Session = Depends(get_db),
) -> str:
    """Fetch the log for a specific run from the PeriLab API.

    This replaces the old WebSocket-based log streaming. The frontend
    should poll this endpoint to get log updates.
    """
    identity = resolve_user(request, dev, db)
    if identity.user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required.")

    entry = db.get(JobQueueEntry, run_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found.")
    if not _can_view_entry(identity, entry):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your run.")

    if not entry.perilab_job_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No PeriLab job ID associated with this run yet. The job may still be queued.",
        )

    # Use the first job_id if there are multiple (batch submission)
    first_job_id = entry.perilab_job_id.split(",")[0].strip()

    content = get_solver_backend().client().get_log(first_job_id, tail=tail)

    if not debug:
        content = "\n".join(line for line in content.splitlines() if "[Debug]" not in line)

    return content


def _without_debug_lines(chunks: Iterator[str]) -> Iterator[str]:
    """Drops "[Debug]" lines from a chunked log. Chunks don't align with
    lines, so the trailing partial line is held back until it's complete."""
    pending = ""
    for chunk in chunks:
        pending += chunk
        *lines, pending = pending.split("\n")
        kept = [line + "\n" for line in lines if "[Debug]" not in line]
        if kept:
            yield "".join(kept)
    if pending and "[Debug]" not in pending:
        yield pending


@router.get(
    "/{run_id}/log/stream",
    operation_id="stream_run_log",
    response_class=StreamingResponse,
    responses={200: {"content": {"text/plain": {}}}},
)
def stream_run_log(
    run_id: str,
    request: Request,
    debug: bool = False,
    db: Session = Depends(get_db),
):
    """Streams a run's log from the PeriLab API (GET /jobs/{job_id}/log/stream)
    as plain text: everything logged so far, then new output as PeriLab
    writes it. The response ends when the job finishes. 404 while the run
    has no PeriLab job/log yet - the frontend retries."""
    identity = resolve_user(request, dev, db)
    if identity.user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required.")

    entry = db.get(JobQueueEntry, run_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found.")
    if not _can_view_entry(identity, entry):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your run.")

    job_ids = _perilab_job_ids(entry)
    if not job_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No PeriLab job ID associated with this run yet. The job may still be queued.",
        )

    # First job only for a batch submission, same as GET /{run_id}/log.
    try:
        chunks = get_solver_backend().client().stream_log(job_ids[0])
    except HTTPException as e:
        # 503 = PeriLab API offline; keep it distinct from "no log yet" so the
        # frontend doesn't wait for a start that can't happen.
        if e.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            raise
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.detail)) from e

    if not debug:
        chunks = _without_debug_lines(chunks)
    # no-transform/X-Accel-Buffering keep proxies (vite, nginx) from
    # buffering the stream until it ends.
    return StreamingResponse(
        chunks,
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no"},
    )


@router.delete("/{run_id}", operation_id="delete_run")
def delete_run(run_id: str, request: Request, db: Session = Depends(get_db)):
    """Deletes a finished run: its PeriLab job(s) - log and result files -
    and its DB entry. Active runs have to be cancelled first. The model
    folder (input deck) is left alone; it may be shared with other runs."""
    username = FileHandler.get_user_name(request, dev)
    username = get_user_name_with_api_key(request, dev, username)

    identity = resolve_user(request, dev, db)
    if identity.user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required.")

    entry = db.get(JobQueueEntry, run_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found.")
    if not _can_view_entry(identity, entry):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your run.")
    _sync_status(db, entry)
    if entry.status in (JOB_QUEUED, JOB_RUNNING):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Run is '{entry.status}' - cancel it before deleting.",
        )

    client = get_solver_backend().client()
    for job_id in _perilab_job_ids(entry):
        try:
            client.delete_job(job_id)
        except HTTPException as e:
            # Already gone on the PeriLab side (or the API is down) - don't
            # leave an undeletable entry behind because of it.
            log.warning("Could not delete PeriLab job %s of run %s: %s", job_id, run_id, e.detail)

    audit_log.record(username, "delete_run", entry.model_name, request)
    db.delete(entry)
    db.commit()
    log.info("Run %s has been deleted", run_id)
    return {"deleted": run_id}


@router.put("/{run_id}/cancel", operation_id="cancel_run")
def cancel_run(run_id: str, request: Request, db: Session = Depends(get_db)):
    """Cancels one specific run by its own id. Replaces the old
    model_name/model_folder_name-keyed PUT /jobs/cancel, which could only
    ever mean "the currently active run for this folder" - now that a
    folder can have run history, cancelling has to name which run."""
    username = FileHandler.get_user_name(request, dev)
    username = get_user_name_with_api_key(request, dev, username)

    identity = resolve_user(request, dev, db)
    if identity.user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required.")

    entry = db.get(JobQueueEntry, run_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found.")
    if not _can_view_entry(identity, entry):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your run.")
    if entry.status not in (JOB_QUEUED, JOB_RUNNING):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Run is '{entry.status}', not active - nothing to cancel.",
        )

    audit_log.record(username, "cancel_run", entry.model_name, request)

    cancel_running(db, entry)
    log.info("Run %s has been canceled", run_id)
    return {"cancelled": run_id}
