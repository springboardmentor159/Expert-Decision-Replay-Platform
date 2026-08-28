from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.alternative import Alternative
from app.models.decision import Decision
from app.models.activity import Activity
from app.schemas.alternative import (
    AlternativeCreate,
    AlternativeResponse
)
from app.core.security import get_current_user


router = APIRouter(
    tags=["Alternatives"]
)


# ============================================================
# CREATE ALTERNATIVE
# POST /decisions/{decision_id}/alternatives
# ============================================================

@router.post(
    "/decisions/{decision_id}/alternatives",
    response_model=AlternativeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_alternative(
    decision_id: int,
    alternative: AlternativeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
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

    # Activity log
    activity = Activity(
        user_id=current_user.id,
        action="Alternative Created",
        entity_type="Alternative",
        entity_id=new_alternative.id,
        description=(
            f"User {current_user.id} created "
            f"Alternative {new_alternative.id} "
            f"for Decision {decision_id}"
        )
    )

    db.add(activity)
    db.commit()

    return new_alternative


# ============================================================
# GET ALL ALTERNATIVES FOR A DECISION
# GET /decisions/{decision_id}/alternatives
# ============================================================

@router.get(
    "/decisions/{decision_id}/alternatives",
    response_model=List[AlternativeResponse]
)
def get_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    return (
        db.query(Alternative)
        .filter(Alternative.decision_id == decision_id)
        .all()
    )


# ============================================================
# GET ALTERNATIVE BY ID
# GET /alternatives/{alternative_id}
# ============================================================

@router.get(
    "/alternatives/{alternative_id}",
    response_model=AlternativeResponse
)
def get_alternative(
    alternative_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    alternative = (
        db.query(Alternative)
        .filter(Alternative.id == alternative_id)
        .first()
    )

    if not alternative:
        raise HTTPException(
            status_code=404,
            detail="Alternative not found"
        )

    return alternative


# ============================================================
# UPDATE ALTERNATIVE
# PUT /alternatives/{alternative_id}
# ============================================================

@router.put(
    "/alternatives/{alternative_id}",
    response_model=AlternativeResponse
)
def update_alternative(
    alternative_id: int,
    alternative_data: AlternativeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    alternative = (
        db.query(Alternative)
        .filter(Alternative.id == alternative_id)
        .first()
    )

    if not alternative:
        raise HTTPException(
            status_code=404,
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

    # Activity log
    activity = Activity(
        user_id=current_user.id,
        action="Alternative Updated",
        entity_type="Alternative",
        entity_id=alternative.id,
        description=(
            f"User {current_user.id} updated "
            f"Alternative {alternative.id}"
        )
    )

    db.add(activity)
    db.commit()

    return alternative


# ============================================================
# COMPARE ALTERNATIVES
# GET /decisions/{decision_id}/alternatives/compare
# ============================================================

@router.get(
    "/decisions/{decision_id}/alternatives/compare"
)
def compare_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
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