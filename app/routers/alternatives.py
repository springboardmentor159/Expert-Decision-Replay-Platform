from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.alternative import Alternative
from app.models.decision import Decision
from app.models.user import User
from app.schemas.alternative import (
    AlternativeCreate,
    AlternativeResponse,
    AlternativeUpdate,
)
from app.schemas.audit_log import AuditAction, AuditEntityType
from app.services.audit_service import log_audit


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

    alternative = Alternative(
        decision_id=decision_id,
        name=alternative_data.name,
        description=alternative_data.description,
        pros=alternative_data.pros,
        cons=alternative_data.cons,
        estimated_cost=alternative_data.estimated_cost,
        feasibility_score=alternative_data.feasibility_score,
        risk_level=alternative_data.risk_level.value
    )

    db.add(alternative)
    db.flush()

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type=AuditEntityType.ALTERNATIVE,
        entity_id=alternative.id,
        description=(
            f"User {current_user.id} created "
            f"Alternative {alternative.id} "
            f"for Decision {decision_id}"
        ),
        new_value={
            "name": alternative.name,
            "description": alternative.description,
            "pros": alternative.pros,
            "cons": alternative.cons,
            "estimated_cost": alternative.estimated_cost,
            "feasibility_score": alternative.feasibility_score,
            "risk_level": alternative.risk_level
        },
        request_method="POST",
        endpoint=f"/decisions/{decision_id}/alternatives"
    )

    db.commit()
    db.refresh(alternative)

    return alternative


# GET ALL ALTERNATIVES FOR A DECISION
@router.get(
    "/decisions/{decision_id}/alternatives",
    response_model=List[AlternativeResponse]
)
def get_alternatives(
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

    return (
        db.query(Alternative)
        .filter(
            Alternative.decision_id == decision_id
        )
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
    alternative = db.query(Alternative).filter(
        Alternative.id == alternative_id
    ).first()

    if not alternative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found"
        )

    old_values = {
        "name": alternative.name,
        "description": alternative.description,
        "pros": alternative.pros,
        "cons": alternative.cons,
        "estimated_cost": alternative.estimated_cost,
        "feasibility_score": alternative.feasibility_score,
        "risk_level": alternative.risk_level
    }

    alternative.name = alternative_data.name
    alternative.description = alternative_data.description
    alternative.pros = alternative_data.pros
    alternative.cons = alternative_data.cons
    alternative.estimated_cost = alternative_data.estimated_cost
    alternative.feasibility_score = alternative_data.feasibility_score
    alternative.risk_level = alternative_data.risk_level.value

    new_values = {
        "name": alternative.name,
        "description": alternative.description,
        "pros": alternative.pros,
        "cons": alternative.cons,
        "estimated_cost": alternative.estimated_cost,
        "feasibility_score": alternative.feasibility_score,
        "risk_level": alternative.risk_level
    }

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type=AuditEntityType.ALTERNATIVE,
        entity_id=alternative.id,
        description=(
            f"User {current_user.id} updated "
            f"Alternative {alternative.id}"
        ),
        old_value=old_values,
        new_value=new_values,
        request_method="PUT",
        endpoint=f"/alternatives/{alternative.id}"
    )

    db.commit()
    db.refresh(alternative)

    return alternative


# COMPARE ALTERNATIVES
@router.get(
    "/decisions/{decision_id}/alternatives/compare"
)
def compare_alternatives(
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

    alternatives = db.query(Alternative).filter(
        Alternative.decision_id == decision_id
    ).all()

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