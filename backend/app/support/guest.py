# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Guest access (Phase 1): what anonymous visitors may do, and how much.

Guests are real User rows with role "guest" (routers/auth.py create_guest), so they authenticate like everyone
else and all restrictions are per role, not per deployment: an admin logging in on a public guest-access instance
still has every feature. Guests can run bounded jobs of built-in models; everything that writes arbitrary files or
runs extra server-side work (uploads, input-deck edits, analyses, deviations, sharing) is refused here. The limits
are admin settings (support/admin_settings.py); the job time limit and retention are enforced by
support/guest_sweeper.py.
"""

from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from ..db import base
from ..db.models import User
from .admin_settings import instance_setting
from .base_models import ModelData
from .db_auth import resolve_user

GUEST_DENIED = "Not available for guests — log in for full access."
LIMIT_KEYS = ("max_nodes", "max_output_steps", "max_job_minutes", "max_concurrent_jobs", "retention_days")


def current_user(request: Request) -> User | None:
    """The bearer-token user of this request (own short session), or None without a DB or login."""
    if base.SessionLocal is None:
        return None
    with base.SessionLocal() as db:
        return resolve_user(request, db).user


def reject_guest(user: User) -> None:
    if user.role == "guest":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=GUEST_DENIED)


def require_non_guest(request: Request) -> User:
    """FastAPI dependency: 401 without a login, 403 for guests."""
    user = current_user(request)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required.")
    reject_guest(user)
    return user


def guest_limits(db: Session) -> dict:
    return {key: instance_setting(db, f"guest_{key}") for key in LIMIT_KEYS}


def apply_guest_limits(data: ModelData, limits: dict) -> None:
    """Bounds the result size before the input deck is written: at most `max_output_steps` outputs per output
    definition, never frequency-based (which could produce one output per step)."""
    cap = limits["max_output_steps"]
    for output in data.outputs:
        output.useOutputFrequency = False
        output.numberOfOutputSteps = min(output.numberOfOutputSteps or cap, cap)
