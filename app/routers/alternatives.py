from enum import Enum
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.alternative import Alternative
from app.models.decision import Decision
from app.models.user import User
from app.schemas.alternative import (
    AlternativeComparisonResponse,
    AlternativeCreate,
    AlternativeResponse,
    AlternativeUpdate,
)

from app.services.activity_logger import log_activity

router = APIRouter(tags=["Alternatives"])


@router.post(
    "/decisions/{decision_id}/alternatives",
    response_model=AlternativeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new alternative for a decision"
)
def create_alternative(
    decision_id: int,
    alternative_in: AlternativeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify decision exists
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    risk_value = alternative_in.risk_level.value if isinstance(alternative_in.risk_level, Enum) else alternative_in.risk_level

    new_alternative = Alternative(
        decision_id=decision_id,
        name=alternative_in.name,
        description=alternative_in.description,
        pros=alternative_in.pros,
        cons=alternative_in.cons,
        estimated_cost=alternative_in.estimated_cost,
        feasibility_score=alternative_in.feasibility_score,
        risk_level=risk_value
    )
    db.add(new_alternative)
    db.commit()
    db.refresh(new_alternative)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="create_alternative",
        entity_type="alternative",
        entity_id=new_alternative.id,
        description=f"User {current_user.full_name} added alternative '{new_alternative.name}' to decision '{decision.title}'"
    )

    return new_alternative


@router.get(
    "/decisions/{decision_id}/alternatives/compare",
    response_model=AlternativeComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare all alternatives for a decision"
)
def compare_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify decision exists
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    alternatives = db.query(Alternative).filter(Alternative.decision_id == decision_id).all()
    return AlternativeComparisonResponse(
        decision_id=decision_id,
        alternatives=alternatives
    )


@router.get(
    "/decisions/{decision_id}/alternatives",
    response_model=List[AlternativeResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all alternatives for a decision"
)
def get_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify decision exists
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    alternatives = db.query(Alternative).filter(Alternative.decision_id == decision_id).all()
    return alternatives


@router.get(
    "/alternatives/{alternative_id}",
    response_model=AlternativeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single alternative by ID"
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


@router.put(
    "/alternatives/{alternative_id}",
    response_model=AlternativeResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing alternative"
)
def update_alternative(
    alternative_id: int,
    alternative_in: AlternativeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alternative = db.query(Alternative).filter(Alternative.id == alternative_id).first()
    if not alternative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found"
        )

    if alternative_in.name is not None:
        alternative.name = alternative_in.name
    if alternative_in.description is not None:
        alternative.description = alternative_in.description
    if alternative_in.pros is not None:
        alternative.pros = alternative_in.pros
    if alternative_in.cons is not None:
        alternative.cons = alternative_in.cons
    if alternative_in.estimated_cost is not None:
        alternative.estimated_cost = alternative_in.estimated_cost
    if alternative_in.feasibility_score is not None:
        alternative.feasibility_score = alternative_in.feasibility_score
    if alternative_in.risk_level is not None:
        risk_value = alternative_in.risk_level.value if isinstance(alternative_in.risk_level, Enum) else alternative_in.risk_level
        alternative.risk_level = risk_value

    db.commit()
    db.refresh(alternative)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="update_alternative",
        entity_type="alternative",
        entity_id=alternative.id,
        description=f"User {current_user.full_name} updated alternative '{alternative.name}'"
    )

    return alternative
