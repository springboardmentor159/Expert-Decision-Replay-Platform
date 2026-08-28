from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.schemas.rationale import (
    RationaleUpdate,
    RationaleResponse,
)
from app.routers.users import get_current_user


router = APIRouter(
    tags=["Decision Rationale"]
)


# UPDATE DECISION RATIONALE
@router.put(
    "/decisions/{decision_id}/rationale",
    response_model=RationaleResponse
)
def update_rationale(
    decision_id: int,
    rationale_data: RationaleUpdate,
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
            status_code=404,
            detail="Decision not found"
        )

    decision.rationale = rationale_data.rationale

    db.commit()
    db.refresh(decision)

    return {
        "decision_id": decision.id,
        "rationale": decision.rationale
    }


# GET DECISION RATIONALE
@router.get(
    "/decisions/{decision_id}/rationale",
    response_model=RationaleResponse
)
def get_rationale(
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
            status_code=404,
            detail="Decision not found"
        )

    return {
        "decision_id": decision.id,
        "rationale": decision.rationale
    }