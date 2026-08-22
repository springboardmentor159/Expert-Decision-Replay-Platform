from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.schemas.decision_rationale import (
    DecisionRationaleUpdate,
    DecisionRationaleResponse
)
from app.core.security import get_current_user


router = APIRouter(
    tags=["Decision Rationale"]
)


# ============================================================
# UPDATE DECISION RATIONALE
# PUT /decisions/{decision_id}/rationale
# ============================================================

@router.put(
    "/decisions/{decision_id}/rationale",
    response_model=DecisionRationaleResponse
)
def update_rationale(
    decision_id: int,
    rationale_data: DecisionRationaleUpdate,
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

    # Only the decision creator can update the rationale
    if decision.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update the rationale of your own decision"
        )

    decision.rationale = rationale_data.rationale

    db.commit()
    db.refresh(decision)

    return {
        "decision_id": decision.id,
        "rationale": decision.rationale,
        "updated_at": decision.updated_at
    }


# ============================================================
# GET DECISION RATIONALE
# GET /decisions/{decision_id}/rationale
# ============================================================

@router.get(
    "/decisions/{decision_id}/rationale",
    response_model=DecisionRationaleResponse
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
        "rationale": decision.rationale,
        "updated_at": decision.updated_at
    }