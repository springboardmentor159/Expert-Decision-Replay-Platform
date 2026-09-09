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

from app.services.activity_log import create_activity_log
from app.services.audit_log import create_audit_log
from app.services.access_log import create_access_log

from app.models.audit_action import AuditAction
from app.models.audit_entity import AuditEntityType


router = APIRouter(
    tags=["Alternatives"]
)


# ==========================================
# CREATE ALTERNATIVE FOR A DECISION
# ==========================================
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
        name=alternative.name,
        description=alternative.description,
        pros=alternative.pros,
        cons=alternative.cons,
        estimated_cost=alternative.estimated_cost,
        feasibility_score=alternative.feasibility_score,
        risk_level=alternative.risk_level
    )

    db.add(new_alternative)
    db.flush()

    # ==========================================
    # CREATE ACTIVITY LOG
    # ==========================================

    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="created",
        entity_type="alternative",
        entity_id=new_alternative.id,
        description=(
            f"Created alternative: {new_alternative.name} "
            f"for decision: {decision.title}"
        )
    )

    # ==========================================
    # CREATE AUDIT LOG
    # ==========================================

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type=AuditEntityType.ALTERNATIVE,
        entity_id=new_alternative.id,
        description=(
            f"Created alternative: {new_alternative.name} "
            f"for decision: {decision.title}"
        ),
        new_value={
            "name": new_alternative.name,
            "description": new_alternative.description,
            "pros": new_alternative.pros,
            "cons": new_alternative.cons,
            "estimated_cost": new_alternative.estimated_cost,
            "feasibility_score": new_alternative.feasibility_score,
            "risk_level": new_alternative.risk_level,
            "decision_id": decision_id
        },
        request_method="POST",
        endpoint=f"/decisions/{decision_id}/alternatives"
    )

    db.commit()
    db.refresh(new_alternative)

    return new_alternative


# ==========================================
# GET ALL ALTERNATIVES FOR A DECISION
# ==========================================
@router.get(
    "/decisions/{decision_id}/alternatives",
    response_model=List[AlternativeResponse]
)
def get_alternatives_for_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
        .filter(
            Alternative.decision_id == decision_id
        )
        .all()
    )

    # ==========================================
    # CREATE ACCESS LOG
    # ==========================================

    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Alternative",
        resource_id=decision_id,
        action="LIST"
    )

    db.commit()

    return alternatives


# ==========================================
# COMPARE ALTERNATIVES FOR A DECISION
# ==========================================
@router.get(
    "/decisions/{decision_id}/alternatives/compare",
    response_model=AlternativeCompareResponse
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

    # ==========================================
    # CREATE ACCESS LOG
    # ==========================================

    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Alternative",
        resource_id=decision_id,
        action="COMPARE"
    )

    db.commit()

    return {
        "decision_id": decision_id,
        "alternatives": alternatives
    }


# ==========================================
# GET ALTERNATIVE BY ID
# ==========================================
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

    # ==========================================
    # CREATE ACCESS LOG
    # ==========================================

    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Alternative",
        resource_id=alternative.id,
        action="VIEW"
    )

    db.commit()

    return alternative


# ==========================================
# UPDATE ALTERNATIVE
# ==========================================
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

    # ==========================================
    # SAVE OLD VALUES FOR AUDIT
    # ==========================================

    old_value = {
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
    alternative.risk_level = alternative_data.risk_level

    # ==========================================
    # CREATE ACTIVITY LOG
    # ==========================================

    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="updated",
        entity_type="alternative",
        entity_id=alternative.id,
        description=(
            f"Updated alternative: {alternative.name}"
        )
    )

    # ==========================================
    # CREATE AUDIT LOG
    # ==========================================

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type=AuditEntityType.ALTERNATIVE,
        entity_id=alternative.id,
        description=(
            f"Updated alternative: {alternative.name}"
        ),
        old_value=old_value,
        new_value={
            "name": alternative.name,
            "description": alternative.description,
            "pros": alternative.pros,
            "cons": alternative.cons,
            "estimated_cost": alternative.estimated_cost,
            "feasibility_score": alternative.feasibility_score,
            "risk_level": alternative.risk_level
        },
        request_method="PUT",
        endpoint=f"/alternatives/{alternative_id}"
    )

    # ==========================================
    # CREATE ACCESS LOG
    # ==========================================

    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Alternative",
        resource_id=alternative.id,
        action="UPDATE"
    )

    db.commit()
    db.refresh(alternative)

    return alternative