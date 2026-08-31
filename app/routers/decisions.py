from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.models.decision_status import DecisionStatus
from app.models.tag import Tag
from app.models.user import User
from app.schemas.decision import (
    DecisionCreate,
    DecisionResponse,
    DecisionUpdate,
    DecisionStatusUpdate,
)
from app.core.security import get_current_user


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)


# ==========================================
# CREATE DECISION
# ==========================================
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
        rationale=decision.rationale,
        status=DecisionStatus.DRAFT,
        created_by=current_user.id
    )

    db.add(new_decision)
    db.commit()
    db.refresh(new_decision)

    return new_decision


# ==========================================
# GET ALL DECISIONS + FILTERING + SEARCH
# ==========================================
@router.get(
    "",
    response_model=List[DecisionResponse]
)
def get_decisions(
    status_filter: Optional[DecisionStatus] = Query(
        default=None,
        alias="status"
    ),
    category: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Decision)

    # Filter by status
    if status_filter is not None:
        query = query.filter(
            Decision.status == status_filter
        )

    # Filter by category
    if category is not None:
        query = query.filter(
            Decision.category == category
        )

    # Filter by tag name
    if tag is not None:
        query = (
            query
            .join(Decision.tags)
            .filter(Tag.name == tag)
        )

    # Search by title, problem statement, or rationale
    if search is not None:
        search_term = f"%{search}%"

        query = query.filter(
            or_(
                Decision.title.ilike(search_term),
                Decision.problem_statement.ilike(search_term),
                Decision.rationale.ilike(search_term),
            )
        )

    return query.distinct().all()


# ==========================================
# GET DECISION BY ID
# ==========================================
@router.get(
    "/{decision_id}",
    response_model=DecisionResponse
)
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return decision


# ==========================================
# UPDATE DECISION
# ==========================================
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
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    # Only the creator can update the decision
    if decision.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this decision"
        )

    # Update only provided fields
    if decision_data.title is not None:
        decision.title = decision_data.title

    if decision_data.problem_statement is not None:
        decision.problem_statement = decision_data.problem_statement

    if decision_data.category is not None:
        decision.category = decision_data.category

    if decision_data.rationale is not None:
        decision.rationale = decision_data.rationale

    db.commit()
    db.refresh(decision)

    return decision


# ==========================================
# UPDATE DECISION STATUS
# ==========================================
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
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    # Only the creator can change the decision status
    if decision.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this decision status"
        )

    decision.status = status_data.status

    db.commit()
    db.refresh(decision)

    return decision