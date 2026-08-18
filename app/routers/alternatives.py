from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.models.alternative import Alternative
from app.models.user import User
from app.schemas.alternative import (
    AlternativeCreate,
    AlternativeUpdate,
    AlternativeResponse,
    AlternativeCompareResponse,
)
from app.core.security import get_current_user

router = APIRouter(tags=["Alternatives"])


# CREATE ALTERNATIVE FOR A DECISION
@router.post(
    "/decisions/{decision_id}/alternatives",
    response_model=AlternativeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_alternative(
    decision_id: int,
    alternative: AlternativeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    new_alternative = Alternative(
        decision_id=decision_id,
        name=alternative.name,
        description=alternative.description,
        pros=alternative.pros,
        cons=alternative.cons,
        estimated_cost=alternative.estimated_cost,
        feasibility_score=alternative.feasibility_score,
        risk_level=alternative.risk_level
    )

    db.add(new_alternative)
    db.commit()
    db.refresh(new_alternative)

    return new_alternative


# GET ALL ALTERNATIVES FOR A DECISION
@router.get(
    "/decisions/{decision_id}/alternatives",
    response_model=List[AlternativeResponse]
)
def get_alternatives_for_decision(
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

    return db.query(Alternative).filter(Alternative.decision_id == decision_id).all()


# COMPARE ALTERNATIVES FOR A DECISION
@router.get(
    "/decisions/{decision_id}/alternatives/compare",
    response_model=AlternativeCompareResponse
)
def compare_alternatives(
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

    alternatives = db.query(Alternative).filter(Alternative.decision_id == decision_id).all()

    return {
        "decision_id": decision_id,
        "alternatives": alternatives
    }


# GET ALTERNATIVE BY ID
@router.get(
    "/alternatives/{alternative_id}",
    response_model=AlternativeResponse
)
def get_alternative(
    alternative_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alternative = db.query(Alternative).filter(Alternative.id == alternative_id).first()
    if not alternative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found"
        )

    return alternative


# UPDATE ALTERNATIVE
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
    alternative = db.query(Alternative).filter(Alternative.id == alternative_id).first()
    if not alternative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found"
        )

    alternative.name = alternative_data.name
    alternative.description = alternative_data.description
    alternative.pros = alternative_data.pros
    alternative.cons = alternative_data.cons
    alternative.estimated_cost = alternative_data.estimated_cost
    alternative.feasibility_score = alternative_data.feasibility_score
    alternative.risk_level = alternative_data.risk_level

    db.commit()
    db.refresh(alternative)

    return alternative