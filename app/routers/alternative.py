from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.alternative import Alternative
from app.models.decision import Decision
from app.schemas.alternative import (
    AlternativeCreate,
    AlternativeResponse,
)
from app.core.security import get_current_user
from app.services.activity import create_activity_log
from app.services.audit import create_audit_log


router = APIRouter(
    tags=["Alternatives"],
)


# ---------------------------------------------------------
# CREATE ALTERNATIVE
# ---------------------------------------------------------
@router.post(
    "/decisions/{decision_id}/alternatives",
    response_model=AlternativeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_alternative(
    decision_id: int,
    alternative: AlternativeCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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
        name=alternative.name,
        description=alternative.description,
        pros=alternative.pros,
        cons=alternative.cons,
        estimated_cost=alternative.estimated_cost,
        feasibility_score=alternative.feasibility_score,
        risk_level=alternative.risk_level,
    )

    db.add(new_alternative)
    db.flush()

    # Sprint 10 activity log
    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="created",
        entity_type="Alternative",
        entity_id=new_alternative.id,
        description=(
            f"User {current_user.id} added "
            f"Alternative {new_alternative.id} "
            f"to Decision {decision_id}"
        ),
    )

    # Sprint 11 audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Alternative",
        entity_id=new_alternative.id,
        decision_id=decision_id,
        description=(
            f"Alternative {new_alternative.id} created "
            f"for Decision {decision_id}"
        ),
        ip_address=request.client.host if request.client else None,
        new_value={
            "id": new_alternative.id,
            "decision_id": decision_id,
            "name": new_alternative.name,
            "description": new_alternative.description,
            "pros": new_alternative.pros,
            "cons": new_alternative.cons,
            "estimated_cost": new_alternative.estimated_cost,
            "feasibility_score": new_alternative.feasibility_score,
            "risk_level": new_alternative.risk_level,
        },
        request_method=request.method,
        endpoint=request.url.path,
    )

    db.commit()
    db.refresh(new_alternative)

    return new_alternative


# ---------------------------------------------------------
# GET ALTERNATIVES FOR A DECISION
# ---------------------------------------------------------
@router.get(
    "/decisions/{decision_id}/alternatives",
    response_model=List[AlternativeResponse],
)
def get_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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


# ---------------------------------------------------------
# GET SINGLE ALTERNATIVE
# ---------------------------------------------------------
@router.get(
    "/alternatives/{alternative_id}",
    response_model=AlternativeResponse,
)
def get_alternative(
    alternative_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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


# ---------------------------------------------------------
# UPDATE ALTERNATIVE
# ---------------------------------------------------------
@router.put(
    "/alternatives/{alternative_id}",
    response_model=AlternativeResponse,
)
def update_alternative(
    alternative_id: int,
    alternative: AlternativeCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    existing_alternative = (
        db.query(Alternative)
        .filter(Alternative.id == alternative_id)
        .first()
    )

    if not existing_alternative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found",
        )

    decision_id = existing_alternative.decision_id

    old_value = {
        "id": existing_alternative.id,
        "decision_id": existing_alternative.decision_id,
        "name": existing_alternative.name,
        "description": existing_alternative.description,
        "pros": existing_alternative.pros,
        "cons": existing_alternative.cons,
        "estimated_cost": existing_alternative.estimated_cost,
        "feasibility_score": existing_alternative.feasibility_score,
        "risk_level": existing_alternative.risk_level,
    }

    existing_alternative.name = alternative.name
    existing_alternative.description = alternative.description
    existing_alternative.pros = alternative.pros
    existing_alternative.cons = alternative.cons
    existing_alternative.estimated_cost = alternative.estimated_cost
    existing_alternative.feasibility_score = alternative.feasibility_score
    existing_alternative.risk_level = alternative.risk_level

    db.flush()

    new_value = {
        "id": existing_alternative.id,
        "decision_id": existing_alternative.decision_id,
        "name": existing_alternative.name,
        "description": existing_alternative.description,
        "pros": existing_alternative.pros,
        "cons": existing_alternative.cons,
        "estimated_cost": existing_alternative.estimated_cost,
        "feasibility_score": existing_alternative.feasibility_score,
        "risk_level": existing_alternative.risk_level,
    }

    # Sprint 10 activity log
    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="updated",
        entity_type="Alternative",
        entity_id=existing_alternative.id,
        description=(
            f"User {current_user.id} updated "
            f"Alternative {existing_alternative.id}"
        ),
    )

    # Sprint 11 audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Alternative",
        entity_id=existing_alternative.id,
        decision_id=decision_id,
        description=(
            f"Alternative {existing_alternative.id} updated"
        ),
        ip_address=request.client.host if request.client else None,
        old_value=old_value,
        new_value=new_value,
        request_method=request.method,
        endpoint=request.url.path,
    )

    db.commit()
    db.refresh(existing_alternative)

    return existing_alternative


# ---------------------------------------------------------
# DELETE ALTERNATIVE
# ---------------------------------------------------------
@router.delete(
    "/alternatives/{alternative_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_alternative(
    alternative_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    existing_alternative = (
        db.query(Alternative)
        .filter(Alternative.id == alternative_id)
        .first()
    )

    if not existing_alternative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found",
        )

    decision_id = existing_alternative.decision_id

    old_value = {
        "id": existing_alternative.id,
        "decision_id": existing_alternative.decision_id,
        "name": existing_alternative.name,
        "description": existing_alternative.description,
        "pros": existing_alternative.pros,
        "cons": existing_alternative.cons,
        "estimated_cost": existing_alternative.estimated_cost,
        "feasibility_score": existing_alternative.feasibility_score,
        "risk_level": existing_alternative.risk_level,
    }

    # Sprint 10 activity log
    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="deleted",
        entity_type="Alternative",
        entity_id=existing_alternative.id,
        description=(
            f"User {current_user.id} deleted "
            f"Alternative {existing_alternative.id} "
            f"from Decision {decision_id}"
        ),
    )

    # Sprint 11 audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="Alternative",
        entity_id=existing_alternative.id,
        decision_id=decision_id,
        description=(
            f"Alternative {existing_alternative.id} deleted "
            f"from Decision {decision_id}"
        ),
        ip_address=request.client.host if request.client else None,
        old_value=old_value,
        request_method=request.method,
        endpoint=request.url.path,
    )

    db.delete(existing_alternative)
    db.commit()

    return None