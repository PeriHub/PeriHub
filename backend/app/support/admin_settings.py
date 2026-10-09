# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Runtime-editable admin settings, backed by the admin_settings table.

Phase 0 goal: move things like EXTERNAL_PERILAB_URL out of "env var set at
deploy time" and into "admin can change it from a settings screen without a
restart", while not breaking any existing deployment that only has the env
var set and no DB row yet.

Resolution order for `get_setting`: org-scoped DB row -> instance-wide DB
row (org_id IS NULL) -> `env_fallback` argument -> `default`. Callers that
already have a globals.py env var (external_perilab_url, cluster_url, ...)
should pass it as `env_fallback` so nothing breaks for community users who
never touch the new admin settings UI.
"""

from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.models import AdminSetting, User
from .globals import external_perilab_url, guest_access, max_concurrent_jobs_per_user, max_concurrent_local_jobs


def get_setting(
    db: Session,
    key: str,
    org_id: str | None = None,
    env_fallback: str = "",
    default: Any = None,
) -> Any:
    if org_id is not None:
        row = db.scalar(select(AdminSetting).where(AdminSetting.key == key, AdminSetting.org_id == org_id))
        if row is not None:
            return row.value

    row = db.scalar(select(AdminSetting).where(AdminSetting.key == key, AdminSetting.org_id.is_(None)))
    if row is not None:
        return row.value

    if env_fallback:
        return env_fallback

    return default


def set_setting(db: Session, key: str, value: Any, org_id: str | None = None) -> AdminSetting:
    row = db.scalar(select(AdminSetting).where(AdminSetting.key == key, AdminSetting.org_id == org_id))
    if row is None:
        row = AdminSetting(key=key, org_id=org_id, value=value)
        db.add(row)
    else:
        row.value = value
    db.commit()
    db.refresh(row)
    return row


# Instance-wide settings editable on the admin page (routers/admin.py). The
# env vars in globals.py stay the defaults until an admin saves a value.
INSTANCE_DEFAULTS = {
    "max_concurrent_local_jobs": max_concurrent_local_jobs,
    "max_concurrent_jobs_per_user": max_concurrent_jobs_per_user,
    "signup_open": True,
    "default_role": "member",
    "external_perilab_url": external_perilab_url,
    "guest_access": guest_access,
    "guest_max_nodes": 10000,
    "guest_max_output_steps": 50,
    "guest_max_job_minutes": 10,
    "guest_max_concurrent_jobs": 1,
    "guest_retention_days": 1,
}


def instance_setting(db: Session, key: str) -> Any:
    return get_setting(db, key, default=INSTANCE_DEFAULTS[key])


def overridden_instance_settings(db: Session) -> list[str]:
    return list(db.scalars(select(AdminSetting.key).where(AdminSetting.org_id.is_(None))))


def signup_allowed(db: Session) -> bool:
    """New accounts may be created: signup is open, or there is no account yet (the very first account is always
    allowed so a fresh install can't lock itself out)."""
    return bool(instance_setting(db, "signup_open")) or (
        db.scalar(select(User.id).where(User.role != "guest").limit(1)) is None
    )


def enforce_signup_open(db: Session) -> None:
    """403 for new accounts while signup is closed (see signup_allowed)."""
    if not signup_allowed(db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Signup is closed.")
