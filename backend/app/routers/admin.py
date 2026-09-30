# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Admin page API (Phase 1): user management, jobs & usage, instance settings, audit log.

Every endpoint is guarded by `require_admin`, so this file is the one place to audit
for admin access. Admins only see their own org. The first user to sign up or log in
becomes admin (support/rbac.ensure_first_admin). Existing admin-capable endpoints stay
where they are and the admin page calls them directly: cancelling any org job
(`PUT /jobs/{run_id}/cancel`) and stale-data cleanup (`DELETE /admin/user-data`).
"""

import json
from collections import deque
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..db.models import JOB_QUEUED, JOB_RUNNING, JobQueueEntry, User
from ..support import audit_log
from ..support.admin_settings import (
    INSTANCE_DEFAULTS,
    instance_setting,
    overridden_instance_settings,
    set_setting,
)
from ..support.base_models import UsageSummary
from ..support.db_auth import resolve_user
from ..support.globals import audit_log_path
from ..support.rbac import require_role
from .usage import _summarize

router = APIRouter(prefix="/admin", tags=["Admin Methods"])


def require_admin(request: Request, db: Session = Depends(get_db)) -> User:
    user = resolve_user(request, db).user
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required.")
    require_role(user, "admin")
    return user


class AdminUser(BaseModel):
    id: str
    display_name: str
    email: str | None
    auth_provider: str
    role: str
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None
    job_count: int


class AdminUserUpdate(BaseModel):
    role: Literal["admin", "developer", "member", "viewer"] | None = None
    is_active: bool | None = None


class AdminJob(BaseModel):
    id: str
    owner: str
    model_name: str
    model_folder_name: str
    status: str
    submitted_at: datetime
    finished_at: datetime | None


class AdminSettings(BaseModel):
    max_concurrent_local_jobs: int = Field(ge=1)
    max_concurrent_jobs_per_user: int = Field(ge=0, description="0 disables the per-user cap")
    signup_open: bool
    default_role: Literal["member", "viewer"]
    external_perilab_url: str

    @field_validator("external_perilab_url")
    @classmethod
    def _http_url(cls, v: str) -> str:
        v = v.strip()
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("must be empty or start with http:// or https://")
        return v


class AdminSettingsResponse(AdminSettings):
    overridden: list[str] = Field(description="Keys saved in the DB; the rest use env/default values")


def _to_admin_user(user: User, job_count: int) -> AdminUser:
    return AdminUser(
        id=user.id,
        display_name=user.display_name,
        email=user.email,
        auth_provider=user.auth_provider,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
        job_count=job_count,
    )


def _job_count(db: Session, user_id: str) -> int:
    return db.scalar(select(func.count()).select_from(JobQueueEntry).where(JobQueueEntry.user_id == user_id)) or 0


@router.get("/users", operation_id="admin_list_users", response_model=list[AdminUser])
def list_users(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> list[AdminUser]:
    """All users of the admin's organization with their job count."""
    counts = dict(db.execute(select(JobQueueEntry.user_id, func.count()).group_by(JobQueueEntry.user_id)).all())
    users = db.scalars(select(User).where(User.org_id == admin.org_id).order_by(User.created_at))
    return [_to_admin_user(u, counts.get(u.id, 0)) for u in users]


@router.patch("/users/{user_id}", operation_id="admin_update_user", response_model=AdminUser)
def update_user(
    user_id: str,
    payload: AdminUserUpdate,
    request: Request,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminUser:
    """Change a user's role and/or active flag. 409 if this would leave the org without an active admin."""
    user = db.get(User, user_id)
    if user is None or user.org_id != admin.org_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    loses_admin = (
        user.role == "admin"
        and user.is_active
        and ((payload.role is not None and payload.role != "admin") or payload.is_active is False)
    )
    if loses_admin:
        other_admins = db.scalar(
            select(func.count())
            .select_from(User)
            .where(User.org_id == admin.org_id, User.role == "admin", User.is_active.is_(True), User.id != user.id)
        )
        if not other_admins:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="At least one active admin must remain.")

    changes = payload.model_dump(exclude_none=True)
    for key, value in changes.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    audit_log.record(admin.email or admin.id, "admin_update_user", user.id, request, extra=changes)
    return _to_admin_user(user, _job_count(db, user.id))


@router.get("/jobs", operation_id="admin_list_jobs", response_model=list[AdminJob])
def list_jobs(
    active_only: bool = False,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[AdminJob]:
    """The organization's runs across all users, newest first (max 500). Cancel via `cancel_run`."""
    stmt = (
        select(JobQueueEntry, User)
        .join(User, JobQueueEntry.user_id == User.id)
        .where(User.org_id == admin.org_id)
        .order_by(JobQueueEntry.submitted_at.desc())
        .limit(500)
    )
    if active_only:
        stmt = stmt.where(JobQueueEntry.status.in_((JOB_QUEUED, JOB_RUNNING)))
    return [
        AdminJob(
            id=entry.id,
            owner=owner.email or owner.display_name,
            model_name=entry.model_name,
            model_folder_name=entry.model_folder_name,
            status=entry.status,
            submitted_at=entry.submitted_at,
            finished_at=entry.finished_at,
        )
        for entry, owner in db.execute(stmt)
    ]


@router.get("/usage", operation_id="admin_get_usage", response_model=UsageSummary)
def get_usage(admin: User = Depends(require_admin)) -> UsageSummary:
    """Usage summary (jobs per user/model) for the admin's organization."""
    return _summarize(org_id=admin.org_id)


def _settings_response(db: Session) -> AdminSettingsResponse:
    values = {key: instance_setting(db, key) for key in INSTANCE_DEFAULTS}
    return AdminSettingsResponse(**values, overridden=overridden_instance_settings(db))


@router.get("/settings", operation_id="admin_get_settings", response_model=AdminSettingsResponse)
def get_settings(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> AdminSettingsResponse:
    """Instance-wide settings; values not in `overridden` come from env vars / defaults."""
    return _settings_response(db)


@router.put("/settings", operation_id="admin_update_settings", response_model=AdminSettingsResponse)
def update_settings(
    payload: AdminSettings,
    request: Request,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminSettingsResponse:
    """Save the instance-wide settings (takes effect immediately, no restart)."""
    changed = {k: v for k, v in payload.model_dump().items() if v != instance_setting(db, k)}
    for key, value in changed.items():
        set_setting(db, key, value)
    audit_log.record(admin.email or admin.id, "admin_update_settings", "instance", request, extra=changed)
    return _settings_response(db)


@router.get("/audit-log", operation_id="admin_get_audit_log", response_model=list[dict])
def get_audit_log(limit: int = Query(200, ge=1, le=1000), admin: User = Depends(require_admin)) -> list[dict]:
    """The last `limit` audit-log entries, newest first."""
    try:
        with open(audit_log_path, encoding="utf-8") as f:
            lines = deque(f, maxlen=limit)
    except FileNotFoundError:
        return []
    entries = []
    for line in reversed(lines):
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries
