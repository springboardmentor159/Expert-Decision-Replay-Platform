from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.decision import Decision
from app.models.user import User
from app.schemas.decision import (
    DecisionCreate,
    DecisionResponse,
    DecisionStatus,
    DecisionStatusUpdate,
    DecisionUpdate,
)

router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"],
)


def get_decision_or_404(decision_id: int, db: Session) -> Decision:
    decision = db.query(Decision).filter(Decision.id == decision_id).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return decision


@router.post(
    "",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_decision(
    decision_data: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_decision = Decision(
        title=decision_data.title,
        problem_statement=decision_data.problem_statement,
        category=decision_data.category,
        status=DecisionStatus.DRAFT.value,
        created_by=current_user.id,
    )

    db.add(new_decision)
    db.commit()
    db.refresh(new_decision)

    return new_decision


@router.get("", response_model=List[DecisionResponse])
def get_decisions(
    decision_status: Optional[DecisionStatus] = Query(default=None, alias="status"),
    category: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Decision)

    if decision_status is not None:
        query = query.filter(Decision.status == decision_status.value)

    if category is not None:
        query = query.filter(Decision.category == category)

    return query.order_by(Decision.created_at.desc()).all()


@router.get("/{decision_id}", response_model=DecisionResponse)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_decision_or_404(decision_id, db)


@router.put("/{decision_id}", response_model=DecisionResponse)
def update_decision(
    decision_id: int,
    decision_data: DecisionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(decision_id, db)

    updates = decision_data.model_dump(exclude_unset=True)

    for field_name, value in updates.items():
        setattr(decision, field_name, value)

    db.commit()
    db.refresh(decision)

    return decision


@router.patch("/{decision_id}/status", response_model=DecisionResponse)
def update_decision_status(
    decision_id: int,
    status_data: DecisionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(decision_id, db)

    decision.status = status_data.status.value

    db.commit()
    db.refresh(decision)

    return decision