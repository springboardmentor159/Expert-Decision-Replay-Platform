from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.decision import Decision
from app.models.alternative import Alternative

from app.schemas.alternative import (
    AlternativeCreate,
    AlternativeUpdate,
    AlternativeResponse
)

from app.core.dependencies import get_current_user


router = APIRouter(
    tags=["Alternatives"]
)


# =========================================================
# 1. CREATE ALTERNATIVE
# POST /decisions/{decision_id}/alternatives
# =========================================================

@router.post(
    "/decisions/{decision_id}/alternatives",
    response_model=AlternativeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_alternative(
    decision_id: int,
    alternative_data: AlternativeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check whether the decision exists
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

    # Create alternative
    new_alternative = Alternative(
        decision_id=decision_id,
        name=alternative_data.name,
        description=alternative_data.description,
        pros=alternative_data.pros,
        cons=alternative_data.cons,
        estimated_cost=alternative_data.estimated_cost,
        feasibility_score=alternative_data.feasibility_score,
        risk_level=alternative_data.risk_level
    )

    db.add(new_alternative)
    db.commit()
    db.refresh(new_alternative)

    return new_alternative


# =========================================================
# 2. GET ALL ALTERNATIVES FOR A DECISION
# GET /decisions/{decision_id}/alternatives
# =========================================================

@router.get(
    "/decisions/{decision_id}/alternatives",
    response_model=List[AlternativeResponse]
)
def get_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check whether the decision exists
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

    # Get all alternatives
    alternatives = (
        db.query(Alternative)
        .filter(
            Alternative.decision_id == decision_id
        )
        .all()
    )

    return alternatives


# =========================================================
# 3. GET ALTERNATIVE BY ID
# GET /alternatives/{alternative_id}
# =========================================================

@router.get(
    "/alternatives/{alternative_id}",
    response_model=AlternativeResponse
)
def get_alternative(
    alternative_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alternative = (
        db.query(Alternative)
        .filter(Alternative.id == alternative_id)
        .first()
    )

    if not alternative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found"
        )

    return alternative


# =========================================================
# 4. UPDATE ALTERNATIVE
# PUT /alternatives/{alternative_id}
# =========================================================

@router.put(
    "/alternatives/{alternative_id}",
    response_model=AlternativeResponse
)
def update_alternative(
    alternative_id: int,
    alternative_data: AlternativeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alternative = (
        db.query(Alternative)
        .filter(Alternative.id == alternative_id)
        .first()
    )

    if not alternative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found"
        )

    # Only update fields allowed by AlternativeUpdate
    update_data = alternative_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(alternative, field, value)

    db.commit()
    db.refresh(alternative)

    return alternative


# =========================================================
# 5. COMPARE ALTERNATIVES
# GET /decisions/{decision_id}/alternatives/compare
# =========================================================

@router.get(
    "/decisions/{decision_id}/alternatives/compare"
)
def compare_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check whether the decision exists
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

    alternatives = (
        db.query(Alternative)
        .filter(
            Alternative.decision_id == decision_id
        )
        .all()
    )

    return {
        "decision_id": decision_id,
        "alternatives": [
            {
                "name": alternative.name,
                "estimated_cost": alternative.estimated_cost,
                "feasibility_score": alternative.feasibility_score,
                "risk_level": alternative.risk_level
            }
            for alternative in alternatives
        ]
    }