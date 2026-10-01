# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Per-user API keys for programmatic callers (scripts, CI).

Replaces the env-configured API_KEYS, which mapped a key to a bare username with no account behind it. A key now
belongs to a User and acts with that user's role (support/db_auth.resolve_user). Keys are long random secrets, so a
plain SHA-256 is enough to store them (no slow password hash needed) and allows a direct indexed lookup.
"""

import hashlib
import secrets
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.models import ApiKey, User

KEY_PREFIX_LEN = 12


def generate_key() -> str:
    return "phk_" + secrets.token_urlsafe(32)


def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def user_from_api_key(db: Session, key: str) -> User | None:
    """The active owner of a non-revoked key, or None. Records the key's last use."""
    row = db.execute(
        select(ApiKey, User)
        .join(User, User.id == ApiKey.user_id)
        .where(ApiKey.key_hash == hash_key(key), ApiKey.revoked_at.is_(None), User.is_active.is_(True))
    ).first()
    if row is None:
        return None
    api_key, user = row
    api_key.last_used_at = datetime.now(timezone.utc)
    db.commit()
    return user
