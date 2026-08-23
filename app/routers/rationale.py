from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.decision import Decision
from app.models.user import User
from app.schemas.rationale import RationaleUpdate

router = APIRouter(
    prefix="/decisions",
    tags=["Decision Rationale"],
)


# CREATE / UPDATE RATIONALE
@router.put("/{decision_id}/rationale")
def update_rationale(
    decision_id: int,
    data: RationaleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    decision.rationale = data.rationale

    db.commit()
    db.refresh(decision)

    return {
        "id": decision.id,
        "rationale": decision.rationale,
    }


# GET RATIONALE
@router.get("/{decision_id}/rationale")
def get_rationale(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    if decision.rationale is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision rationale not found",
        )

    return {
        "id": decision.id,
        "rationale": decision.rationale,
    }


# DELETE RATIONALE
@router.delete("/{decision_id}/rationale")
def delete_rationale(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    if decision.rationale is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision rationale not found",
        )

    decision.rationale = None

    db.commit()
    db.refresh(decision)

    return {
        "message": "Decision rationale deleted successfully"
    }