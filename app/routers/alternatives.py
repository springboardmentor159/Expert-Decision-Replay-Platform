from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.alternative import Alternative
from app.models.decision import Decision
from app.models.user import User

from app.schemas.alternative import (
    AlternativeCreate,
    AlternativeUpdate,
    AlternativeResponse
)

from app.core.security import get_current_user

from app.services.audit import log_audit


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/alternatives",
    tags=["Alternatives"]
)


# =========================================================
# HELPER - SERIALIZE ALTERNATIVE
# =========================================================

def alternative_to_dict(alternative: Alternative):
    """
    Convert an Alternative SQLAlchemy object into a
    JSON-compatible dictionary for audit logging.

    This is used to preserve old/new values without
    storing the SQLAlchemy object itself.
    """

    return {
        "id": alternative.id,
        "decision_id": alternative.decision_id,
        "name": alternative.name,
        "description": alternative.description,
        "pros": alternative.pros,
        "cons": alternative.cons,
        "estimated_cost": alternative.estimated_cost,
        "feasibility_score": alternative.feasibility_score,
        "risk_level": alternative.risk_level
    }


# =========================================================
# CREATE ALTERNATIVE
# =========================================================

@router.post(
    "/decision/{decision_id}",
    response_model=AlternativeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_alternative(
    decision_id: int,
    alternative_data: AlternativeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # CHECK DECISION
    # -----------------------------------------------------

    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    # -----------------------------------------------------
    # CREATE ALTERNATIVE
    # -----------------------------------------------------

    new_alternative = Alternative(
        decision_id=decision_id,
        name=alternative_data.name,
        description=alternative_data.description,
        pros=alternative_data.pros,
        cons=alternative_data.cons,
        estimated_cost=alternative_data.estimated_cost,
        feasibility_score=alternative_data.feasibility_score,
        risk_level=alternative_data.risk_level
    )

    db.add(new_alternative)

    # Flush so the database generates the alternative ID
    # before creating the audit record.
    db.flush()

    # -----------------------------------------------------
    # AUDIT - CREATE
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Alternative",
        entity_id=new_alternative.id,
        description=(
            f"User {current_user.id} created "
            f"Alternative {new_alternative.id} "
            f"for Decision {decision_id}"
        ),
        new_value=alternative_to_dict(
            new_alternative
        ),
        request_method="POST",
        endpoint=f"/alternatives/decision/{decision_id}"
    )

    # -----------------------------------------------------
    # COMMIT
    # -----------------------------------------------------

    db.commit()
    db.refresh(new_alternative)

    return new_alternative


# =========================================================
# GET ALL ALTERNATIVES FOR A DECISION
# =========================================================

@router.get(
    "/decision/{decision_id}",
    response_model=list[AlternativeResponse]
)
def get_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # CHECK DECISION
    # -----------------------------------------------------

    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    alternatives = db.query(
        Alternative
    ).filter(
        Alternative.decision_id == decision_id
    ).all()

    return alternatives


# =========================================================
# GET SINGLE ALTERNATIVE
# =========================================================

@router.get(
    "/{alternative_id}",
    response_model=AlternativeResponse
)
def get_alternative(
    alternative_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    alternative = db.query(
        Alternative
    ).filter(
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
    alternative_data: AlternativeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # FIND ALTERNATIVE
    # -----------------------------------------------------

    alternative = db.query(
        Alternative
    ).filter(
        Alternative.id == alternative_id
    ).first()

    if not alternative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found"
        )

    # -----------------------------------------------------
    # SAVE OLD VALUE
    # -----------------------------------------------------

    old_value = alternative_to_dict(
        alternative
    )

    # -----------------------------------------------------
    # GET PROVIDED FIELDS
    # -----------------------------------------------------

    update_data = alternative_data.model_dump(
        exclude_unset=True
    )

    if not update_data:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    # -----------------------------------------------------
    # APPLY UPDATE
    # -----------------------------------------------------

    for key, value in update_data.items():

        setattr(
            alternative,
            key,
            value
        )

    db.flush()

    # -----------------------------------------------------
    # SAVE NEW VALUE
    # -----------------------------------------------------

    new_value = alternative_to_dict(
        alternative
    )

    # -----------------------------------------------------
    # AUDIT - UPDATE
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Alternative",
        entity_id=alternative.id,
        description=(
            f"User {current_user.id} updated "
            f"Alternative {alternative.id}"
        ),
        old_value=old_value,
        new_value=new_value,
        request_method="PUT",
        endpoint=f"/alternatives/{alternative_id}"
    )

    # -----------------------------------------------------
    # COMMIT
    # -----------------------------------------------------

    db.commit()
    db.refresh(alternative)

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
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # FIND ALTERNATIVE
    # -----------------------------------------------------

    alternative = db.query(
        Alternative
    ).filter(
        Alternative.id == alternative_id
    ).first()

    if not alternative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found"
        )

    # -----------------------------------------------------
    # SAVE VALUE BEFORE DELETE
    # -----------------------------------------------------

    old_value = alternative_to_dict(
        alternative
    )

    decision_id = alternative.decision_id

    # -----------------------------------------------------
    # AUDIT - DELETE
    #
    # Audit is created BEFORE deleting the entity.
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="Alternative",
        entity_id=alternative.id,
        description=(
            f"User {current_user.id} deleted "
            f"Alternative {alternative.id} "
            f"from Decision {decision_id}"
        ),
        old_value=old_value,
        request_method="DELETE",
        endpoint=f"/alternatives/{alternative_id}"
    )

    # -----------------------------------------------------
    # DELETE
    # -----------------------------------------------------

    db.delete(alternative)

    # -----------------------------------------------------
    # COMMIT
    # -----------------------------------------------------

    db.commit()

    return None