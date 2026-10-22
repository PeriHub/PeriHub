# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Background housekeeping for guest accounts (Phase 1).

The PeriLab API has no run-time limit, and guests close their tab without cancelling, so PeriHub itself stops
guest jobs that exceed `guest_max_job_minutes`. Guest accounts are throwaway: after `guest_retention_days` the
user row, its job entries (dropping out of usage statistics - accepted), their PeriLab jobs and its simulation
folder are deleted.
It also syncs active runs of users with job notification emails on, so a run that ends with no browser polling
still mails within about a minute (support/job_notifications.py).
Started from main.py's lifespan when a DB is configured; every step logs and swallows its own errors so a PeriLab
outage never stops the loop.
"""

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import base
from ..db.models import JOB_QUEUED, JOB_RUNNING, JobQueueEntry, User
from .account import delete_account
from .admin_settings import instance_setting
from .globals import log
from .job_queue import cancel_running, sync_status

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
            delete_account(db, user)
        except Exception as exc:  # noqa: BLE001 - retried on the next retention run
            log.warning("guest_sweeper: could not delete guest %s: %s", user.id, exc)
            db.rollback()
            continue
        deleted += 1
    return deleted


def sync_notified_jobs(db: Session) -> None:
    """sync_status() is what notices a run ended (and mails); without a browser polling, nothing else calls it."""
    entries = db.scalars(
        select(JobQueueEntry)
        .join(User, JobQueueEntry.user_id == User.id)
        .where(User.notify_job_emails.is_(True), JobQueueEntry.status.in_(_ACTIVE))
    ).all()
    for entry in entries:
        try:
            sync_status(db, entry)
        except Exception as exc:  # noqa: BLE001 - retried on the next sweep
            log.warning("guest_sweeper: could not sync job %s: %s", entry.id, exc)
            db.rollback()


def sweep(db: Session, now: datetime, retention: bool = True) -> None:
    sync_notified_jobs(db)
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
    """Every INTERVAL_SECONDS: sync runs of notified users, stop overdue guest jobs; at most every RETENTION_EVERY:
    delete expired guests.
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
