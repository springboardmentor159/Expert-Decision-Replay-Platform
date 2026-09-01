from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.models.alternative import Alternative
from app.schemas.alternative import (
    AlternativeCreate,
    AlternativeResponse,
    AlternativeUpdate,
    AlternativeComparisonResponse
)
from app.routers.auth import get_current_user


router = APIRouter(
    tags=["Alternatives"]
)


# =========================================================
# CREATE ALTERNATIVE
# =========================================================

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

    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

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

    return new_alternative


# =========================================================
# GET ALL ALTERNATIVES FOR A DECISION
# =========================================================

@router.get(
    "/decisions/{decision_id}/alternatives",
    response_model=list[AlternativeResponse]
)
def get_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    alternatives = db.query(Alternative).filter(
        Alternative.decision_id == decision_id
    ).all()

    return alternatives


# =========================================================
# GET ONE ALTERNATIVE
# =========================================================

@router.get(
    "/alternatives/{alternative_id}",
    response_model=AlternativeResponse
)
def get_alternative(
    alternative_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    alternative = db.query(Alternative).filter(
        Alternative.id == alternative_id
    ).first()

    if not alternative:
        raise HTTPException(
            status_code=404,
            detail="Alternative not found"
        )

    return alternative


# =========================================================
# UPDATE ALTERNATIVE
# =========================================================

@router.put(
    "/alternatives/{alternative_id}",
    response_model=AlternativeResponse
)
def update_alternative(
    alternative_id: int,
    alternative_data: AlternativeUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    alternative = db.query(Alternative).filter(
        Alternative.id == alternative_id
    ).first()

    if not alternative:
        raise HTTPException(
            status_code=404,
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

    db.commit()
    db.refresh(alternative)

    return alternative

# =========================================================
# DELETE ALTERNATIVE
# =========================================================

@router.delete(
    "/alternatives/{alternative_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_alternative(
    alternative_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    alternative = db.query(Alternative).filter(
        Alternative.id == alternative_id
    ).first()

    if not alternative:
        raise HTTPException(
            status_code=404,
            detail="Alternative not found"
        )

    db.delete(alternative)
    db.commit()

    return None
# =========================================================
# COMPARE ALTERNATIVES
# =========================================================

@router.get(
    "/decisions/{decision_id}/alternatives/compare",
    response_model=AlternativeComparisonResponse
)
def compare_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    alternatives = db.query(Alternative).filter(
        Alternative.decision_id == decision_id
    ).all()

    if not alternatives:
        raise HTTPException(
            status_code=404,
            detail="No alternatives found for this decision"
        )

    comparison = []

    for alternative in alternatives:
        comparison.append({
            "alternative_id": alternative.id,
            "name": alternative.name,
            "estimated_cost": alternative.estimated_cost,
            "feasibility_score": alternative.feasibility_score,
            "risk_level": alternative.risk_level
        })

    return {
        "decision_id": decision_id,
        "alternatives": comparison
    }