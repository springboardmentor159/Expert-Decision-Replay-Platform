from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.decision import Decision
from app.models.user import User
from app.schemas.decision import (
    DecisionCreate,
    DecisionResponse,
    DecisionStatus,
    DecisionStatusUpdate,
    DecisionUpdate,
)

router = APIRouter(prefix="/decisions", tags=["Decisions"])


@router.post(
    "",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new decision",
    description="Create a new decision. User must be authenticated.",
)
def create_decision(
    decision: DecisionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new decision.
    - **title**: Decision title
    - **problem_statement**: Description of the problem
    - **category**: Decision category
    - Status is automatically set to "Draft"
    """
    db_decision = Decision(
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status=DecisionStatus.Draft.value,
        created_by=current_user.id,
    )
    db.add(db_decision)
    db.commit()
    db.refresh(db_decision)
    return db_decision


@router.get(
    "",
    response_model=List[DecisionResponse],
    summary="Get all decisions with optional filtering",
    description="Retrieve decisions. Can filter by status and/or category.",
)
def get_decisions(
    status: Optional[str] = Query(None, description="Filter by decision status"),
    category: Optional[str] = Query(None, description="Filter by decision category"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all decisions with optional filtering.
    - **status**: Filter by status (Draft, Under Review, Approved, Rejected, Archived)
    - **category**: Filter by category
    - User must be authenticated
    """
    query = db.query(Decision)

    if status:
        query = query.filter(Decision.status == status)

    if category:
        query = query.filter(Decision.category == category)

    return query.all()


@router.get(
    "/{decision_id}",
    response_model=DecisionResponse,
    summary="Get a specific decision",
    description="Retrieve a specific decision by ID.",
)
def get_decision(
    decision_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific decision by ID.
    - Returns 404 if decision not found
    """
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )
    return decision


@router.put(
    "/{decision_id}",
    response_model=DecisionResponse,
    summary="Update a decision",
    description="Update an existing decision. Fields like id, created_by, and created_at cannot be changed.",
)
def update_decision(
    decision_id: int,
    decision_update: DecisionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a decision.
    - **title**: Update the decision title (optional)
    - **problem_statement**: Update the problem statement (optional)
    - **category**: Update the category (optional)
    - Fields that CANNOT be changed: id, created_by, created_at
    - Returns 404 if decision not found
    """
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    # Update only the allowed fields
    if decision_update.title is not None:
        decision.title = decision_update.title
    if decision_update.problem_statement is not None:
        decision.problem_statement = decision_update.problem_statement
    if decision_update.category is not None:
        decision.category = decision_update.category

    db.commit()
    db.refresh(decision)
    return decision


@router.patch(
    "/{decision_id}/status",
    response_model=DecisionResponse,
    summary="Update decision status",
    description="Update the status of a decision to a valid status value.",
)
def update_decision_status(
    decision_id: int,
    status_update: DecisionStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update decision status.
    - **status**: New status (Draft, Under Review, Approved, Rejected, Archived)
    - Only valid status values are accepted
    - Returns 404 if decision not found
    """
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    # Update status with validated enum value
    decision.status = status_update.status.value

    db.commit()
    db.refresh(decision)
    return decision


@router.delete(
    "/{decision_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a decision",
    description="Delete a decision (soft delete via status change to Archived).",
)
def delete_decision(
    decision_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a decision (archived).
    - Returns 404 if decision not found
    """
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    decision.status = DecisionStatus.Archived.value
    db.commit()
    return None
