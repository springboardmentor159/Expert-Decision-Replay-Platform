from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.alternative import Alternative
from app.models.decision import Decision
from app.models.user import User
from app.schemas.alternative import (
    AlternativeCreate,
    AlternativeResponse,
    AlternativeUpdate,
    AlternativeComparison,
    AlternativeComparisonItem,
)

router = APIRouter(prefix="/alternatives", tags=["Alternatives"])


@router.post(
    "",
    response_model=AlternativeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new alternative for a decision",
    description="Create a new alternative associated with a decision.",
)
def create_alternative(
    decision_id: int,
    alternative: AlternativeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new alternative for a decision.
    - **decision_id**: ID of the decision this alternative belongs to
    - **name**: Alternative name
    - **description**: Description of the option
    - **pros**: Advantages
    - **cons**: Disadvantages
    - **estimated_cost**: Expected cost
    - **feasibility_score**: Feasibility (1-5)
    - **risk_level**: Risk level (Low, Medium, High, Critical)
    """
    # Check if decision exists
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    # Create alternative
    db_alternative = Alternative(
        decision_id=decision_id,
        name=alternative.name,
        description=alternative.description,
        pros=alternative.pros,
        cons=alternative.cons,
        estimated_cost=alternative.estimated_cost,
        feasibility_score=alternative.feasibility_score,
        risk_level=alternative.risk_level,
    )
    db.add(db_alternative)
    db.commit()
    db.refresh(db_alternative)
    return db_alternative


@router.get(
    "/{alternative_id}",
    response_model=AlternativeResponse,
    summary="Get a specific alternative",
    description="Retrieve a specific alternative by ID.",
)
def get_alternative(
    alternative_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific alternative by ID.
    - Returns 404 if alternative not found
    """
    alternative = db.query(Alternative).filter(Alternative.id == alternative_id).first()
    if not alternative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found",
        )
    return alternative


@router.put(
    "/{alternative_id}",
    response_model=AlternativeResponse,
    summary="Update an alternative",
    description="Update an existing alternative. Fields like id, decision_id, and created_at cannot be changed.",
)
def update_alternative(
    alternative_id: int,
    alternative_update: AlternativeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an alternative.
    - All fields are optional
    - Fields that CANNOT be changed: id, decision_id, created_at
    - Returns 404 if alternative not found
    """
    alternative = db.query(Alternative).filter(Alternative.id == alternative_id).first()
    if not alternative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found",
        )

    # Update only the provided fields
    if alternative_update.name is not None:
        alternative.name = alternative_update.name
    if alternative_update.description is not None:
        alternative.description = alternative_update.description
    if alternative_update.pros is not None:
        alternative.pros = alternative_update.pros
    if alternative_update.cons is not None:
        alternative.cons = alternative_update.cons
    if alternative_update.estimated_cost is not None:
        alternative.estimated_cost = alternative_update.estimated_cost
    if alternative_update.feasibility_score is not None:
        alternative.feasibility_score = alternative_update.feasibility_score
    if alternative_update.risk_level is not None:
        alternative.risk_level = alternative_update.risk_level

    db.commit()
    db.refresh(alternative)
    return alternative


# Decision-specific endpoints
decision_router = APIRouter(prefix="/decisions", tags=["Alternatives"])


@decision_router.post(
    "/{decision_id}/alternatives",
    response_model=AlternativeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new alternative for a decision",
    description="Create a new alternative associated with a specific decision.",
)
def create_decision_alternative(
    decision_id: int,
    alternative: AlternativeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new alternative for a decision.
    - **decision_id**: ID of the decision (from URL)
    - **name**: Alternative name
    - **description**: Description of the option
    - **pros**: Advantages
    - **cons**: Disadvantages
    - **estimated_cost**: Expected cost
    - **feasibility_score**: Feasibility (1-5)
    - **risk_level**: Risk level (Low, Medium, High, Critical)
    """
    # Check if decision exists
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    # Create alternative
    db_alternative = Alternative(
        decision_id=decision_id,
        name=alternative.name,
        description=alternative.description,
        pros=alternative.pros,
        cons=alternative.cons,
        estimated_cost=alternative.estimated_cost,
        feasibility_score=alternative.feasibility_score,
        risk_level=alternative.risk_level,
    )
    db.add(db_alternative)
    db.commit()
    db.refresh(db_alternative)
    return db_alternative


@decision_router.get(
    "/{decision_id}/alternatives",
    response_model=List[AlternativeResponse],
    summary="Get all alternatives for a decision",
    description="Retrieve all alternatives belonging to a specific decision.",
)
def get_decision_alternatives(
    decision_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all alternatives for a decision.
    - **decision_id**: ID of the decision
    - Returns empty list if decision has no alternatives
    - Returns 404 if decision doesn't exist
    """
    # Check if decision exists
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    alternatives = db.query(Alternative).filter(Alternative.decision_id == decision_id).all()
    return alternatives


@decision_router.get(
    "/{decision_id}/alternatives/compare",
    response_model=AlternativeComparison,
    summary="Compare alternatives for a decision",
    description="Get alternatives in a comparison-friendly format.",
)
def compare_alternatives(
    decision_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Compare alternatives for a decision.
    - Returns alternatives with key comparison fields
    - **decision_id**: ID of the decision
    """
    # Check if decision exists
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    alternatives = db.query(Alternative).filter(Alternative.decision_id == decision_id).all()
    
    comparison_items = [
        AlternativeComparisonItem(
            name=alt.name,
            estimated_cost=alt.estimated_cost,
            feasibility_score=alt.feasibility_score,
            risk_level=alt.risk_level,
        )
        for alt in alternatives
    ]

    return AlternativeComparison(
        decision_id=decision_id,
        alternatives=comparison_items,
    )
