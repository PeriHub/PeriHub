# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Self-service API keys (user settings). Any logged-in non-guest may create keys; a key acts as its owner with the
owner's role (support/db_auth.resolve_user), so it grants nothing the user couldn't already do. The plain key is
returned once, at creation - only its SHA-256 is stored (support/api_keys.py)."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..db.models import ApiKey, User
from ..support import audit_log
from ..support.api_keys import KEY_PREFIX_LEN, generate_key, hash_key
from ..support.guest import require_non_guest

router = APIRouter(prefix="/auth/api-keys", tags=["Auth Methods"])


class ApiKeyCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def _name(cls, value: str) -> str:
        value = value.strip()
        if not value or len(value) > 100:
            raise ValueError("Name must be 1-100 characters.")
        return value


class ApiKeyInfo(BaseModel):
    id: str
    name: str
    prefix: str
    created_at: datetime
    last_used_at: datetime | None


class ApiKeyCreated(ApiKeyInfo):
    key: str


def _info(row: ApiKey) -> dict:
    return {f: getattr(row, f) for f in ApiKeyInfo.model_fields}


@router.get("", operation_id="list_api_keys")
def list_api_keys(user: User = Depends(require_non_guest), db: Session = Depends(get_db)) -> list[ApiKeyInfo]:
    """The caller's active API keys (never the keys themselves)."""
    rows = db.scalars(
        select(ApiKey).where(ApiKey.user_id == user.id, ApiKey.revoked_at.is_(None)).order_by(ApiKey.created_at)
    )
    return [ApiKeyInfo(**_info(row)) for row in rows]


@router.post("", operation_id="create_api_key")
def create_api_key(
    payload: ApiKeyCreate,
    request: Request,
    user: User = Depends(require_non_guest),
    db: Session = Depends(get_db),
) -> ApiKeyCreated:
    """Create a key for the caller. The returned `key` is shown only this once."""
    key = generate_key()
    row = ApiKey(user_id=user.id, name=payload.name, prefix=key[:KEY_PREFIX_LEN], key_hash=hash_key(key))
    db.add(row)
    db.commit()
    db.refresh(row)
    audit_log.record(user.id, "create_api_key", row.id, request, extra={"name": row.name})
    return ApiKeyCreated(**_info(row), key=key)


@router.delete("/{key_id}", operation_id="revoke_api_key", status_code=status.HTTP_204_NO_CONTENT)
def revoke_api_key(
    key_id: str,
    request: Request,
    user: User = Depends(require_non_guest),
    db: Session = Depends(get_db),
) -> Response:
    """Revoke one of the caller's keys; 404 if it isn't theirs or is already revoked."""
    row = db.scalar(select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user.id, ApiKey.revoked_at.is_(None)))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found.")
    row.revoked_at = datetime.now(timezone.utc)
    db.commit()
    audit_log.record(user.id, "revoke_api_key", row.id, request)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
