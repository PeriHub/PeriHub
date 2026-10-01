# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""DB-backed identity resolution.

The caller is identified only by a credential the server can verify:
  1. X-Api-Key            (user-generated key, see support/api_keys.py)
  2. Authorization Bearer (session JWT from local/OAuth/guest login, see support/local_auth.py)

The old client-supplied `userName` header is no longer trusted - anyone could set it and act on another user's
folder. Folders are keyed by `user.id` (support/guest.user_folder).
"""

from dataclasses import dataclass

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.models import User
from .api_keys import user_from_api_key
from .local_auth import decode_session_token


@dataclass
class ResolvedIdentity:
    username: str  # folder identity: the user's id, "" when unauthenticated
    user: User | None = None


def _user_from_bearer_token(request: Request, db: Session) -> User | None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    user_id = decode_session_token(auth_header.removeprefix("Bearer ").strip())
    if not user_id:
        return None
    return db.scalar(select(User).where(User.id == user_id, User.is_active.is_(True)))


def resolve_user(request: Request, db: Session | None = None) -> ResolvedIdentity:
    """Resolves the caller's account; `user` is None without a DB session or a valid credential."""
    user = None
    if db is not None:
        api_key = request.headers.get("X-Api-Key")
        user = user_from_api_key(db, api_key) if api_key else _user_from_bearer_token(request, db)
    return ResolvedIdentity(username=user.id if user else "", user=user)
