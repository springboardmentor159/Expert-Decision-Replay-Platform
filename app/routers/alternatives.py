from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.alternative import Alternative
from app.models.decision import Decision
from app.models.user import User
from app.schemas.alternative import (
    AlternativeCreate,
    AlternativeResponse,
    AlternativeUpdate,
)
from app.schemas.audit_log import AuditAction, AuditEntityType
from app.services.activity_service import log_activity
from app.services.audit_service import log_audit


router = APIRouter(
    tags=["Alternatives"],
)


def get_decision_or_404(
    db: Session,
    decision_id: int,
) -> Decision:
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

    return decision


def get_alternative_or_404(
    db: Session,
    alternative_id: int,
) -> Alternative:
    alternative = (
        db.query(Alternative)
        .filter(Alternative.id == alternative_id)
        .first()
    )

    if not alternative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found",
        )

    return alternative


def ensure_decision_view_access(
    decision: Decision,
    current_user: User,
) -> None:
    """
    Verify access to a decision and its alternatives.

    Employees may access their own decisions.
    Reviewers, Managers and Administrators may access
    decisions available through the platform.
    """

    if current_user.role == "Employee":
        if decision.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access alternatives for your own decisions",
            )
        return

    if current_user.role in {
        "Reviewer",
        "Manager",
        "Administrator",
    }:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions",
    )


def ensure_alternative_manage_access(
    decision: Decision,
    current_user: User,
) -> None:
    """
    Only the decision owner can modify alternatives while
    the decision is still a draft.

    Administrators can manage alternatives regardless of
    decision ownership.
    """

    if current_user.role == "Administrator":
        return

    if (
        current_user.role in {"Employee", "Manager"}
        and decision.created_by == current_user.id
        and decision.status == "Draft"
    ):
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=(
            "Only the decision owner can manage alternatives "
            "while the decision is a draft"
        ),
    )


def validate_alternative_fields(
    name: str,
    description: str,
    pros: str,
    cons: str,
    estimated_cost: int,
    feasibility_score: int,
) -> None:
    if not name or not name.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Alternative name cannot be empty",
        )

    if not description or not description.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Alternative description cannot be empty",
        )

    if not pros or not pros.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Alternative pros cannot be empty",
        )

    if not cons or not cons.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Alternative cons cannot be empty",
        )

    if estimated_cost < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Estimated cost cannot be negative",
        )

    if not 1 <= feasibility_score <= 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Feasibility score must be between 1 and 5",
        )


def alternative_values(
    alternative: Alternative,
) -> dict:
    return {
        "decision_id": alternative.decision_id,
        "name": alternative.name,
        "description": alternative.description,
        "pros": alternative.pros,
        "cons": alternative.cons,
        "estimated_cost": alternative.estimated_cost,
        "feasibility_score": alternative.feasibility_score,
        "risk_level": alternative.risk_level,
    }


# ---------------------------------------------------------------------------
# CREATE ALTERNATIVE
# ---------------------------------------------------------------------------

@router.post(
    "/decisions/{decision_id}/alternatives",
    response_model=AlternativeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_alternative(
    decision_id: int,
    alternative_data: AlternativeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        db,
        decision_id,
    )

    ensure_alternative_manage_access(
        decision,
        current_user,
    )

    validate_alternative_fields(
        alternative_data.name,
        alternative_data.description,
        alternative_data.pros,
        alternative_data.cons,
        alternative_data.estimated_cost,
        alternative_data.feasibility_score,
    )

    alternative = Alternative(
        decision_id=decision_id,
        name=alternative_data.name.strip(),
        description=alternative_data.description.strip(),
        pros=alternative_data.pros.strip(),
        cons=alternative_data.cons.strip(),
        estimated_cost=alternative_data.estimated_cost,
        feasibility_score=alternative_data.feasibility_score,
        risk_level=alternative_data.risk_level.value,
    )

    db.add(alternative)
    db.flush()

    values = alternative_values(alternative)

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type=AuditEntityType.ALTERNATIVE,
        entity_id=alternative.id,
        description=(
            f"Alternative '{alternative.name}' created "
            f"for Decision {decision_id}"
        ),
        new_value=values,
        request_method="POST",
        endpoint=f"/decisions/{decision_id}/alternatives",
    )

    log_activity(
        db,
        current_user.id,
        "Alternative Created",
        "Alternative",
        alternative.id,
        (
            f"Alternative '{alternative.name}' created "
            f"for Decision {decision_id}"
        ),
    )

    db.commit()
    db.refresh(alternative)

    return alternative


# ---------------------------------------------------------------------------
# GET ALL ALTERNATIVES FOR A DECISION
# ---------------------------------------------------------------------------

