# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Enterprise-only login: generic OAuth2/OIDC (support/oidc_client.py).

Works against any IdP that publishes a standard OIDC discovery document -
including a self-hosted Keycloak realm, which exposes exactly that at
`{KEYCLOAK_URL}/realms/{REALM}/.well-known/openid-configuration`. There's
deliberately no Keycloak-specific code path any more: point
OAUTH_DISCOVERY_URL at your Keycloak realm (or Auth0, Azure AD, Okta, ...)
and it works the same way.

Both routes call `require_feature("oauth_login")` first, so with no
license server configured (open-core default) or a community-plan
license, these 402 - matching how support/entitlements.py already gates
other paid features. Local email/password (routers/auth.py) is unaffected
either way.
"""

from datetime import datetime, timezone

import requests
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..db.models import Organization
from ..support.entitlements import require_feature
from ..support.external_identity import get_or_create_external_user
from ..support.globals import log, oauth_email_claims, oauth_name_claims, oauth_picture_claims, oauth_trust_email
from ..support.license_client import get_status
from ..support.local_auth import create_session_token
from ..support.oidc_client import build_authorization_url, exchange_code_for_userinfo
from ..support.rbac import ensure_first_admin

router = APIRouter(prefix="/oauth", tags=["Auth Methods"])


class AuthResponse(BaseModel):
    token: str
    user_id: str
    display_name: str
    role: str


class AuthorizationUrlResponse(BaseModel):
    authorization_url: str
    state: str


def _get_or_create_default_org(db: Session) -> Organization:
    org = db.scalar(select(Organization))
    if org is None:
        org = Organization(name="Default", plan="enterprise")
        db.add(org)
        db.commit()
        db.refresh(org)
    # Reaching this router at all means require_feature() already confirmed
    # an enterprise-granting license, so keep the org row's plan in sync -
    # it's what seat enforcement (support/seats.py) checks.
    current_plan = get_status().plan
    if org.plan != current_plan:
        org.plan = current_plan
        db.commit()
    return org


def _first_claim(userinfo: dict, names: list[str]) -> str | None:
    """The first of `names` (OAUTH_NAME_CLAIM / OAUTH_EMAIL_CLAIM / OAUTH_PICTURE_CLAIM) the IdP filled in."""
    return next((str(userinfo[n]).strip() for n in names if userinfo.get(n) and str(userinfo[n]).strip()), None)


@router.get(
    "/oidc/login",
    operation_id="start_oidc_login",
    response_model=AuthorizationUrlResponse,
)
def start_oidc_login() -> AuthorizationUrlResponse:
    """Returns the IdP's authorization URL + a `state` value for the
    frontend to redirect the browser to and round-trip, respectively."""
    require_feature("oauth_login")
    try:
        url, state = build_authorization_url()
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not reach the OIDC discovery endpoint: {exc}",
        ) from exc
    return AuthorizationUrlResponse(authorization_url=url, state=state)


@router.get("/oidc/callback", operation_id="oidc_callback", response_model=AuthResponse)
def oidc_callback(code: str = Query(...), db: Session = Depends(get_db)) -> AuthResponse:
    """Exchanges the authorization `code` for tokens, fetches userinfo, and
    finds or creates the corresponding local User. The frontend is
    responsible for verifying `state` matches what /oidc/login returned
    before calling this - see support/oidc_client.py's docstring."""
    require_feature("oauth_login")

    try:
        userinfo = exchange_code_for_userinfo(code)
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"OIDC code exchange failed: {exc}",
        ) from exc

    # Claim names only (no values) - what an admin needs to set OAUTH_*_CLAIM.
    log.info(
        "oauth: userinfo claims %s, email_verified=%r", sorted(userinfo), userinfo.get("email_verified", "<missing>")
    )
    org = _get_or_create_default_org(db)
    email = _first_claim(userinfo, oauth_email_claims)
    user = get_or_create_external_user(
        db,
        provider="oauth",
        provider_subject=userinfo["sub"],
        email=email,
        display_name=_first_claim(userinfo, oauth_name_claims) or userinfo["sub"],
        avatar_url=_first_claim(userinfo, oauth_picture_claims),
        # email_verified vouches for the `email` claim only, not for e.g. `upn` - unless the IdP is trusted.
        email_verified=bool(email)
        and (oauth_trust_email or (userinfo.get("email_verified") is True and email == userinfo.get("email"))),
        org=org,
    )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account has been deactivated.")
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    ensure_first_admin(db, user)

    token = create_session_token(user.id)
    return AuthResponse(token=token, user_id=user.id, display_name=user.display_name, role=user.role)
