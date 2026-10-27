"""Deleting an account and everything it owns (Phase 1).

One path for both callers: users deleting themselves (routers/auth.py) and the
guest sweeper removing expired guests. "Everything" is deliberate - shared
model configs/materials and projects the user created go too, even if others
use them; other people's rows are only detached (project_id cleared), never
deleted.
"""

import shutil

from fastapi import HTTPException
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from ..db.models import (
    JOB_QUEUED,
    JOB_RUNNING,
    ApiKey,
    JobQueueEntry,
    Material,
    ModelConfig,
    OAuthIdentity,
    Project,
    ProjectMembership,
    TeamMembership,
    User,
)
from .file_handler import FileHandler
from .globals import log
from .job_queue import cancel_running, perilab_job_ids, sync_status
from .solver_backend import get_solver_backend

_ACTIVE = (JOB_QUEUED, JOB_RUNNING)


def delete_account(db: Session, user: User) -> None:
    """Stops and deletes the user's jobs (PeriLab side too), deletes their rows and commits, then removes their
    simulation folder. Raises on a DB error - the caller rolls back."""
    for entry in db.scalars(select(JobQueueEntry).where(JobQueueEntry.user_id == user.id)).all():
        if entry.status in _ACTIVE:
            sync_status(db, entry)
            if entry.status in _ACTIVE:
                cancel_running(db, entry)
        # Results live under simulations/<perilab_job_id>/ or on the external PeriLab server, not in the user
        # folder - delete them with the entry (same as routers/jobs.py delete_run).
        for job_id in perilab_job_ids(entry):
            try:
                get_solver_backend().client().delete_job(job_id)
            except HTTPException as e:
                log.warning("account: could not delete PeriLab job %s: %s", job_id, e.detail)
    db.execute(delete(JobQueueEntry).where(JobQueueEntry.user_id == user.id))

    project_ids = select(Project.id).where(Project.created_by == user.id).scalar_subquery()
    # Others' rows in the user's projects stay, just without the project.
    for model in (JobQueueEntry, ModelConfig, Material):
        db.execute(update(model).where(model.project_id.in_(project_ids)).values(project_id=None))
    db.execute(delete(ProjectMembership).where(ProjectMembership.project_id.in_(project_ids)))
    db.execute(delete(ProjectMembership).where(ProjectMembership.user_id == user.id))
    db.execute(delete(Project).where(Project.created_by == user.id))
    db.execute(delete(ModelConfig).where(ModelConfig.owner_id == user.id))
    db.execute(delete(Material).where(Material.owner_id == user.id))
    db.execute(delete(TeamMembership).where(TeamMembership.user_id == user.id))
    db.execute(delete(ApiKey).where(ApiKey.user_id == user.id))
    db.execute(delete(OAuthIdentity).where(OAuthIdentity.user_id == user.id))

    folder = FileHandler.get_local_user_path(user.id)
    db.delete(user)
    db.commit()
    shutil.rmtree(folder, ignore_errors=True)
