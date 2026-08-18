from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.schemas.decision import (
    DecisionCreate,
    DecisionResponse,
    DecisionUpdate,
    StatusUpdate,
    DecisionStatus
)
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"],
    dependencies=[Depends(get_current_user)]
)


@router.post(
    "",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_decision(
    decision_data: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new decision. Status is automatically set to Draft."""
    new_decision = Decision(
        title=decision_data.title,
        problem_statement=decision_data.problem_statement,
        category=decision_data.category,
        status=DecisionStatus.DRAFT.value,
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
    db: Session = Depends(get_db),
    status: Optional[DecisionStatus] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """Get all decisions with optional filtering by status and category."""
    query = db.query(Decision)
    
    if status:
        query = query.filter(Decision.status == status.value)
    
    if category:
        query = query.filter(Decision.category == category)
    
    return query.all()


@router.get(
    "/{decision_id}",
    response_model=DecisionResponse
)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific decision by ID."""
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


@router.put(
    "/{decision_id}",
    response_model=DecisionResponse
)
def update_decision(
    decision_id: int,
    decision_data: DecisionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a decision. Only title, problem_statement, and category can be updated."""
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

    # Update only the allowed fields
    if decision_data.title is not None:
        decision.title = decision_data.title
    
    if decision_data.problem_statement is not None:
        decision.problem_statement = decision_data.problem_statement
    
    if decision_data.category is not None:
        decision.category = decision_data.category

    db.commit()
    db.refresh(decision)

    return decision


@router.patch(
    "/{decision_id}/status",
    response_model=DecisionResponse
)
def update_decision_status(
    decision_id: int,
    status_data: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update the status of a decision."""
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

    decision.status = status_data.status.value
    db.commit()
    db.refresh(decision)

    return decision