# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""CRUD + search for shared model configs and materials.

Both resources share the same shape (owner/org/team/project/visibility +
tags + a JSON blob), so this one router handles both rather than
duplicating the same endpoints twice - `kind` selects which table via a
small dispatch dict.

Requires a logged-in DB user (support.db_auth.resolve_user) - trial's
anonymous random identity has nothing to own a shared resource as, so
these 401 in trial mode. That's an intentional gap, not an oversight:
sharing is a community/enterprise feature per the original roadmap ask.
"""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..db.models import (
    VISIBILITY_ORG,
    VISIBILITY_PRIVATE,
    VISIBILITY_PUBLIC,
    VISIBILITY_TEAM,
    Material,
    ModelConfig,
)
from ..support.db_auth import resolve_user
from ..support.globals import dev
from ..support.rbac import (
    list_visible_materials,
    list_visible_model_configs,
    require_can_edit,
    require_project_role,
)

router = APIRouter(prefix="/library", tags=["Library Methods"])

_VALID_VISIBILITY = {
    VISIBILITY_PRIVATE,
    VISIBILITY_TEAM,
    VISIBILITY_ORG,
    VISIBILITY_PUBLIC,
}
_MODEL_BY_KIND = {"model-config": ModelConfig, "material": Material}


class LibraryItemIn(BaseModel):
    name: str
    visibility: Literal["private", "team", "org", "public"] = "private"
    tags: list[str] = []
    team_id: str | None = None
    project_id: str | None = None
    description: str | None = None  # model-config only
    config: dict | None = None  # model-config only
    properties: dict | None = None  # material only
    source: str | None = None  # material only


class LibraryItemOut(BaseModel):
    id: str
    owner_id: str
    org_id: str | None
    team_id: str | None
    project_id: str | None
    name: str
    visibility: str
    tags: list[str]
    description: str | None = None
    config: dict | None = None
    properties: dict | None = None
    source: str | None = None


def _require_db_user(request: Request, db: Session):
    identity = resolve_user(request, dev, db)
    if identity.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sharing model configs/materials requires a logged-in account (not available in trial mode).",
        )
    return identity.user


def _to_out(kind: str, row) -> LibraryItemOut:
    base = dict(
        id=row.id,
        owner_id=row.owner_id,
        org_id=row.org_id,
        team_id=row.team_id,
        project_id=row.project_id,
        name=row.name,
        visibility=row.visibility,
        tags=row.tags or [],
    )
    if kind == "model-config":
        base.update(description=row.description, config=row.config)
    else:
        base.update(properties=row.properties, source=row.source)
    return LibraryItemOut(**base)


def _validate_scope(payload: LibraryItemIn, user) -> None:
    if payload.visibility == VISIBILITY_ORG and user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot share with 'org' visibility - this account isn't part of an organization.",
        )
    if payload.visibility == VISIBILITY_TEAM and not payload.team_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="'team' visibility requires team_id.",
        )


@router.get("/{kind}", operation_id="list_library_items", response_model=list[LibraryItemOut])
def list_items(
    kind: Literal["model-config", "material"],
    request: Request,
    db: Session = Depends(get_db),
    search: str | None = Query(default=None, description="Case-insensitive substring match on name"),
    tag: str | None = Query(default=None, description="Exact tag match"),
    project_id: str | None = Query(default=None),
):
    user = _require_db_user(request, db)
    lister = list_visible_model_configs if kind == "model-config" else list_visible_materials
    rows = lister(db, user, search=search, tag=tag, project_id=project_id)
    return [_to_out(kind, row) for row in rows]


@router.post("/{kind}", operation_id="create_library_item", response_model=LibraryItemOut)
def create_item(
    kind: Literal["model-config", "material"],
    payload: LibraryItemIn,
    request: Request,
    db: Session = Depends(get_db),
):
    user = _require_db_user(request, db)
    _validate_scope(payload, user)
    model = _MODEL_BY_KIND[kind]

    if payload.project_id:
        require_project_role(db, user, payload.project_id, minimum="member")

    common = dict(
        owner_id=user.id,
        org_id=user.org_id,
        team_id=payload.team_id,
        project_id=payload.project_id,
        name=payload.name,
        visibility=payload.visibility,
        tags=payload.tags,
    )
    if kind == "model-config":
        row = model(**common, description=payload.description, config=payload.config or {})
    else:
        row = model(**common, properties=payload.properties or {}, source=payload.source)

    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_out(kind, row)


def _get_owned_or_404(db: Session, kind: str, item_id: str):
    model = _MODEL_BY_KIND[kind]
    row = db.scalar(select(model).where(model.id == item_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{kind} not found.")
    return row


@router.put(
    "/{kind}/{item_id}",
    operation_id="update_library_item",
    response_model=LibraryItemOut,
)
def update_item(
    kind: Literal["model-config", "material"],
    item_id: str,
    payload: LibraryItemIn,
    request: Request,
    db: Session = Depends(get_db),
):
    user = _require_db_user(request, db)
    row = _get_owned_or_404(db, kind, item_id)
    require_can_edit(user, row)
    _validate_scope(payload, user)

    row.name = payload.name
    row.visibility = payload.visibility
    row.tags = payload.tags
    row.team_id = payload.team_id
    row.project_id = payload.project_id
    if kind == "model-config":
        row.description = payload.description
        row.config = payload.config if payload.config is not None else row.config
    else:
        row.properties = payload.properties if payload.properties is not None else row.properties
        row.source = payload.source

    db.commit()
    db.refresh(row)
    return _to_out(kind, row)


@router.delete("/{kind}/{item_id}", operation_id="delete_library_item")
def delete_item(
    kind: Literal["model-config", "material"],
    item_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    user = _require_db_user(request, db)
    row = _get_owned_or_404(db, kind, item_id)
    require_can_edit(user, row)
    db.delete(row)
    db.commit()
    return {"deleted": item_id}
