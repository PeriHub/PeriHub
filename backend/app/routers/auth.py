# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Local email/password auth (Phase 0 - community baseline).

OAuth2/OIDC login is enterprise-only (see roadmap Phase 1)
and will live in a separate router gated by
support.entitlements.require_feature(), so they can be added without
touching this one.
"""

import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..db.models import Organization, User
from ..support.admin_settings import enforce_signup_open, instance_setting
from ..support.db_auth import resolve_user
from ..support.globals import deployment_mode
from ..support.local_auth import create_session_token, hash_password, verify_password
from ..support.rbac import ensure_first_admin
from ..support.seats import enforce_seat_limit

router = APIRouter(prefix="/auth", tags=["Auth Methods"])


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    token: str
    user_id: str
    display_name: str
    role: str


class MeResponse(BaseModel):
    user_id: str
    email: str | None
    display_name: str
    role: str
    auth_provider: str
    org_id: str | None


def _get_or_create_default_org(db: Session) -> Organization:
    """Community deployments are single-tenant: everyone lands in one
    implicit org rather than making the user pick/name one at signup.
    Enterprise deployments create orgs explicitly (Phase 1 admin flow)."""
    org = db.scalar(select(Organization))
    if org is not None:
        return org
    org = Organization(
        name="Default",
        plan=(deployment_mode if deployment_mode in ("community", "enterprise") else "community"),
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@router.post("/guest", operation_id="create_guest", response_model=AuthResponse)
def create_guest(db: Session = Depends(get_db)) -> AuthResponse:
    """Create a throwaway guest account and return its session token. Only when the admin setting `guest_access` is
    on (404 otherwise). Guests skip signup_open and the seat limit, can only run bounded jobs of built-in models
    (support/guest.py) and are deleted after `guest_retention_days` (support/guest_sweeper.py)."""
    if not instance_setting(db, "guest_access"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guest access is disabled.")
    org = _get_or_create_default_org(db)
    user = User(
        display_name=f"Guest-{secrets.token_hex(4)}",
        auth_provider="guest",
        role="guest",
        org_id=org.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_session_token(user.id)
    return AuthResponse(token=token, user_id=user.id, display_name=user.display_name, role=user.role)


@router.post("/signup", operation_id="signup", response_model=AuthResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """Create a local email/password account in the default organization (seat limit applies) and return a session
    token. 409 if the email is taken, 422 for passwords under 8 characters or a reserved 'Guest-' display name."""
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    if len(payload.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters.",
        )

    if payload.display_name.lower().startswith("guest-"):
        # Folders are keyed by display name and retention deletes simulations/Guest-*.
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Display names starting with 'Guest-' are reserved.",
        )

    enforce_signup_open(db)
    org = _get_or_create_default_org(db)
    enforce_seat_limit(db, org)
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
        auth_provider="local",
        role=instance_setting(db, "default_role"),
        org_id=org.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    ensure_first_admin(db, user)

    token = create_session_token(user.id)
    return AuthResponse(token=token, user_id=user.id, display_name=user.display_name, role=user.role)


@router.post("/login", operation_id="login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """Local email/password login; returns a session token to send as `Authorization: Bearer`. 401 on wrong
    credentials, 403 for deactivated accounts."""
    user = db.scalar(select(User).where(User.email == payload.email, User.auth_provider == "local"))
    if user is None or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    ensure_first_admin(db, user)

    token = create_session_token(user.id)
    return AuthResponse(token=token, user_id=user.id, display_name=user.display_name, role=user.role)


@router.get("/me", operation_id="get_current_user_info", response_model=MeResponse)
def me(request: Request, db: Session = Depends(get_db)) -> MeResponse:
    """The logged-in user's account (id, email, name, role, auth provider, organization); 401 if not logged in."""
    identity = resolve_user(request, db)
    if identity.user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not logged in.")
    user = identity.user
    return MeResponse(
        user_id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=user.role,
        auth_provider=user.auth_provider,
        org_id=user.org_id,
    )
