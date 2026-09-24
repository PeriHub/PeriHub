# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Job submission bookkeeping for locally-submitted (non-cluster) jobs.

There is no queue any more: routers/jobs.py checks capacity
(support/job_concurrency.has_capacity) and the per-user cap
(enforce_user_quota) up front and rejects with a 429 if either is exceeded,
then calls submit_job() below to submit straight to the PeriLab API
(support/perilab_api_client.py, see project root openapi.json) and record
the result. A JobQueueEntry row still exists per submission (status
RUNNING/FAILED and the returned perilab_job_id), so status/log/cancel
calls know which PeriLab job to talk to - this still requires
DATABASE_URL to be configured, since there is no pid.txt-style filesystem
fallback for local (non-cluster) jobs.

Cluster/sbatch submissions are handled entirely separately - Slurm queues
those on the cluster side.
"""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db.models import (
    JOB_CANCELLED,
    JOB_FAILED,
    JOB_QUEUED,
    JOB_RUNNING,
    JobQueueEntry,
    User,
)
from .globals import log, max_concurrent_jobs_per_user
from .solver_backend import get_solver_backend

_ACTIVE_STATUSES = (JOB_QUEUED, JOB_RUNNING)


def count_active_for_user(db: Session, user_id: str) -> int:
    return (
        db.scalar(
            select(func.count())
            .select_from(JobQueueEntry)
            .where(
                JobQueueEntry.user_id == user_id,
                JobQueueEntry.status.in_(_ACTIVE_STATUSES),
            )
        )
        or 0
    )


def enforce_user_quota(db: Session, user: User) -> None:
    """Raises ValueError if `user` is already at max_concurrent_jobs_per_user
    active (running) jobs. Callers (routers/jobs.py) turn this into a 429."""
    if max_concurrent_jobs_per_user <= 0:
        return  # 0 or negative disables the per-user cap
    current = count_active_for_user(db, user.id)
    if current >= max_concurrent_jobs_per_user:
        raise ValueError(
            f"You already have {current}/{max_concurrent_jobs_per_user} jobs running. "
            "Wait for one to finish, or cancel one, before submitting another."
        )


def _owner_username(user: User) -> str:
    """Solver backend submit() takes a username (folder identity), not a
    DB user id - resolve it here so job_queue stays the only place that
    needs to know both representations."""
    return user.email or user.id


def submit_job(
    db: Session,
    user: User,
    model_name: str,
    model_folder_name: str,
    remotepath: str,
    project_id: str | None = None,
    node_count: int | None = None,
    solver_args: str = "",
    num_procs: int = 1,
    job_ids: str = "-1",
) -> JobQueueEntry:
    """Submits a job to the PeriLab API immediately and records it.

    Callers are expected to have already checked has_capacity()/
    enforce_user_quota() and rejected with a 429 rather than calling this
    when the instance is full - there's no queue to fall back to any more.
    Raises (and marks the entry FAILED) if the PeriLab API submission
    itself fails; HTTPException from the API client propagates as-is
    (support/perilab_api_client.py already maps transport/HTTP errors to
    502), anything else is left for the caller to handle.
    """
    entry = JobQueueEntry(
        user_id=user.id,
        org_id=user.org_id,
        project_id=project_id,
        model_name=model_name,
        model_folder_name=model_folder_name,
        remotepath=remotepath,
        status=JOB_QUEUED,  # transient: updated to RUNNING/FAILED below, in this same call
        node_count=node_count,
        solver_args=solver_args,
        num_procs=num_procs,
        job_ids=job_ids,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    try:
        perilab_job_id = get_solver_backend().submit(
            _owner_username(user),
            model_name,
            model_folder_name,
            remotepath,
            args=solver_args,
            num_procs=num_procs,
            job_ids=job_ids,
        )
    except Exception as exc:  # noqa: BLE001 - record the failure, then let it propagate
        log.error("job_queue: submit failed for %s/%s: %s", model_name, model_folder_name, exc)
        entry.status = JOB_FAILED
        entry.error = str(exc)
        entry.finished_at = datetime.now(timezone.utc)
        db.commit()
        raise

    entry.status = JOB_RUNNING
    entry.started_at = datetime.now(timezone.utc)
    entry.perilab_job_id = perilab_job_id
    db.commit()
    log.info(
        "job_queue: submitted %s/%s for user %s (perilab_job_id=%s)",
        model_name,
        model_folder_name,
        user.id,
        perilab_job_id,
    )
    return entry


def cancel_running(db: Session, entry: JobQueueEntry) -> None:
    """Cancels a running entry against the PeriLab API and marks it
    cancelled. Raises whatever the API client raises (HTTPException) if
    the PeriLab API can't be reached - callers should let that propagate as
    a 502 rather than silently marking the job cancelled when it might
    still be running."""
    if entry.perilab_job_id:
        get_solver_backend().cancel(entry.perilab_job_id)
    entry.status = JOB_CANCELLED
    entry.finished_at = datetime.now(timezone.utc)
    db.commit()
