# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Usage summary, aggregated from the JobQueueEntry rows every submission already writes
(support/job_queue.py) - no separate usage log to keep in sync."""

from fastapi import APIRouter, Request
from sqlalchemy import func, select

from ..db import base
from ..db.models import JOB_CANCELLED, JobQueueEntry, User
from ..support.base_models import UsageSummary
from ..support.db_auth import resolve_user
from ..support.globals import dev

router = APIRouter(prefix="/usage", tags=["Usage Methods"])


def _summarize(user_id: str | None = None) -> UsageSummary:
    summary = UsageSummary()
    if base.SessionLocal is None:
        return summary  # DB-less trial mode: nothing can have been submitted
    with base.SessionLocal() as db:
        owner = func.coalesce(User.email, User.id)
        stmt = select(owner, JobQueueEntry.model_name, JobQueueEntry.status, func.count()).join(User)
        if user_id is not None:
            stmt = stmt.where(JobQueueEntry.user_id == user_id)
        stmt = stmt.group_by(owner, JobQueueEntry.model_name, JobQueueEntry.status)
        for username, model_name, status, count in db.execute(stmt):
            summary.total_jobs_submitted += count
            if status == JOB_CANCELLED:
                summary.total_jobs_cancelled += count
            summary.jobs_per_user[username] = summary.jobs_per_user.get(username, 0) + count
            summary.jobs_per_model[model_name] = summary.jobs_per_model.get(model_name, 0) + count
    return summary


@router.get("/me", operation_id="get_my_usage")
def get_my_usage(request: Request) -> UsageSummary:
    """Usage summary (jobs submitted/cancelled, per model) scoped to the calling user."""
    if base.SessionLocal is None:
        return UsageSummary()
    with base.SessionLocal() as db:
        user = resolve_user(request, dev, db).user
    return _summarize(user.id) if user is not None else UsageSummary()


@router.get("/all", operation_id="get_all_usage")
def get_all_usage() -> UsageSummary:
    """Instance-wide usage summary.

    NOTE: unauthenticated/unrestricted for now, matching the rest of this
    router set. Before exposing this beyond a trusted operator, it should be
    gated the same way the admin/audit-log endpoints eventually are (see the
    security and licensing roadmap items) so one user can't see another
    tenant's aggregate usage.
    """
    return _summarize()
