from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.alternative import Alternative
from app.models.decision import Decision
from app.models.user import User
from app.schemas.alternative import AlternativeCreate, AlternativeResponse
from app.services.activity_service import log_activity
from app.services.audit_service import log_audit


router = APIRouter(
    tags=["Alternatives"]
)


# ---------------------------------------------------------
# CREATE ALTERNATIVE
# POST /decisions/{decision_id}/alternatives
# ---------------------------------------------------------
@router.post(
    "/decisions/{decision_id}/alternatives",
    response_model=AlternativeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_alternative(
    decision_id: int,
    alternative_data: AlternativeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    new_alternative = Alternative(
        decision_id=decision_id,
        name=alternative_data.name,
        description=alternative_data.description,
        pros=alternative_data.pros,
        cons=alternative_data.cons,
        estimated_cost=alternative_data.estimated_cost,
        feasibility_score=alternative_data.feasibility_score,
        risk_level=alternative_data.risk_level.value
    )

    db.add(new_alternative)
    db.flush()

    log_activity(
        db,
        user_id=current_user.id,
        action="alternative_created",
        entity_type="alternative",
        entity_id=new_alternative.id,
        description=f"User {current_user.id} added Alternative {new_alternative.id}"
    )

    log_audit(
        db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Alternative",
        entity_id=new_alternative.id,
        description=f"User {current_user.id} created Alternative {new_alternative.id}",
        new_value={
            "name": new_alternative.name,
            "decision_id": decision_id,
        },
    )

    db.commit()
    db.refresh(new_alternative)

    return new_alternative


# ---------------------------------------------------------
# GET ALL ALTERNATIVES FOR A DECISION
# GET /decisions/{decision_id}/alternatives
# ---------------------------------------------------------
@router.get(
    "/decisions/{decision_id}/alternatives",
    response_model=List[AlternativeResponse]
)
def get_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    alternatives = (
        db.query(Alternative)
        .filter(Alternative.decision_id == decision_id)
        .all()
    )

    return alternatives


# ---------------------------------------------------------
# GET ONE ALTERNATIVE
# GET /alternatives/{alternative_id}
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# UPDATE ALTERNATIVE
# PUT /alternatives/{alternative_id}
# ---------------------------------------------------------
@router.put(
    "/alternatives/{alternative_id}",
    response_model=AlternativeResponse
)
def update_alternative(
    alternative_id: int,
    alternative_data: AlternativeCreate,
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
    old_data = {
        "name": alternative.name,
        "description": alternative.description,
        "pros": alternative.pros,
        "cons": alternative.cons,
    }

    alternative.name = alternative_data.name
    alternative.description = alternative_data.description
    alternative.pros = alternative_data.pros
    alternative.cons = alternative_data.cons
    alternative.estimated_cost = alternative_data.estimated_cost
    alternative.feasibility_score = alternative_data.feasibility_score
    alternative.risk_level = alternative_data.risk_level.value

    log_activity(
        db,
        user_id=current_user.id,
        action="alternative_updated",
        entity_type="alternative",
        entity_id=alternative.id,
        description=f"User {current_user.id} updated Alternative {alternative.id}"
    )

    log_audit(
        db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Alternative",
        entity_id=alternative.id,
        description=f"User {current_user.id} updated Alternative {alternative.id}",
        old_value=old_data,
        new_value={
            "name": alternative.name,
            "description": alternative.description,
            "pros": alternative.pros,
            "cons": alternative.cons,
        },
    )

    db.commit()
    db.refresh(alternative)

    return alternative
@router.get(
    "/decisions/{decision_id}/alternatives/compare"
)
def compare_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
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
                "id": alternative.id,
                "name": alternative.name,
                "description": alternative.description,
                "pros": alternative.pros,
                "cons": alternative.cons,
                "estimated_cost": alternative.estimated_cost,
                "feasibility_score": alternative.feasibility_score,
                "risk_level": alternative.risk_level
            }
            for alternative in alternatives
        ]
    }
@router.delete(
    "/alternatives/{alternative_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_alternative(
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
    log_audit(
        db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="Alternative",
        entity_id=alternative.id,
        description=f"User {current_user.id} deleted Alternative {alternative.id}",
    )

    db.delete(alternative)
    db.commit()

    return None
