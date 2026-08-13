from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.schemas.decision import DecisionCreate, DecisionResponse
from app.routers.users import get_current_user


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)


# CREATE DECISION
@router.post(
    "",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_decision(
    decision: DecisionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    new_decision = Decision(
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status="Draft",
        created_by=int(current_user["sub"])
    )

    db.add(new_decision)
    db.commit()
    db.refresh(new_decision)

    return new_decision


# GET ALL DECISIONS
@router.get(
    "",
    response_model=List[DecisionResponse]
)
def get_decisions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Decision).all()


# GET DECISION BY ID
@router.get(
    "/{decision_id}",
    response_model=DecisionResponse
)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return decision