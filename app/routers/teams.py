from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.team import Team
from app.models.user import User


router = APIRouter(
    prefix="/teams",
    tags=["Teams"]
)


# =========================================================
# REQUEST SCHEMA
# =========================================================

class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None


# =========================================================
# CREATE TEAM
# =========================================================

@router.post("")
def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    existing_team = (
        db.query(Team)
        .filter(Team.name == team_data.name)
        .first()
    )

    if existing_team:
        raise HTTPException(
            status_code=400,
            detail="Team with this name already exists"
        )

    team = Team(
        name=team_data.name,
        description=team_data.description
    )

    db.add(team)
    db.commit()
    db.refresh(team)

    return {
        "id": team.id,
        "name": team.name,
        "description": team.description
    }


# =========================================================
# GET ALL TEAMS
# =========================================================

@router.get("")
def get_teams(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    teams = db.query(Team).all()

    return [
        {
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "member_count": len(team.members)
        }
        for team in teams
    ]


# =========================================================
# GET TEAM BY ID
# =========================================================

@router.get("/{team_id}")
def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    team = (
        db.query(Team)
        .filter(Team.id == team_id)
        .first()
    )

    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    return {
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "member_count": len(team.members)
    }


# =========================================================
# ADD USER TO TEAM
# =========================================================

@router.post("/{team_id}/members/{user_id}")
def add_team_member(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    team = (
        db.query(Team)
        .filter(Team.id == team_id)
        .first()
    )

    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user in team.members:
        raise HTTPException(
            status_code=400,
            detail="User is already a member of this team"
        )

    team.members.append(user)

    db.commit()

    return {
        "message": "User added to team successfully",
        "team_id": team.id,
        "user_id": user.id
    }


# =========================================================
# GET TEAM MEMBERS
# =========================================================

@router.get("/{team_id}/members")
def get_team_members(
    team_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    team = (
        db.query(Team)
        .filter(Team.id == team_id)
        .first()
    )

    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    return [
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role
        }
        for user in team.members
    ]


# =========================================================
# REMOVE USER FROM TEAM
# =========================================================

@router.delete("/{team_id}/members/{user_id}")
def remove_team_member(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    team = (
        db.query(Team)
        .filter(Team.id == team_id)
        .first()
    )

    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user not in team.members:
        raise HTTPException(
            status_code=404,
            detail="User is not a member of this team"
        )

    team.members.remove(user)

    db.commit()

    return {
        "message": "User removed from team successfully",
        "team_id": team.id,
        "user_id": user.id
    }