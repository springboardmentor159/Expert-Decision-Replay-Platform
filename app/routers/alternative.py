from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.alternative import Alternative
from app.models.decision import Decision
from app.schemas.alternative import (
    AlternativeCreate,
    AlternativeResponse,
)
from app.core.security import get_current_user


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
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Check whether the decision exists
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

    # Create alternative
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
    db.commit()
    db.refresh(new_alternative)

    return new_alternative