"""Find-or-create a User from an external OAuth2/OIDC identity.

Used by ee/oauth.py's OIDC login path so seat enforcement and org
assignment behave the same way as local signup, regardless of which
upstream IdP (Keycloak, Auth0, Azure AD, ...) actually authenticated the
user.

Email, name and avatar (picture claim) come from the IdP on every login, not just the first: a
missing or changed email fixes itself (job notification emails go there).
Emails are unique across accounts, so one already used by another account
is not taken over - logged and left alone - except that a first SSO login
with the *verified* email of an existing account links to that account
(OAUTH_LINK_BY_EMAIL, on by default).
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db.models import OAuthIdentity, Organization, User
from ..support.admin_settings import instance_setting
from ..support.globals import log, oauth_link_by_email
from ..support.seats import enforce_seat_limit


def get_or_create_external_user(
    db: Session,
    provider: str,
    provider_subject: str,
    email: str | None,
    display_name: str,
    org: Organization,
    avatar_url: str | None = None,
    email_verified: bool = False,
) -> User:
    identity = db.scalar(
        select(OAuthIdentity).where(
            OAuthIdentity.provider == provider,
            OAuthIdentity.provider_subject == provider_subject,
        )
    )
    if identity is not None:
        user = identity.user
        user.display_name = display_name
        user.avatar_url = _web_url(avatar_url)
        if email and email != user.email:
            if _email_taken(db, email, user.id):
                log.warning("oauth: not changing %s's email to %s - another account uses it", user.id, email)
            else:
                user.email = email
        return user

    # New external identity with the verified email of an existing account: that's the same person - sign them
    # into it (OAUTH_LINK_BY_EMAIL). Never on an unverified email, or whoever can set one at the IdP could take
    # over the account. The password keeps working next to SSO.
    if email and email_verified and oauth_link_by_email:
        existing = db.scalar(select(User).where(func.lower(User.email) == email.lower(), User.role != "guest").limit(1))
        if existing is not None:
            db.add(OAuthIdentity(user_id=existing.id, provider=provider, provider_subject=provider_subject))
            existing.avatar_url = _web_url(avatar_url)
            db.commit()
            log.info("oauth: linked %s identity to existing account %s by email", provider, existing.id)
            return existing

    # New external identity: enforce the seat limit before creating a row,
    # not after - never let a signup succeed and then get "un-created".
    # The admin's "signup closed" only stops email & password registration:
    # whoever the IdP lets through gets an account (seat limit still applies).
    enforce_seat_limit(db, org)

    if email and _email_taken(db, email, None):
        log.warning("oauth: new account without email - %s is used by another account", email)
        email = None
    user = User(
        email=email,
        display_name=display_name,
        avatar_url=_web_url(avatar_url),
        auth_provider="oauth",
        role=instance_setting(db, "default_role"),
        org_id=org.id,
    )
    db.add(user)
    db.flush()  # assign user.id without committing yet

    db.add(OAuthIdentity(user_id=user.id, provider=provider, provider_subject=provider_subject))
    db.commit()
    db.refresh(user)
    return user


def _email_taken(db: Session, email: str, user_id: str | None) -> bool:
    return db.scalar(select(User.id).where(User.email == email, User.id != user_id).limit(1)) is not None


def _web_url(url: str | None) -> str | None:
    """Only http(s) URLs - the value ends up in an <img src> in every browser that shows this user."""
    return url if url and url.lower().startswith(("https://", "http://")) and len(url) <= 2000 else None