@router.get(
    "/decisions/{decision_id}/alternatives",
    response_model=List[AlternativeResponse],
)
def get_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        db,
        decision_id,
    )

    ensure_decision_view_access(
        decision,
        current_user,
    )

    return (
        db.query(Alternative)
        .filter(
            Alternative.decision_id == decision_id,
        )
        .order_by(
            Alternative.created_at.asc(),
            Alternative.id.asc(),
        )
        .all()
    )


# ---------------------------------------------------------------------------
# GET ALTERNATIVE BY ID
# ---------------------------------------------------------------------------

@router.get(
    "/alternatives/{alternative_id}",
    response_model=AlternativeResponse,
)
def get_alternative(
    alternative_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alternative = get_alternative_or_404(
        db,
        alternative_id,
    )

    decision = get_decision_or_404(
        db,
        alternative.decision_id,
    )

    ensure_decision_view_access(
        decision,
        current_user,
    )

    return alternative


# ---------------------------------------------------------------------------
# UPDATE ALTERNATIVE
# ---------------------------------------------------------------------------

@router.put(
    "/alternatives/{alternative_id}",
    response_model=AlternativeResponse,
)
def update_alternative(
    alternative_id: int,
    alternative_data: AlternativeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alternative = get_alternative_or_404(
        db,
        alternative_id,
    )

    decision = get_decision_or_404(
        db,
        alternative.decision_id,
    )

    ensure_alternative_manage_access(
        decision,
        current_user,
    )

    validate_alternative_fields(
        alternative_data.name,
        alternative_data.description,
        alternative_data.pros,
        alternative_data.cons,
        alternative_data.estimated_cost,
        alternative_data.feasibility_score,
    )

    old_values = alternative_values(alternative)

    alternative.name = alternative_data.name.strip()
    alternative.description = (
        alternative_data.description.strip()
    )
    alternative.pros = alternative_data.pros.strip()
    alternative.cons = alternative_data.cons.strip()
    alternative.estimated_cost = alternative_data.estimated_cost
    alternative.feasibility_score = (
        alternative_data.feasibility_score
    )
    alternative.risk_level = alternative_data.risk_level.value

    new_values = alternative_values(alternative)

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type=AuditEntityType.ALTERNATIVE,
        entity_id=alternative.id,
        description=(
            f"Alternative '{alternative.name}' updated "
            f"for Decision {decision.id}"
        ),
        old_value=old_values,
        new_value=new_values,
        request_method="PUT",
        endpoint=f"/alternatives/{alternative.id}",
    )

    log_activity(
        db,
        current_user.id,
        "Alternative Updated",
        "Alternative",
        alternative.id,
        (
            f"Alternative '{alternative.name}' updated "
            f"for Decision {decision.id}"
        ),
    )

    db.commit()
    db.refresh(alternative)

    return alternative


# ---------------------------------------------------------------------------
# DELETE ALTERNATIVE
# ---------------------------------------------------------------------------

@router.delete(
    "/alternatives/{alternative_id}",
    status_code=status.HTTP_200_OK,
)
def delete_alternative(
    alternative_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alternative = get_alternative_or_404(
        db,
        alternative_id,
    )

    decision = get_decision_or_404(
        db,
        alternative.decision_id,
    )

    ensure_alternative_manage_access(
        decision,
        current_user,
    )

    old_values = alternative_values(alternative)
    alternative_name = alternative.name

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.DELETE,
        entity_type=AuditEntityType.ALTERNATIVE,
        entity_id=alternative.id,
        description=(
            f"Alternative '{alternative.name}' deleted "
            f"from Decision {decision.id}"
        ),
        old_value=old_values,
        request_method="DELETE",
        endpoint=f"/alternatives/{alternative.id}",
    )

    log_activity(
        db,
        current_user.id,
        "Alternative Deleted",
        "Alternative",
        alternative.id,
        (
            f"Alternative '{alternative.name}' deleted "
            f"from Decision {decision.id}"
        ),
    )

    db.delete(alternative)
    db.commit()

    return {
        "message": "Alternative deleted successfully",
        "alternative_id": alternative_id,
        "name": alternative_name,
    }


# ---------------------------------------------------------------------------
# COMPARE ALTERNATIVES
# ---------------------------------------------------------------------------

@router.get(
    "/decisions/{decision_id}/alternatives/compare",
)
def compare_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        db,
        decision_id,
    )

    ensure_decision_view_access(
        decision,
        current_user,
    )

    alternatives = (
        db.query(Alternative)
        .filter(
            Alternative.decision_id == decision_id,
        )
        .order_by(
            Alternative.feasibility_score.desc(),
            Alternative.id.asc(),
        )
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
                "risk_level": alternative.risk_level,
            }
            for alternative in alternatives
        ],
    }