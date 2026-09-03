from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.decision import Decision
from app.models.decision_rationale import DecisionRationale
from app.models.user import User


router = APIRouter(
    prefix="/decisions",
    tags=["Decision Rationale"]
)


class RationaleCreate(BaseModel):
    content: str


class RationaleResponse(BaseModel):
    id: int
    decision_id: int
    user_id: int
    content: str

    class Config:
        from_attributes = True


@router.post(
    "/{decision_id}/rationale",
    response_model=RationaleResponse,
    status_code=status.HTTP_201_CREATED
)
def create_rationale(
    decision_id: int,
    rationale_data: RationaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    existing = db.query(DecisionRationale).filter(
        DecisionRationale.decision_id == decision_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Rationale already exists"
        )

    rationale = DecisionRationale(
        decision_id=decision_id,
        user_id=current_user.id,
        content=rationale_data.content
    )

    db.add(rationale)
    db.commit()
    db.refresh(rationale)

    return rationale


@router.get(
    "/{decision_id}/rationale",
    response_model=RationaleResponse
)
def get_rationale(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rationale = db.query(DecisionRationale).filter(
        DecisionRationale.decision_id == decision_id
    ).first()

    if not rationale:
        raise HTTPException(
            status_code=404,
            detail="Rationale not found"
        )

    return rationale