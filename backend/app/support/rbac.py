# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""RBAC role checks + visibility-scoped queries for shared resources.

Roles (User.role): "admin" | "developer" | "member" | "viewer" | "guest".
Deliberately flat, ranked roles rather than a permissions matrix - admin can
manage org/users/admin_settings, developer can additionally create/edit own
models (which run arbitrary Python on the server), member can create and
share model configs/materials, viewer is read-only. guest is an anonymous
throwaway account (support/guest.py) that can only run bounded jobs of
built-in models. Extend `ROLE_RANK` if a real customer needs something
finer-grained (e.g. a separate "billing" role) rather than adding string
checks scattered across routers.

Phase 2 adds: "team" visibility (narrower than "org"), project membership
checks, and tag/name search over the same visibility-filtered set.
"""

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..db.models import (
    VISIBILITY_ORG,
    VISIBILITY_PUBLIC,
    VISIBILITY_TEAM,
    Material,
    ModelConfig,
    Project,
    ProjectMembership,
    TeamMembership,
    User,
)

ROLE_RANK = {"guest": 0, "viewer": 1, "member": 2, "developer": 3, "admin": 4}


def require_role(user: User, minimum: str) -> None:
    """Raises 403 if `user`'s role is below `minimum` in ROLE_RANK."""
    if ROLE_RANK.get(user.role, -1) < ROLE_RANK.get(minimum, 99):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This action requires the '{minimum}' role or higher.",
        )


def ensure_first_admin(db: Session, user: User) -> None:
    """Promotes `user` to admin if their org has no active admin yet - the first
    person to sign up / log in administers the instance. Also covers installs
    that predate this rule: the next login in an admin-less org gets promoted.
    Guests are never promoted."""
    if user.role in ("admin", "guest"):
        return
    # ponytail: check-then-set, two simultaneous first logins can both become admin; either can demote the other.
    has_admin = db.scalar(
        select(User.id).where(User.org_id == user.org_id, User.role == "admin", User.is_active.is_(True)).limit(1)
    )
    if has_admin is None:
        user.role = "admin"
        db.commit()


def _user_team_ids(db: Session, user: User) -> list[str]:
    return list(db.scalars(select(TeamMembership.team_id).where(TeamMembership.user_id == user.id)))


def visible_to(db: Session, user: User, stmt, model, org_admin_sees_all: bool = False):
    """Adds a WHERE clause restricting `stmt` (a select() on ModelConfig or
    Material) to rows `user` is allowed to see: their own rows, anything
    shared with their team(s), anything shared org-wide within their org,
    or anything public. With `org_admin_sees_all`, an admin also sees every
    row of their org (incl. private) - the same rows can_edit() lets them edit."""
    conditions = [model.owner_id == user.id, model.visibility == VISIBILITY_PUBLIC]
    if user.org_id is not None:
        conditions.append((model.org_id == user.org_id) & (model.visibility == VISIBILITY_ORG))
        if org_admin_sees_all and user.role == "admin":
            conditions.append(model.org_id == user.org_id)
    team_ids = _user_team_ids(db, user)
    if team_ids:
        conditions.append((model.team_id.in_(team_ids)) & (model.visibility == VISIBILITY_TEAM))
    return stmt.where(or_(*conditions))


def can_edit(user: User, row) -> bool:
    """Only the owner or an org admin can edit/delete a shared resource -
    viewing (visible_to) is broader than editing."""
    if row.owner_id == user.id:
        return True
    return user.role == "admin" and user.org_id is not None and user.org_id == row.org_id


def require_can_edit(user: User, row) -> None:
    if not can_edit(user, row):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner or an org admin can modify this resource.",
        )


def _apply_search(
    stmt,
    model,
    db: Session,
    search: str | None,
    tag: str | None,
    project_id: str | None,
) -> list:
    if search:
        stmt = stmt.where(model.name.ilike(f"%{search}%"))
    if project_id:
        stmt = stmt.where(model.project_id == project_id)
    rows = list(db.scalars(stmt))
    if tag:
        # Tag filtering happens in Python rather than a DB JSON-contains
        # query so this works identically on SQLite (dev/tests) and
        # Postgres (production) without a dialect-specific query - the
        # library is expected to stay small enough per user/org that this
        # doesn't need a GIN index and a Postgres-only query yet.
        rows = [r for r in rows if tag in (r.tags or [])]
    return rows


def list_visible_model_configs(
    db: Session,
    user: User,
    search: str | None = None,
    tag: str | None = None,
    project_id: str | None = None,
) -> list[ModelConfig]:
    stmt = visible_to(db, user, select(ModelConfig), ModelConfig)
    return _apply_search(stmt, ModelConfig, db, search, tag, project_id)


def list_visible_materials(
    db: Session,
    user: User,
    search: str | None = None,
    tag: str | None = None,
    project_id: str | None = None,
) -> list[Material]:
    stmt = visible_to(db, user, select(Material), Material, org_admin_sees_all=True)
    return _apply_search(stmt, Material, db, search, tag, project_id)


def require_project_role(db: Session, user: User, project_id: str, minimum: str = "member") -> ProjectMembership:
    """Raises 403/404. Org admins always pass, matching can_edit()'s "owner
    or org admin" pattern; otherwise `user` must have a ProjectMembership
    row with at least `minimum` project role ("member" < "owner")."""
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    if user.role == "admin" and user.org_id == project.org_id:
        return ProjectMembership(project_id=project_id, user_id=user.id, role="owner")

    membership = db.scalar(
        select(ProjectMembership).where(
            ProjectMembership.project_id == project_id,
            ProjectMembership.user_id == user.id,
        )
    )
    project_role_rank = {"member": 0, "owner": 1}
    if membership is None or project_role_rank.get(membership.role, -1) < project_role_rank.get(minimum, 99):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Requires '{minimum}' membership on this project.",
        )
    return membership
