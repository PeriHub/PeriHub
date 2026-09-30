# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Background housekeeping for guest accounts (Phase 1).

The PeriLab API has no run-time limit, and guests close their tab without cancelling, so PeriHub itself stops
guest jobs that exceed `guest_max_job_minutes`. Guest accounts are throwaway: after `guest_retention_days` the
user row, its job entries (dropping out of usage statistics - accepted), their PeriLab jobs and its simulation
folder are deleted.
Started from main.py's lifespan when a DB is configured; every step logs and swallows its own errors so a PeriLab
outage never stops the loop.
"""

import asyncio
import shutil
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from ..db import base
from ..db.models import JOB_QUEUED, JOB_RUNNING, JobQueueEntry, User
from .admin_settings import instance_setting
from .file_handler import FileHandler
from .globals import log
from .job_queue import cancel_running, perilab_job_ids, sync_status
from .solver_backend import get_solver_backend

INTERVAL_SECONDS = 60
RETENTION_EVERY = timedelta(hours=1)
_ACTIVE = (JOB_QUEUED, JOB_RUNNING)


def stop_overdue_guest_jobs(db: Session, now: datetime) -> int:
    minutes = instance_setting(db, "guest_max_job_minutes")
    started = func.coalesce(JobQueueEntry.started_at, JobQueueEntry.submitted_at)
    overdue = db.scalars(
        select(JobQueueEntry)
        .join(User, JobQueueEntry.user_id == User.id)
        .where(User.role == "guest", JobQueueEntry.status.in_(_ACTIVE), started < now - timedelta(minutes=minutes))
    ).all()
    stopped = 0
    for entry in overdue:
        try:
            sync_status(db, entry)
            if entry.status not in _ACTIVE:
                # Already resolved (done/failed/cancelled/lost) by sync_status - not
                # actually stopped by the time limit, so no "Stopped" error.
                continue
            entry.error = f"Stopped: guest time limit ({minutes} min)"
            cancel_running(db, entry)
        except Exception as exc:  # noqa: BLE001 - retried on the next sweep
            log.warning("guest_sweeper: could not stop job %s: %s", entry.id, exc)
            db.rollback()
            continue
        stopped += 1
    return stopped


def delete_expired_guests(db: Session, now: datetime) -> int:
    days = instance_setting(db, "guest_retention_days")
    expired = db.scalars(select(User).where(User.role == "guest", User.created_at < now - timedelta(days=days))).all()
    deleted = 0
    for user in expired:
        try:
            client = get_solver_backend().client()
            for entry in db.scalars(select(JobQueueEntry).where(JobQueueEntry.user_id == user.id)).all():
                if entry.status in _ACTIVE:
                    sync_status(db, entry)
                    if entry.status in _ACTIVE:
                        cancel_running(db, entry)
                # Results live under simulations/<perilab_job_id>/ or on the external PeriLab server, not in the
                # guest folder - delete them with the entry (same as routers/jobs.py delete_run).
                for job_id in perilab_job_ids(entry):
                    try:
                        client.delete_job(job_id)
                    except HTTPException as e:
                        log.warning("guest_sweeper: could not delete PeriLab job %s: %s", job_id, e.detail)
            db.execute(delete(JobQueueEntry).where(JobQueueEntry.user_id == user.id))
            folder = FileHandler.get_local_user_path(user.display_name)
            db.delete(user)
            db.commit()
        except Exception as exc:  # noqa: BLE001 - retried on the next retention run
            log.warning("guest_sweeper: could not delete guest %s: %s", user.id, exc)
            db.rollback()
            continue
        shutil.rmtree(folder, ignore_errors=True)
        deleted += 1
    return deleted


def sweep(db: Session, now: datetime, retention: bool = True) -> None:
    stopped = stop_overdue_guest_jobs(db, now)
    deleted = delete_expired_guests(db, now) if retention else 0
    if stopped or deleted:
        log.info("guest_sweeper: stopped %d job(s), deleted %d guest(s)", stopped, deleted)


def _sweep_once(retention: bool) -> None:
    try:
        with base.SessionLocal() as db:
            sweep(db, datetime.now(timezone.utc), retention)
    except Exception as exc:  # noqa: BLE001 - the loop must survive anything
        log.warning("guest_sweeper: sweep failed: %s", exc)


async def run_forever() -> None:
    """Every INTERVAL_SECONDS: stop overdue guest jobs; at most every RETENTION_EVERY: delete expired guests.
    ponytail: every uvicorn worker runs its own loop (idempotent, so only duplicate queries); move to a single
    scheduler if PeriHub ever runs many workers."""
    last_retention = None
    while True:
        now = datetime.now(timezone.utc)
        retention = last_retention is None or now - last_retention >= RETENTION_EVERY
        await asyncio.to_thread(_sweep_once, retention)
        if retention:
            last_retention = now
        await asyncio.sleep(INTERVAL_SECONDS)
