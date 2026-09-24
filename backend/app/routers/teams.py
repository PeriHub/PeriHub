# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Teams (org sub-groups) - Phase 2.

Unlike projects (any member can spin one up), teams are an org-structure
concept - only an org admin creates them or changes membership, matching
how a real enterprise customer would manage its own org chart.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..db.models import Team, TeamMembership, User
from ..support.db_auth import resolve_user
from ..support.globals import dev
from ..support.rbac import require_role

router = APIRouter(prefix="/teams", tags=["Project Methods"])


class TeamIn(BaseModel):
    name: str


class TeamOut(BaseModel):
    id: str
    org_id: str
    name: str


def _require_db_user(request: Request, db: Session) -> User:
    identity = resolve_user(request, dev, db)
    if identity.user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required.")
    return identity.user


@router.get("", operation_id="list_teams", response_model=list[TeamOut])
def list_teams(request: Request, db: Session = Depends(get_db)):
    user = _require_db_user(request, db)
    rows = db.scalars(select(Team).where(Team.org_id == user.org_id))
    return list(rows)


@router.post("", operation_id="create_team", response_model=TeamOut)
def create_team(payload: TeamIn, request: Request, db: Session = Depends(get_db)):
    user = _require_db_user(request, db)
    require_role(user, "admin")
    if user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Account must belong to an organization.",
        )
    team = Team(org_id=user.org_id, name=payload.name)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


@router.post("/{team_id}/members/{user_id}", operation_id="add_team_member")
def add_team_member(team_id: str, user_id: str, request: Request, db: Session = Depends(get_db)):
    user = _require_db_user(request, db)
    require_role(user, "admin")
    team = db.get(Team, team_id)
    if team is None or team.org_id != user.org_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found.")

    existing = db.scalar(
        select(TeamMembership).where(TeamMembership.team_id == team_id, TeamMembership.user_id == user_id)
    )
    if existing is None:
        db.add(TeamMembership(team_id=team_id, user_id=user_id))
        db.commit()
    return {"team_id": team_id, "user_id": user_id}


@router.delete("/{team_id}/members/{user_id}", operation_id="remove_team_member")
def remove_team_member(team_id: str, user_id: str, request: Request, db: Session = Depends(get_db)):
    user = _require_db_user(request, db)
    require_role(user, "admin")
    membership = db.scalar(
        select(TeamMembership).where(TeamMembership.team_id == team_id, TeamMembership.user_id == user_id)
    )
    if membership is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found.")
    db.delete(membership)
    db.commit()
    return {"removed": user_id}
