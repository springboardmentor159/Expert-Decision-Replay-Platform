from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.decision import Decision
from app.models.decision_version import DecisionVersion
from app.models.user import User
from app.schemas.decision_version import (
    DecisionVersionCreate,
    DecisionVersionResponse,
)

router = APIRouter(
    prefix="/decisions",
    tags=["Decision Versions"]
)


@router.post(
    "/{decision_id}/versions",
    response_model=DecisionVersionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_decision_version(
    decision_id: int,
    version_data: DecisionVersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    last_version = (
        db.query(DecisionVersion)
        .filter(DecisionVersion.decision_id == decision_id)
        .order_by(DecisionVersion.version_number.desc())
        .first()
    )

    next_version = 1 if last_version is None else last_version.version_number + 1

    new_version = DecisionVersion(
        decision_id=decision_id,
        version_number=next_version,
        title=version_data.title,
        description=version_data.description,
        status=version_data.status,
        created_by=current_user.id,
    )

    db.add(new_version)
    db.commit()
    db.refresh(new_version)

    return new_version