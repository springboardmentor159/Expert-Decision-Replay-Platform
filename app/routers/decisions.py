from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.schemas.decision import DecisionCreate, DecisionResponse
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"],
    dependencies=[Depends(get_current_user)]
)
@router.post(
    "",
    response_model=DecisionResponse,
    status_code=201
)
def create_decision(
    decision_data: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    new_decision = Decision(
        title=decision_data.title,
        problem_statement=decision_data.problem_statement,
        category=decision_data.category,
        status="Draft",
        created_by=int(current_user["sub"])
    )

    db.add(new_decision)
    db.commit()
    db.refresh(new_decision)

    return new_decision
@router.get(
    "",
    response_model=List[DecisionResponse]
)
def get_decisions(
    db: Session = Depends(get_db)
):
    return db.query(Decision).all()
@router.get(
    "/{decision_id}",
    response_model=DecisionResponse
)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    return decision