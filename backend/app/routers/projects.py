# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Projects (workspaces) - Phase 2.

Any logged-in member can create a project (becomes its "owner"); adding
other members is restricted to existing project owners or org admins, via
support.rbac.require_project_role.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..db.models import Project, ProjectMembership, User
from ..support.db_auth import resolve_user
from ..support.globals import dev
from ..support.rbac import require_project_role

router = APIRouter(prefix="/projects", tags=["Project Methods"])


class ProjectIn(BaseModel):
    name: str
    description: str | None = None


class ProjectOut(BaseModel):
    id: str
    org_id: str
    name: str
    description: str | None
    created_by: str


class MemberIn(BaseModel):
    user_id: str
    role: str = "member"  # "member" | "owner"


class MemberOut(BaseModel):
    user_id: str
    role: str


def _require_db_user(request: Request, db: Session) -> User:
    identity = resolve_user(request, dev, db)
    if identity.user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required.")
    return identity.user


@router.get("", operation_id="list_projects", response_model=list[ProjectOut])
def list_projects(request: Request, db: Session = Depends(get_db)):
    user = _require_db_user(request, db)
    member_project_ids = select(ProjectMembership.project_id).where(ProjectMembership.user_id == user.id)
    rows = db.scalars(select(Project).where(Project.id.in_(member_project_ids) | (Project.org_id == user.org_id)))
    return list(rows)


@router.post("", operation_id="create_project", response_model=ProjectOut)
def create_project(payload: ProjectIn, request: Request, db: Session = Depends(get_db)):
    user = _require_db_user(request, db)
    if user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Account must belong to an organization to create a project.",
        )

    project = Project(
        org_id=user.org_id,
        name=payload.name,
        description=payload.description,
        created_by=user.id,
    )
    db.add(project)
    db.flush()
    db.add(ProjectMembership(project_id=project.id, user_id=user.id, role="owner"))
    db.commit()
    db.refresh(project)
    return project


@router.get(
    "/{project_id}/members",
    operation_id="list_project_members",
    response_model=list[MemberOut],
)
def list_members(project_id: str, request: Request, db: Session = Depends(get_db)):
    user = _require_db_user(request, db)
    require_project_role(db, user, project_id, minimum="member")
    rows = db.scalars(select(ProjectMembership).where(ProjectMembership.project_id == project_id))
    return [MemberOut(user_id=r.user_id, role=r.role) for r in rows]


@router.post("/{project_id}/members", operation_id="add_project_member", response_model=MemberOut)
def add_member(project_id: str, payload: MemberIn, request: Request, db: Session = Depends(get_db)):
    user = _require_db_user(request, db)
    require_project_role(db, user, project_id, minimum="owner")

    existing = db.scalar(
        select(ProjectMembership).where(
            ProjectMembership.project_id == project_id,
            ProjectMembership.user_id == payload.user_id,
        )
    )
    if existing is not None:
        existing.role = payload.role
    else:
        existing = ProjectMembership(project_id=project_id, user_id=payload.user_id, role=payload.role)
        db.add(existing)
    db.commit()
    return MemberOut(user_id=payload.user_id, role=existing.role)


@router.delete("/{project_id}/members/{user_id}", operation_id="remove_project_member")
def remove_member(project_id: str, user_id: str, request: Request, db: Session = Depends(get_db)):
    user = _require_db_user(request, db)
    require_project_role(db, user, project_id, minimum="owner")
    membership = db.scalar(
        select(ProjectMembership).where(
            ProjectMembership.project_id == project_id,
            ProjectMembership.user_id == user_id,
        )
    )
    if membership is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found.")
    db.delete(membership)
    db.commit()
    return {"removed": user_id}
