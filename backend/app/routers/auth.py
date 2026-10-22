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
import threading
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..db.models import Organization, User
from ..support import audit_log
from ..support.account import delete_account
from ..support.admin_settings import enforce_signup_open, instance_setting
from ..support.db_auth import resolve_user
from ..support.globals import deployment_mode, public_url
from ..support.local_auth import (
    create_password_reset_token,
    create_session_token,
    decode_password_reset_token,
    hash_password,
    password_matches_fingerprint,
    verify_password,
)
from ..support.mailer import mail_enabled, send_mail
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
    notify_job_emails: bool


class AccountSettingsUpdate(BaseModel):
    notify_job_emails: bool


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class DeleteAccountRequest(BaseModel):
    # Email & password accounts confirm with their password, OAuth accounts (no password) with their email.
    password: str | None = None
    email: str | None = None


def _check_new_password(password: str) -> None:
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters.",
        )


def _require_account(request: Request, db: Session) -> User:
    user = resolve_user(request, db).user
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not logged in.")
    if user.role == "guest":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Guest accounts can't do this.")
    return user


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

    _check_new_password(payload.password)

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
        notify_job_emails=user.notify_job_emails,
    )


@router.patch("/me", operation_id="update_account_settings", response_model=MeResponse)
def update_account_settings(payload: AccountSettingsUpdate, request: Request, db: Session = Depends(get_db)):
    """Change the logged-in account's settings: `notify_job_emails` = email when one of your runs finishes, fails
    or is stopped by someone else (not when you cancel it yourself). 403 for guests."""
    user = _require_account(request, db)
    user.notify_job_emails = payload.notify_job_emails
    db.commit()
    return me(request, db)


@router.post("/password", operation_id="change_password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(payload: ChangePasswordRequest, request: Request, db: Session = Depends(get_db)) -> None:
    """Change the logged-in email & password account's password. 401 if `current_password` is wrong, 400 for
    accounts without a PeriHub password (OAuth), 422 for new passwords under 8 characters. Other sessions stay
    logged in."""
    user = _require_account(request, db)
    if user.auth_provider != "local" or not user.password_hash:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This account has no PeriHub password.")
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is wrong.")
    _check_new_password(payload.new_password)
    user.password_hash = hash_password(payload.new_password)
    db.commit()
    audit_log.record(user.id, "change_password", user.id, request)


# ponytail: in-process, per worker and lost on restart; a shared store if PeriHub runs many workers.
_RESET_COOLDOWN_SECONDS = 300
_last_reset_mail: dict[str, float] = {}
_reset_lock = threading.Lock()


def _reset_mail_allowed(email: str) -> bool:
    now = time.monotonic()
    with _reset_lock:
        if now - _last_reset_mail.get(email, -_RESET_COOLDOWN_SECONDS) < _RESET_COOLDOWN_SECONDS:
            return False
        _last_reset_mail[email] = now
        return True


@router.post("/password/forgot", operation_id="forgot_password", status_code=status.HTTP_202_ACCEPTED)
def forgot_password(payload: ForgotPasswordRequest, request: Request, db: Session = Depends(get_db)) -> None:
    """Email a one-hour, single-use password reset link to an email & password account. Always 202, whether or not
    the address has an account (no account enumeration); at most one mail per address every 5 minutes. 404 when
    mail isn't configured (SMTP_HOST/SMTP_FROM/PUBLIC_URL)."""
    if not mail_enabled():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Password reset by email is not available.")
    email = payload.email.lower()
    user = db.scalar(select(User).where(User.email == payload.email, User.auth_provider == "local"))
    if user is None or not user.password_hash or not user.is_active or not _reset_mail_allowed(email):
        return
    token = create_password_reset_token(user.id, user.password_hash)
    send_mail(
        user.email,
        "Reset your PeriHub password",
        f"Hello {user.display_name},\n\n"
        f"someone asked to reset the password of your PeriHub account. To choose a new one, open this link "
        f"within the next hour:\n\n{public_url}/auth/reset?token={token}\n\n"
        f"If you didn't ask for this, ignore this email - your password stays as it is.\n",
    )
    audit_log.record(user.id, "forgot_password", user.id, request)


@router.post("/password/reset", operation_id="reset_password", status_code=status.HTTP_204_NO_CONTENT)
def reset_password(payload: ResetPasswordRequest, request: Request, db: Session = Depends(get_db)) -> None:
    """Set a new password with the token from a reset email. 400 if the link is invalid, expired or already used
    (any password change invalidates it), 422 for new passwords under 8 characters."""
    decoded = decode_password_reset_token(payload.token)
    user = db.get(User, decoded[0]) if decoded else None
    if (
        user is None
        or not user.is_active
        or user.auth_provider != "local"
        or not password_matches_fingerprint(user.password_hash, decoded[1])
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="This reset link is invalid or has expired."
        )
    _check_new_password(payload.new_password)
    user.password_hash = hash_password(payload.new_password)
    db.commit()
    audit_log.record(user.id, "reset_password", user.id, request)


@router.post("/me/delete", operation_id="delete_account", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_account(payload: DeleteAccountRequest, request: Request, db: Session = Depends(get_db)) -> None:
    """Permanently delete the logged-in account and everything it owns: jobs (stopped, with their PeriLab results),
    simulation files, model configs and materials (shared ones too), projects it created, team memberships and API
    keys. Confirm with `password` (email & password accounts) or `email` (OAuth accounts): 401 if it doesn't match.
    409 for the organization's last admin."""
    user = _require_account(request, db)
    if user.password_hash:
        confirmed = payload.password is not None and verify_password(payload.password, user.password_hash)
    else:
        confirmed = bool(payload.email and user.email) and payload.email.strip().lower() == user.email.lower()
    if not confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Confirmation doesn't match.")
    if user.role == "admin":
        other_admin = db.scalar(
            select(User.id)
            .where(User.org_id == user.org_id, User.role == "admin", User.is_active.is_(True), User.id != user.id)
            .limit(1)
        )
        if other_admin is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You're the last admin. Make someone else an admin before deleting your account.",
            )
    user_id = user.id
    delete_account(db, user)
    audit_log.record(user_id, "delete_account", user_id, request)
