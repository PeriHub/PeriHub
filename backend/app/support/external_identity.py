# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Find-or-create a User from an external OAuth2/OIDC identity.

Used by routers/oauth.py's OIDC login path so seat enforcement and org
assignment behave the same way as local signup, regardless of which
upstream IdP (Keycloak, Auth0, Azure AD, ...) actually authenticated the
user.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.models import OAuthIdentity, Organization, User
from .seats import enforce_seat_limit


def get_or_create_external_user(
    db: Session,
    provider: str,
    provider_subject: str,
    email: str | None,
    display_name: str,
    org: Organization,
) -> User:
    identity = db.scalar(
        select(OAuthIdentity).where(
            OAuthIdentity.provider == provider,
            OAuthIdentity.provider_subject == provider_subject,
        )
    )
    if identity is not None:
        return identity.user

    # New external identity: enforce the seat limit before creating a row,
    # not after - never let a signup succeed and then get "un-created".
    enforce_seat_limit(db, org)

    user = User(
        email=email,
        display_name=display_name,
        auth_provider="oauth",
        role="member",
        org_id=org.id,
    )
    db.add(user)
    db.flush()  # assign user.id without committing yet

    db.add(OAuthIdentity(user_id=user.id, provider=provider, provider_subject=provider_subject))
    db.commit()
    db.refresh(user)
    return user
