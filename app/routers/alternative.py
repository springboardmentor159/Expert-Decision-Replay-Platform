from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.alternative import Alternative
from app.models.decision import Decision
from app.models.user import User
from app.schemas.alternative import (
    AlternativeCreate,
    AlternativeUpdate,
    AlternativeResponse,
    AlternativeCompareResponse,
)
from app.utils.security import get_current_user
from app.utils.activity_logger import log_activity
from app.utils.audit import log_audit


router = APIRouter(tags=["Alternatives"])


def get_decision_or_404(decision_id: int, db: Session) -> Decision:
    decision = db.query(Decision).filter(Decision.id == decision_id).first()

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return decision


# CREATE ALTERNATIVE
@router.post(
    "/decisions/{decision_id}/alternatives",
    response_model=AlternativeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_alternative(
    decision_id: int,
    alternative: AlternativeCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_decision_or_404(decision_id, db)

    new_alternative = Alternative(
        decision_id=decision_id,
        name=alternative.name,
        description=alternative.description,
        pros=alternative.pros,
        cons=alternative.cons,
        estimated_cost=alternative.estimated_cost,
        feasibility_score=alternative.feasibility_score,
        risk_level=alternative.risk_level.value,
    )

    db.add(new_alternative)
    db.commit()
    db.refresh(new_alternative)
    log_activity(
        db=db,
        user_id=current_user.id,
        action="alternative_created",
        entity_type="Alternative",
        entity_id=new_alternative.id,
        description=f"Alternative '{new_alternative.name}' was added to a decision",
    )
    log_audit(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Alternative",
        entity_id=new_alternative.id,
        description=f"Alternative '{new_alternative.name}' was added to decision {decision_id}",
        new_value={
            "decision_id": decision_id,
            "name": new_alternative.name,
            "risk_level": new_alternative.risk_level,
        },
        request=request,
    )

    return new_alternative


# GET ALL ALTERNATIVES FOR A DECISION
@router.get(
    "/decisions/{decision_id}/alternatives",
    response_model=list[AlternativeResponse]
)
def get_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_decision_or_404(decision_id, db)

    return (
        db.query(Alternative)
        .filter(Alternative.decision_id == decision_id)
        .all()
    )


# GET ONE ALTERNATIVE BY ID
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

    if alternative is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found"
        )

    return alternative


# UPDATE ALTERNATIVE
@router.put(
    "/alternatives/{alternative_id}",
    response_model=AlternativeResponse
)
def update_alternative(
    alternative_id: int,
    data: AlternativeUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alternative = (
        db.query(Alternative)
        .filter(Alternative.id == alternative_id)
        .first()
    )

    if alternative is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found"
        )

    old_value = {
        "name": alternative.name,
        "estimated_cost": alternative.estimated_cost,
        "feasibility_score": alternative.feasibility_score,
        "risk_level": alternative.risk_level,
    }

    # Only allowed fields can be updated.
    # id, decision_id, created_at are never touched here.
    if data.name is not None:
        alternative.name = data.name

    if data.description is not None:
        alternative.description = data.description

    if data.pros is not None:
        alternative.pros = data.pros

    if data.cons is not None:
        alternative.cons = data.cons

    if data.estimated_cost is not None:
        alternative.estimated_cost = data.estimated_cost

    if data.feasibility_score is not None:
        alternative.feasibility_score = data.feasibility_score

    if data.risk_level is not None:
        alternative.risk_level = data.risk_level.value

    alternative.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(alternative)

    log_audit(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Alternative",
        entity_id=alternative.id,
        description=f"Alternative '{alternative.name}' was updated",
        old_value=old_value,
        new_value={
            "name": alternative.name,
            "estimated_cost": alternative.estimated_cost,
            "feasibility_score": alternative.feasibility_score,
            "risk_level": alternative.risk_level,
        },
        request=request,
    )

    return alternative


# COMPARE ALTERNATIVES FOR A DECISION
@router.get(
    "/decisions/{decision_id}/alternatives/compare",
    response_model=AlternativeCompareResponse
)
def compare_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_decision_or_404(decision_id, db)

    alternatives = (
        db.query(Alternative)
        .filter(Alternative.decision_id == decision_id)
        .all()
    )

    return {
        "decision_id": decision_id,
        "alternatives": alternatives
    }