from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.alternative import Alternative
from app.schemas.alternative import (
    AlternativeResponse,
    AlternativeUpdate,
)
from app.core.dependencies import get_current_user
from app.services.activity_log_service import create_activity_log


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

    # Update alternative fields
    alternative.name = alternative_data.name
    alternative.description = alternative_data.description
    alternative.pros = alternative_data.pros
    alternative.cons = alternative_data.cons
    alternative.estimated_cost = alternative_data.estimated_cost
    alternative.feasibility_score = alternative_data.feasibility_score
    alternative.risk_level = alternative_data.risk_level.value

    db.commit()
    db.refresh(alternative)

    # Get authenticated user ID
    user_id = int(current_user["sub"])

    # Create activity log
    create_activity_log(
        db=db,
        user_id=user_id,
        action="UPDATE",
        entity_type="Alternative",
        entity_id=alternative.id,
        description=f"Updated alternative: {alternative.name}",
    )

    return alternative