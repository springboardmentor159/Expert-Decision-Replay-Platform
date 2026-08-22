from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.schemas.decision import (
    DecisionCreate,
    DecisionResponse,
    DecisionUpdate,
    DecisionStatus,
    DecisionStatusUpdate,
    DecisionRationaleUpdate,
    DecisionRationaleResponse,
)
from app.utils.security import get_current_user
from app.models.user import User


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
    current_user: User = Depends(get_current_user)
):
    new_decision = Decision(
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status=DecisionStatus.DRAFT.value,
        created_by=current_user.id
    )

    db.add(new_decision)
    db.commit()
    db.refresh(new_decision)

    return new_decision


# GET ALL DECISIONS (with optional filtering)
@router.get(
    "",
    response_model=list[DecisionResponse]
)
def get_decisions(
    status_filter: Optional[DecisionStatus] = Query(
        default=None,
        alias="status",
        description="Filter decisions by status"
    ),
    category: Optional[str] = Query(
        default=None,
        description="Filter decisions by category"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Decision)

    if status_filter is not None:
        query = query.filter(Decision.status == status_filter.value)

    if category is not None:
        query = query.filter(Decision.category == category)

    return query.all()


# GET DECISION BY ID
@router.get(
    "/{decision_id}",
    response_model=DecisionResponse
)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    return decision


# UPDATE DECISION
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

    # Only allowed fields can be updated.
    # id, created_by, created_at are never touched here.
    if decision_data.title is not None:
        decision.title = decision_data.title

    if decision_data.problem_statement is not None:
        decision.problem_statement = decision_data.problem_statement

    if decision_data.category is not None:
        decision.category = decision_data.category

    decision.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(decision)

    return decision


# UPDATE DECISION STATUS
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

    decision.status = status_data.status.value
    decision.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(decision)

    return decision


# Sprint 7: SET / UPDATE DECISION RATIONALE
@router.put(
    "/{decision_id}/rationale",
    response_model=DecisionRationaleResponse
)
def update_decision_rationale(
    decision_id: int,
    data: DecisionRationaleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    decision.rationale = data.rationale
    decision.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(decision)

    return DecisionRationaleResponse(
        decision_id=decision.id,
        rationale=decision.rationale
    )


# Sprint 7: GET DECISION RATIONALE
@router.get(
    "/{decision_id}/rationale",
    response_model=DecisionRationaleResponse
)
def get_decision_rationale(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    return DecisionRationaleResponse(
        decision_id=decision.id,
        rationale=decision.rationale
    )
