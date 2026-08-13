from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.decision import (
    DecisionCreate,
    DecisionUpdate,
    DecisionResponse
)

router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)


@router.post("/", response_model=DecisionResponse)
def create_decision(
    decision: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_decision = Decision(
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        created_by=current_user.id
    )

    db.add(new_decision)
    db.commit()
    db.refresh(new_decision)

    return new_decision


@router.get("/", response_model=list[DecisionResponse])
def get_all_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decisions = db.query(Decision).all()
    return decisions


@router.get("/{decision_id}", response_model=DecisionResponse)
def get_decision(
    decision_id: int,
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

    return decision


@router.put("/{decision_id}", response_model=DecisionResponse)
def update_decision(
    decision_id: int,
    decision_data: DecisionUpdate,
    db: Session = Depends(get_db)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    decision.title = decision_data.title
    decision.problem_statement = decision_data.problem_statement
    decision.category = decision_data.category
    decision.status = decision_data.status

    db.commit()
    db.refresh(decision)

    return decision


@router.delete("/{decision_id}")
def delete_decision(
    decision_id: int,
    db: Session = Depends(get_db)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    db.delete(decision)
    db.commit()

    return {
        "message": "Decision deleted successfully"
    }