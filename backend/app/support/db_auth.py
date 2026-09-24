# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""DB-backed identity resolution (Phase 0).

FileHandler.get_user_name() trusts a client-supplied `userName` header,
which was fine when "identity" only meant "which folder to write simulation
files into". Now that identity also controls DB rows (ownership of shared
model configs/materials, roles, seats), that header can't be trusted on its
own any more.

This module adds `resolve_user()`, layered the same additive way
api_key_auth.get_user_name_with_api_key() already is: each check either
returns a resolved User or falls through to the next one, so nothing that
already works (API keys, OAuth header flow, trial guests) breaks while
routers migrate to this over time.

Resolution order:
  1. X-Api-Key            (existing behaviour, unchanged - service accounts)
  2. Authorization Bearer (local-auth session JWT, see support/local_auth.py)
  3. `userName` header    (legacy/OAuth/trial path via FileHandler)

Full migration of every router call site from FileHandler.get_user_name()
to resolve_user() is Phase 1 work (it needs a DB session threaded through
each endpoint); this module is the building block that unlocks it.
"""

from dataclasses import dataclass

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.models import User
from .api_key_auth import get_user_name_with_api_key
from .file_handler import FileHandler
from .globals import deployment_mode
from .local_auth import decode_session_token


@dataclass
class ResolvedIdentity:
    username: str  # display/folder identity - unchanged meaning from before
    user: User | None = None  # DB row, when auth resolved to a real account
    is_trial: bool = False


def _user_from_bearer_token(request: Request, db: Session | None) -> User | None:
    if db is None:
        return None
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.removeprefix("Bearer ").strip()
    user_id = decode_session_token(token)
    if not user_id:
        return None
    return db.scalar(select(User).where(User.id == user_id, User.is_active.is_(True)))


def resolve_user(request: Request, dev: bool, db: Session | None = None) -> ResolvedIdentity:
    """Resolves the caller's identity for the current request.

    `db` is optional so this still works in DB-less trial mode; pass it
    whenever a session is available (i.e. DATABASE_URL is configured) to
    get real account resolution instead of just the legacy header.
    """
    legacy_username = FileHandler.get_user_name(request, dev)
    legacy_username = get_user_name_with_api_key(request, dev, legacy_username)

    db_user = _user_from_bearer_token(request, db)
    if db_user is not None:
        return ResolvedIdentity(username=db_user.id, user=db_user, is_trial=False)

    return ResolvedIdentity(
        username=legacy_username,
        user=None,
        is_trial=(deployment_mode == "trial"),
    )
