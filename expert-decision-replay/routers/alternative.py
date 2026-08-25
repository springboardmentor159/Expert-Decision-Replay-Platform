from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.alternative import Alternative
from app.models.decision import Decision
from app.schemas.alternative import AlternativeCreate, AlternativeResponse
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/alternatives",
    tags=["Alternatives"]
)


# =========================================================
# CREATE ALTERNATIVE
# =========================================================

@router.post(
    "/",
    response_model=AlternativeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_alternative(
    alternative: AlternativeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Check whether decision exists
    decision = db.query(Decision).filter(
        Decision.id == alternative.decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    new_alternative = Alternative(
        decision_id=alternative.decision_id,
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
# GET ALL ALTERNATIVES
# =========================================================

@router.get(
    "/",
    response_model=list[AlternativeResponse]
)
def get_alternatives(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    alternatives = db.query(Alternative).all()

    return alternatives


# =========================================================
# GET ALTERNATIVE BY ID
# =========================================================

@router.get(
    "/{alternative_id}",
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found"
        )

    return alternative