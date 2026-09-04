from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.decision import Decision
from app.models.alternative import Alternative
from app.services.activity import create_activity
from app.services.audit import create_audit_log
from app.schemas.alternative import (
    AlternativeCreate,
    AlternativeUpdate,
    AlternativeResponse,
)


router = APIRouter(
    tags=["Alternatives"],
)


# ============================================================
# CREATE ALTERNATIVE
# ============================================================

@router.post(
    "/decisions/{decision_id}/alternatives",
    response_model=AlternativeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_alternative(
    decision_id: int,
    alternative_data: AlternativeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

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
    db.flush()

    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Alternative",
        entity_id=new_alternative.id,
        description=(
            f"User {current_user.id} created "
            f"Alternative {new_alternative.id}"
        ),
        new_value={
            "decision_id": decision_id,
            "name": new_alternative.name,
            "description": new_alternative.description,
            "pros": new_alternative.pros,
            "cons": new_alternative.cons,
            "estimated_cost": new_alternative.estimated_cost,
            "feasibility_score": new_alternative.feasibility_score,
            "risk_level": new_alternative.risk_level,
        },
        request_method="POST",
        endpoint=f"/decisions/{decision_id}/alternatives",
    )

    # Activity log
    create_activity(
        db=db,
        user_id=current_user.id,
        action="Alternative created",
        entity_type="Alternative",
        entity_id=new_alternative.id,
        description=(
            f"Alternative '{new_alternative.name}' was created."
        ),
    )

    db.commit()
    db.refresh(new_alternative)

    return new_alternative


# ============================================================
# GET ALL ALTERNATIVES
# ============================================================

@router.get(
    "/decisions/{decision_id}/alternatives",
    response_model=List[AlternativeResponse],
)
def get_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return (
        db.query(Alternative)
        .filter(Alternative.decision_id == decision_id)
        .all()
    )


# ============================================================
# GET ALTERNATIVE BY ID
# ============================================================

@router.get(
    "/alternatives/{alternative_id}",
    response_model=AlternativeResponse,
)
def get_alternative(
    alternative_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alternative = (
        db.query(Alternative)
        .filter(Alternative.id == alternative_id)
        .first()
    )

    if not alternative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found",
        )

    return alternative


# ============================================================
# UPDATE ALTERNATIVE
# ============================================================

@router.put(
    "/alternatives/{alternative_id}",
    response_model=AlternativeResponse,
)
def update_alternative(
    alternative_id: int,
    alternative_data: AlternativeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alternative = (
        db.query(Alternative)
        .filter(Alternative.id == alternative_id)
        .first()
    )

    if not alternative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found",
        )

    # Capture old values
    old_value = {
        "decision_id": alternative.decision_id,
        "name": alternative.name,
        "description": alternative.description,
        "pros": alternative.pros,
        "cons": alternative.cons,
        "estimated_cost": alternative.estimated_cost,
        "feasibility_score": alternative.feasibility_score,
        "risk_level": alternative.risk_level,
    }

    # Update
    alternative.name = alternative_data.name
    alternative.description = alternative_data.description
    alternative.pros = alternative_data.pros
    alternative.cons = alternative_data.cons
    alternative.estimated_cost = alternative_data.estimated_cost
    alternative.feasibility_score = alternative_data.feasibility_score
    alternative.risk_level = alternative_data.risk_level

    db.flush()

    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Alternative",
        entity_id=alternative.id,
        description=(
            f"User {current_user.id} updated "
            f"Alternative {alternative.id}"
        ),
        old_value=old_value,
        new_value={
            "decision_id": alternative.decision_id,
            "name": alternative.name,
            "description": alternative.description,
            "pros": alternative.pros,
            "cons": alternative.cons,
            "estimated_cost": alternative.estimated_cost,
            "feasibility_score": alternative.feasibility_score,
            "risk_level": alternative.risk_level,
        },
        request_method="PUT",
        endpoint=f"/alternatives/{alternative.id}",
    )

    # Activity log
    create_activity(
        db=db,
        user_id=current_user.id,
        action="Alternative updated",
        entity_type="Alternative",
        entity_id=alternative.id,
        description=(
            f"Alternative '{alternative.name}' was updated."
        ),
    )

    db.commit()
    db.refresh(alternative)

    return alternative


# ============================================================
# DELETE ALTERNATIVE
# ============================================================

@router.delete(
    "/alternatives/{alternative_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_alternative(
    alternative_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alternative = (
        db.query(Alternative)
        .filter(Alternative.id == alternative_id)
        .first()
    )

    if not alternative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found",
        )

    # Capture old values before deletion
    old_value = {
        "decision_id": alternative.decision_id,
        "name": alternative.name,
        "description": alternative.description,
        "pros": alternative.pros,
        "cons": alternative.cons,
        "estimated_cost": alternative.estimated_cost,
        "feasibility_score": alternative.feasibility_score,
        "risk_level": alternative.risk_level,
    }

    # Audit log BEFORE deletion
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="Alternative",
        entity_id=alternative.id,
        description=(
            f"User {current_user.id} deleted "
            f"Alternative {alternative.id}"
        ),
        old_value=old_value,
        request_method="DELETE",
        endpoint=f"/alternatives/{alternative.id}",
    )

    # Activity log
    create_activity(
        db=db,
        user_id=current_user.id,
        action="Alternative deleted",
        entity_type="Alternative",
        entity_id=alternative.id,
        description=(
            f"Alternative '{alternative.name}' was deleted."
        ),
    )

    db.delete(alternative)
    db.commit()

    return None


# ============================================================
# COMPARE ALTERNATIVES
# ============================================================

@router.get(
    "/decisions/{decision_id}/alternatives/compare",
)
def compare_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
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
                "risk_level": alternative.risk_level,
            }
            for alternative in alternatives
        ],
    }