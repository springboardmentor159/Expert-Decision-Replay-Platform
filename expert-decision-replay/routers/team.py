from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.team import Team
from app.models.user import User
from app.schemas.team import TeamCreate, TeamResponse


router = APIRouter(
    prefix="/teams",
    tags=["Teams"]
)


@router.post(
    "/",
    response_model=TeamResponse
)
def create_team(
    team: TeamCreate,
    db: Session = Depends(get_db)
):
    existing_team = (
        db.query(Team)
        .filter(Team.name == team.name)
        .first()
    )

    if existing_team:
        raise HTTPException(
            status_code=400,
            detail="Team already exists"
        )

    new_team = Team(
        name=team.name,
        description=team.description,
        department=team.department,
        team_lead_id=team.team_lead_id,
        status=team.status
    )

    db.add(new_team)
    db.commit()
    db.refresh(new_team)

    return new_team


@router.get(
    "/",
    response_model=list[TeamResponse]
)
def get_all_teams(
    db: Session = Depends(get_db)
):
    return db.query(Team).all()
@router.get(
    "/{team_id}/members"
)
def get_team_members(
    team_id: int,
    db: Session = Depends(get_db)
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

    members = (
        db.query(User)
        .filter(User.team_id == team_id)
        .all()
    )

    return {
        "team_id": team.id,
        "team_name": team.name,
        "members": [
            {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "department": user.department,
                "designation": user.designation,
                "role": user.role
            }
            for user in members
        ]
    }
@router.put(
    "/{team_id}/members/{user_id}"
)
def assign_user_to_team(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db)
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

    user.team_id = team_id

    db.commit()
    db.refresh(user)

    return {
        "message": "User assigned to team successfully",
        "user_id": user.id,
        "user_name": user.full_name,
        "team_id": team.id,
        "team_name": team.name
    }
@router.delete(
    "/{team_id}/members/{user_id}"
)
def remove_user_from_team(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db)
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
        .filter(
            User.id == user_id,
            User.team_id == team_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User is not a member of this team"
        )

    user.team_id = None

    db.commit()
    db.refresh(user)

    return {
        "message": "User removed from team successfully",
        "user_id": user.id,
        "user_name": user.full_name,
        "team_id": team.id,
        "team_name": team.name
    }