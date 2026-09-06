from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.alternative import Alternative
from app.models.decision import Decision
from app.schemas.alternative import AlternativeCreate, AlternativeResponse
from app.core.dependencies import get_current_user
from app.core.audit_logger import create_audit_log


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

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Alternative",
        entity_id=new_alternative.id,
        description=f"Alternative '{new_alternative.name}' created",
        new_value={
            "decision_id": new_alternative.decision_id,
            "name": new_alternative.name,
            "description": new_alternative.description,
            "pros": new_alternative.pros,
            "cons": new_alternative.cons,
            "estimated_cost": new_alternative.estimated_cost,
            "feasibility_score": new_alternative.feasibility_score,
            "risk_level": new_alternative.risk_level
        },
        request_method="POST",
        endpoint="/alternatives/"
    )

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


# =========================================================
# UPDATE ALTERNATIVE
# =========================================================

@router.put(
    "/{alternative_id}",
    response_model=AlternativeResponse
)
def update_alternative(
    alternative_id: int,
    alternative_data: AlternativeCreate,
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

    decision = db.query(Decision).filter(
        Decision.id == alternative_data.decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    # Store old values before update
    old_value = {
        "decision_id": alternative.decision_id,
        "name": alternative.name,
        "description": alternative.description,
        "pros": alternative.pros,
        "cons": alternative.cons,
        "estimated_cost": alternative.estimated_cost,
        "feasibility_score": alternative.feasibility_score,
        "risk_level": alternative.risk_level
    }

    # Update alternative
    alternative.decision_id = alternative_data.decision_id
    alternative.name = alternative_data.name
    alternative.description = alternative_data.description
    alternative.pros = alternative_data.pros
    alternative.cons = alternative_data.cons
    alternative.estimated_cost = alternative_data.estimated_cost
    alternative.feasibility_score = alternative_data.feasibility_score
    alternative.risk_level = alternative_data.risk_level

    db.commit()
    db.refresh(alternative)

    # Automatic audit log - UPDATE
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Alternative",
        entity_id=alternative.id,
        description=f"Alternative '{alternative.name}' updated",
        old_value=old_value,
        new_value={
            "decision_id": alternative.decision_id,
            "name": alternative.name,
            "description": alternative.description,
            "pros": alternative.pros,
            "cons": alternative.cons,
            "estimated_cost": alternative.estimated_cost,
            "feasibility_score": alternative.feasibility_score,
            "risk_level": alternative.risk_level
        },
        request_method="PUT",
        endpoint=f"/alternatives/{alternative.id}"
    )

    return alternative


# =========================================================
# DELETE ALTERNATIVE
# =========================================================

@router.delete(
    "/{alternative_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_alternative(
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

    # Store old values before deletion
    old_value = {
        "decision_id": alternative.decision_id,
        "name": alternative.name,
        "description": alternative.description,
        "pros": alternative.pros,
        "cons": alternative.cons,
        "estimated_cost": alternative.estimated_cost,
        "feasibility_score": alternative.feasibility_score,
        "risk_level": alternative.risk_level
    }

    alternative_name = alternative.name
    alternative_id_value = alternative.id

    # Delete alternative
    db.delete(alternative)
    db.commit()

    # Automatic audit log - DELETE
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="Alternative",
        entity_id=alternative_id_value,
        description=f"Alternative '{alternative_name}' deleted",
        old_value=old_value,
        new_value=None,
        request_method="DELETE",
        endpoint=f"/alternatives/{alternative_id_value}"
    )

    return None