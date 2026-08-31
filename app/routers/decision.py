from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.decision import Decision
from app.models.enums import DecisionStatus, UserRole
from app.models.user import User
from app.services.activity import log_activity
from app.schemas.decision import (
    DecisionCreate,
    DecisionRationaleUpdate,
    DecisionResponse,
    DecisionStatusUpdate,
    DecisionUpdate,
)

router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)


@router.post(
    "",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_decision(
    decision_data: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_decision = Decision(
        title=decision_data.title,
        problem_statement=decision_data.problem_statement,
        category=decision_data.category,
        status="Draft",
        created_by=current_user.id
    )

    db.add(new_decision)
    db.commit()
    db.refresh(new_decision)

    log_activity(
        db,
        current_user.id,
        "create",
        "decision",
        new_decision.id,
        f"Created decision '{new_decision.title}'",
    )

    return new_decision


@router.get(
    "",
    response_model=List[DecisionResponse]
)
def get_decisions(
    status: Optional[DecisionStatus] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Decision)

    if status is not None:
        query = query.filter(Decision.status == status.value)

    if category is not None:
        query = query.filter(Decision.category == category)

    decisions = query.all()
    return decisions


@router.get(
    "/{decision_id}",
    response_model=DecisionResponse
)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return decision


@router.put(
    "/{decision_id}",
    response_model=DecisionResponse
)
def update_decision(
    decision_id: int,
    decision_data: DecisionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    if decision_data.title is not None:
        decision.title = decision_data.title

    if decision_data.problem_statement is not None:
        decision.problem_statement = decision_data.problem_statement

    if decision_data.category is not None:
        decision.category = decision_data.category

    decision.updated_at = func.now()

    db.commit()
    db.refresh(decision)

    log_activity(
        db,
        current_user.id,
        "update",
        "decision",
        decision.id,
        f"Updated decision '{decision.title}'",
    )

    return decision


@router.patch(
    "/{decision_id}/status",
    response_model=DecisionResponse
)
def update_decision_status(
    decision_id: int,
    status_data: DecisionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    old_status = decision.status.value if isinstance(decision.status, DecisionStatus) else decision.status
    decision.status = status_data.status
    decision.updated_at = func.now()

    db.commit()
    db.refresh(decision)

    log_activity(
        db,
        current_user.id,
        "status_change",
        "decision",
        decision.id,
        f"Changed decision status from '{old_status}' to '{decision.status.value if isinstance(decision.status, DecisionStatus) else decision.status}'",
    )

    return decision


@router.put(
    "/{decision_id}/rationale",
    response_model=DecisionResponse
)
def update_decision_rationale(
    decision_id: int,
    rationale_data: DecisionRationaleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    if decision.created_by != current_user.id and current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this decision rationale"
        )

    decision.rationale = rationale_data.rationale
    decision.updated_at = func.now()

    db.commit()
    db.refresh(decision)

    return decision
