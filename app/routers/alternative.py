from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.alternative import Alternative
from app.models.decision import Decision
from app.schemas.alternative import (
    AlternativeCreate,
    AlternativeUpdate,
    AlternativeResponse,
)
from app.routers.users import get_current_user
from app.utils.activity_logger import log_activity
from app.utils.audit_logger import log_audit


router = APIRouter(
    tags=["Alternatives"]
)


# CREATE ALTERNATIVE
@router.post(
    "/decisions/{decision_id}/alternatives",
    response_model=AlternativeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_alternative(
    decision_id: int,
    alternative_data: AlternativeCreate,
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
    db.flush()
    log_activity(db, int(current_user["sub"]), "alternative_created", "Alternative", new_alternative.id, f"Alternative {new_alternative.id} added")
    log_audit(db, int(current_user["sub"]), "CREATE", "Alternative", new_alternative.id, f"Alternative {new_alternative.id} added")
    db.commit()
    db.refresh(new_alternative)

    return new_alternative


# GET ALL ALTERNATIVES FOR A DECISION
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return (
        db.query(Alternative)
        .filter(Alternative.decision_id == decision_id)
        .all()
    )


# GET ALTERNATIVE BY ID
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
    current_user=Depends(get_current_user)
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

    alternative.name = alternative_data.name
    alternative.description = alternative_data.description
    alternative.pros = alternative_data.pros
    alternative.cons = alternative_data.cons
    alternative.estimated_cost = alternative_data.estimated_cost
    alternative.feasibility_score = alternative_data.feasibility_score
    alternative.risk_level = alternative_data.risk_level.value

    log_activity(db, int(current_user["sub"]), "alternative_updated", "Alternative", alternative.id, f"Alternative {alternative.id} updated")
    log_audit(db, int(current_user["sub"]), "UPDATE", "Alternative", alternative.id, f"Alternative {alternative.id} updated")
    db.commit()
    db.refresh(alternative)

    return alternative


@router.delete(
    "/alternatives/{alternative_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_alternative(
    alternative_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    alternative = db.query(Alternative).filter(Alternative.id == alternative_id).first()
    if not alternative:
        raise HTTPException(status_code=404, detail="Alternative not found")
    log_activity(db, int(current_user["sub"]), "alternative_deleted", "Alternative", alternative.id, f"Alternative {alternative.id} deleted")
    log_audit(db, int(current_user["sub"]), "DELETE", "Alternative", alternative.id, f"Alternative {alternative.id} deleted")
    db.delete(alternative)
    db.commit()


# COMPARE ALTERNATIVES
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