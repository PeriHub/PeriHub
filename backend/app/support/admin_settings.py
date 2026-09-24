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

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.models import AdminSetting


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
