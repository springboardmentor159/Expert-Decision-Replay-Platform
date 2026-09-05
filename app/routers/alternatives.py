
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.alternative import Alternative
from app.schemas.alternative import (
    AlternativeResponse,
    AlternativeUpdate,
)
from app.core.dependencies import get_current_user
from app.services.activity_log_service import create_activity_log
from app.services.audit_log_service import create_audit_log


router = APIRouter(
    prefix="/alternatives",
    tags=["Alternatives"],
    dependencies=[Depends(get_current_user)]
)


# ---------------------------------------------------------
# GET ALTERNATIVE BY ID
# ---------------------------------------------------------

@router.get(
    "/{alternative_id}",
    response_model=AlternativeResponse
)
def get_alternative(
    alternative_id: int,
    db: Session = Depends(get_db)
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


# ---------------------------------------------------------
# UPDATE ALTERNATIVE
# ---------------------------------------------------------

@router.put(
    "/{alternative_id}",
    response_model=AlternativeResponse
)
def update_alternative(
    alternative_id: int,
    alternative_data: AlternativeUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
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

    user_id = int(current_user["sub"])

    # Capture old values before updating
    old_value = {
        "name": alternative.name,
        "description": alternative.description,
        "pros": alternative.pros,
        "cons": alternative.cons,
        "estimated_cost": alternative.estimated_cost,
        "feasibility_score": alternative.feasibility_score,
        "risk_level": alternative.risk_level,
    }

    # Update alternative fields
    alternative.name = alternative_data.name
    alternative.description = alternative_data.description
    alternative.pros = alternative_data.pros
    alternative.cons = alternative_data.cons
    alternative.estimated_cost = alternative_data.estimated_cost
    alternative.feasibility_score = alternative_data.feasibility_score
    alternative.risk_level = alternative_data.risk_level.value

    db.flush()

    # Capture new values
    new_value = {
        "name": alternative.name,
        "description": alternative.description,
        "pros": alternative.pros,
        "cons": alternative.cons,
        "estimated_cost": alternative.estimated_cost,
        "feasibility_score": alternative.feasibility_score,
        "risk_level": alternative.risk_level,
    }

    # Audit: alternative update
    create_audit_log(
        db=db,
        user_id=user_id,
        action="UPDATE",
        entity_type="Alternative",
        entity_id=alternative.id,
        description=f"Updated alternative: {alternative.name}",
        old_value=old_value,
        new_value=new_value,
        ip_address=request.client.host if request.client else None,
        request_method=request.method,
        endpoint=request.url.path,
    )

    # Activity log
    create_activity_log(
        db=db,
        user_id=user_id,
        action="UPDATE",
        entity_type="Alternative",
        entity_id=alternative.id,
        description=f"Updated alternative: {alternative.name}",
    )

    db.commit()
    db.refresh(alternative)

    return alternative
