from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.alternative import Alternative
from app.models.decision import Decision
from app.models.user import User
from app.services.activity import log_activity
from app.schemas.alternative import (
    AlternativeCompareResponse,
    AlternativeCreate,
    AlternativeResponse,
    AlternativeUpdate,
)

router = APIRouter(
    prefix="/decisions",
    tags=["Alternatives"]
)

alternatives_router = APIRouter(
    prefix="/alternatives",
    tags=["Alternatives"]
)


def _get_decision_or_404(db: Session, decision_id: int) -> Decision:
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )
    return decision


@router.post(
    "/{decision_id}/alternatives",
    response_model=AlternativeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_alternative(
    decision_id: int,
    alternative_data: AlternativeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _get_decision_or_404(db, decision_id)

    new_alternative = Alternative(
        decision_id=decision_id,
        name=alternative_data.name,
        description=alternative_data.description,
        pros=alternative_data.pros,
        cons=alternative_data.cons,
        estimated_cost=alternative_data.estimated_cost,
        feasibility_score=alternative_data.feasibility_score,
        risk_level=alternative_data.risk_level,
    )

    db.add(new_alternative)
    db.commit()
    db.refresh(new_alternative)

    log_activity(
        db,
        current_user.id,
        "create",
        "alternative",
        new_alternative.id,
        f"Created alternative '{new_alternative.name}' for decision {decision_id}",
    )

    return new_alternative


@router.get(
    "/{decision_id}/alternatives/compare",
    response_model=AlternativeCompareResponse
)
def compare_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _get_decision_or_404(db, decision_id)

    alternatives = db.query(Alternative).filter(
        Alternative.decision_id == decision_id
    ).all()

    return {
        "decision_id": decision_id,
        "alternatives": alternatives
    }


@router.get(
    "/{decision_id}/alternatives",
    response_model=List[AlternativeResponse]
)
def get_alternatives_by_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _get_decision_or_404(db, decision_id)

    alternatives = db.query(Alternative).filter(
        Alternative.decision_id == decision_id
    ).all()

    return alternatives


@alternatives_router.get(
    "/{alternative_id}",
    response_model=AlternativeResponse
)
def get_alternative(
    alternative_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alternative = db.query(Alternative).filter(
        Alternative.id == alternative_id
    ).first()

    if not alternative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found"
        )

    return alternative


@alternatives_router.put(
    "/{alternative_id}",
    response_model=AlternativeResponse
)
def update_alternative(
    alternative_id: int,
    alternative_data: AlternativeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alternative = db.query(Alternative).filter(
        Alternative.id == alternative_id
    ).first()

    if not alternative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found"
        )

    if alternative_data.name is not None:
        alternative.name = alternative_data.name

    if alternative_data.description is not None:
        alternative.description = alternative_data.description

    if alternative_data.pros is not None:
        alternative.pros = alternative_data.pros

    if alternative_data.cons is not None:
        alternative.cons = alternative_data.cons

    if alternative_data.estimated_cost is not None:
        alternative.estimated_cost = alternative_data.estimated_cost

    if alternative_data.feasibility_score is not None:
        alternative.feasibility_score = alternative_data.feasibility_score

    if alternative_data.risk_level is not None:
        alternative.risk_level = alternative_data.risk_level

    alternative.updated_at = func.now()

    db.commit()
    db.refresh(alternative)

    log_activity(
        db,
        current_user.id,
        "update",
        "alternative",
        alternative.id,
        f"Updated alternative '{alternative.name}'",
    )

    return alternative