"""Password hashing + session tokens for local email/password auth.

Community and enterprise plans both get local auth (it's the baseline,
free tier); OAuth2/OIDC is enterprise-only and gated via
support/entitlements.py, not here.

Session tokens are plain JWTs signed with SESSION_SECRET (HS256) - no
server-side session table in Phase 0. That means logout is client-side
only (the token is valid until it expires) and there's no revocation list
yet; if that's needed before Phase 1, add a `revoked_sessions` table keyed
by the JWT's `jti` claim rather than reworking this module.
"""

import hashlib
import hmac
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from .globals import session_secret, session_ttl_seconds

_pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

_JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _pwd_context.verify(password, password_hash)
    except ValueError:
        # Malformed/foreign hash format - treat as a failed check, not a crash.
        return False


def create_session_token(user_id: str) -> str:
    """Issues a signed JWT identifying `user_id`, valid for
    SESSION_TTL_SECONDS. Raises RuntimeError if SESSION_SECRET isn't
    configured (refuses to sign with an empty/default secret)."""
    if not session_secret:
        raise RuntimeError(
            "SESSION_SECRET is not configured - refusing to issue session tokens. "
            "Set SESSION_SECRET to a long random value before enabling local auth."
        )
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": now + timedelta(seconds=session_ttl_seconds),
    }
    return jwt.encode(payload, session_secret, algorithm=_JWT_ALGORITHM)


def decode_session_token(token: str) -> str | None:
    """Returns the user_id embedded in a valid, unexpired session token, or
    None if the token is missing/invalid/expired."""
    if not session_secret:
        return None
    try:
        payload = jwt.decode(token, session_secret, algorithms=[_JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None
    return payload.get("sub")


# Password reset links (Phase 1): stateless like sessions. Signed with a key
# derived from SESSION_SECRET but distinct from it, so a reset token can never
# pass decode_session_token(); it carries a fingerprint of the current
# password hash, so it stops working once the password changes - i.e. it is
# single-use without a token table.
_RESET_TTL = timedelta(hours=1)


def _reset_key() -> str:
    return hashlib.sha256(f"password-reset:{session_secret}".encode()).hexdigest()


def _password_fingerprint(password_hash: str) -> str:
    return hashlib.sha256(password_hash.encode()).hexdigest()[:32]


def create_password_reset_token(user_id: str, password_hash: str) -> str:
    if not session_secret:
        raise RuntimeError("SESSION_SECRET is not configured - refusing to issue password reset tokens.")
    now = datetime.now(timezone.utc)
    payload = {"uid": user_id, "pwd": _password_fingerprint(password_hash), "iat": now, "exp": now + _RESET_TTL}
    return jwt.encode(payload, _reset_key(), algorithm=_JWT_ALGORITHM)


def decode_password_reset_token(token: str) -> tuple[str, str] | None:
    """(user_id, password fingerprint) of a valid, unexpired reset token, else None. The caller must compare
    the fingerprint with password_matches_fingerprint() to reject already-used links."""
    if not session_secret:
        return None
    try:
        payload = jwt.decode(token, _reset_key(), algorithms=[_JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None
    if not payload.get("uid") or not payload.get("pwd"):
        return None
    return payload["uid"], payload["pwd"]


def password_matches_fingerprint(password_hash: str | None, fingerprint: str) -> bool:
    return bool(password_hash) and hmac.compare_digest(_password_fingerprint(password_hash), fingerprint)
