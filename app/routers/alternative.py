from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.alternative import Alternative
from app.models.decision import Decision
from app.models.user import User
from app.schemas.alternative import AlternativeCreate, AlternativeResponse


router = APIRouter(
    tags=["Alternatives"]
)


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

    new_alternative = Alternative(
        decision_id=decision_id,
        name=alternative_data.name,
        description=alternative_data.description,
        pros=alternative_data.pros,
        cons=alternative_data.cons,
        estimated_cost=alternative_data.estimated_cost,
        feasibility_score=alternative_data.feasibility_score,
        risk_level=alternative_data.risk_level.value
    )

    db.add(new_alternative)
    db.commit()
    db.refresh(new_alternative)

    return new_alternative


@router.get(
    "/decisions/{decision_id}/alternatives",
    response_model=List[AlternativeResponse]
)
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

    if alternative is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found"
        )

    return alternative


@router.put(
    "/alternatives/{alternative_id}",
    response_model=AlternativeResponse
)
def update_alternative(
    alternative_id: int,
    alternative_data: AlternativeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alternative = (
        db.query(Alternative)
        .filter(Alternative.id == alternative_id)
        .first()
    )

    if alternative is None:
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
    alternative.risk_level = alternative_data.risk_level.value

    db.commit()
    db.refresh(alternative)

    return alternative


@router.get(
    "/decisions/{decision_id}/alternatives/compare"
)
def compare_alternatives(
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

    alternatives = (
        db.query(Alternative)
        .filter(Alternative.decision_id == decision_id)
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
@router.delete(
    "/alternatives/{alternative_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_alternative(
    alternative_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alternative = (
        db.query(Alternative)
        .filter(Alternative.id == alternative_id)
        .first()
    )

    if alternative is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found"
        )

    db.delete(alternative)
    db.commit()

    return None