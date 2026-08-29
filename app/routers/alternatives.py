from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.alternative import Alternative
from app.models.audit import AuditAction
from app.models.decision import Decision, DecisionStatus
from app.models.user import User, UserRole
from app.schemas.alternative import (
    AlternativeCreate,
    AlternativeResponse,
    AlternativeUpdate,
)
from app.services.audit import create_audit_log
from app.services.auth import get_current_user


router = APIRouter(
    tags=["Alternatives"]
)


# ============================================================
# DECISION ACCESS HELPERS
# ============================================================

def get_decision_or_404(
    decision_id: int,
    db: Session,
    current_user: User,
) -> Decision:
    """
    Fetch a decision and make sure it belongs to
    the current user's organization.
    """

    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    # Organization isolation
    if decision.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return decision


def can_modify_decision(
    decision: Decision,
    current_user: User,
) -> bool:
    """
    User can modify a decision only if:
    - decision belongs to the same organization, and
    - user is the creator, Manager, or Administrator.
    """

    if decision.organization_id != current_user.organization_id:
        return False

    return (
        decision.created_by == current_user.id
        or current_user.role in (
            UserRole.MANAGER,
            UserRole.ADMINISTRATOR,
        )
    )


# ============================================================
# CREATE AN ALTERNATIVE
# ============================================================

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
        decision_id,
        db,
        current_user,
    )

    if not can_modify_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission to modify "
                "alternatives for this decision"
            ),
        )

    if decision.status == DecisionStatus.ARCHIVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify an archived decision",
        )

    alternative = Alternative(
        decision_id=decision.id,
        name=alternative_data.name,
        description=alternative_data.description,
        pros=alternative_data.pros,
        cons=alternative_data.cons,
        estimated_cost=alternative_data.estimated_cost,
        feasibility_score=alternative_data.feasibility_score,
        risk_level=alternative_data.risk_level,
    )

    db.add(alternative)
    db.flush()

    create_audit_log(
        db=db,
        decision_id=decision.id,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type="Alternative",
        entity_id=alternative.id,
        description=(
            f"Alternative '{alternative.name}' "
            f"was created for decision '{decision.title}'"
        ),
    )

    db.commit()
    db.refresh(alternative)

    return alternative


# ============================================================
# GET ALL ALTERNATIVES FOR A DECISION
# ============================================================

@router.get(
    "/decisions/{decision_id}/alternatives",
    response_model=list[AlternativeResponse],
)
def get_decision_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        decision_id,
        db,
        current_user,
    )

    # Any authenticated user in the organization
    # can view the alternatives.
    if decision.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return (
        db.query(Alternative)
        .filter(
            Alternative.decision_id == decision_id
        )
        .order_by(Alternative.id)
        .all()
    )


# ============================================================
# GET ALTERNATIVE BY ID
# ============================================================

@router.get(
    "/alternatives/{alternative_id}",
    response_model=AlternativeResponse,
)
def get_alternative(
    alternative_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alternative = (
        db.query(Alternative)
        .filter(Alternative.id == alternative_id)
        .first()
    )

    if alternative is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found",
        )

    # Get parent decision
    decision = get_decision_or_404(
        alternative.decision_id,
        db,
        current_user,
    )

    if decision.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found",
        )

    return alternative


# ============================================================
# UPDATE ALTERNATIVE
# ============================================================

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
    alternative = (
        db.query(Alternative)
        .filter(Alternative.id == alternative_id)
        .first()
    )

    if alternative is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found",
        )

    decision = get_decision_or_404(
        alternative.decision_id,
        db,
        current_user,
    )

    if not can_modify_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to modify this alternative"
            ),
        )

    if decision.status == DecisionStatus.ARCHIVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify an archived decision",
        )

    alternative.name = alternative_data.name
    alternative.description = alternative_data.description
    alternative.pros = alternative_data.pros
    alternative.cons = alternative_data.cons
    alternative.estimated_cost = (
        alternative_data.estimated_cost
    )
    alternative.feasibility_score = (
        alternative_data.feasibility_score
    )
    alternative.risk_level = alternative_data.risk_level

    create_audit_log(
        db=db,
        decision_id=alternative.decision_id,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type="Alternative",
        entity_id=alternative.id,
        description=(
            f"Alternative '{alternative.name}' "
            f"was updated"
        ),
    )

    db.commit()
    db.refresh(alternative)

    return alternative


# ============================================================
# DELETE ALTERNATIVE
# ============================================================

@router.delete(
    "/alternatives/{alternative_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_alternative(
    alternative_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alternative = (
        db.query(Alternative)
        .filter(Alternative.id == alternative_id)
        .first()
    )

    if alternative is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found",
        )

    decision = get_decision_or_404(
        alternative.decision_id,
        db,
        current_user,
    )

    if not can_modify_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to delete this alternative"
            ),
        )

    if decision.status == DecisionStatus.ARCHIVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify an archived decision",
        )

    decision_id = alternative.decision_id
    alternative_name = alternative.name
    decision_title = decision.title

    create_audit_log(
        db=db,
        decision_id=decision_id,
        user_id=current_user.id,
        action=AuditAction.DELETE,
        entity_type="Alternative",
        entity_id=alternative.id,
        description=(
            f"Alternative '{alternative_name}' "
            f"was deleted from decision "
            f"'{decision_title}'"
        ),
    )

    db.delete(alternative)
    db.commit()

    return None


# ============================================================
# COMPARE ALL ALTERNATIVES
# ============================================================

@router.get(
    "/decisions/{decision_id}/alternatives/compare"
)
def compare_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        decision_id,
        db,
        current_user,
    )

    alternatives = (
        db.query(Alternative)
        .filter(
            Alternative.decision_id == decision_id
        )
        .order_by(Alternative.id)
        .all()
    )

    return {
        "decision_id": decision_id,
        "alternatives": [
            {
                "name": alternative.name,
                "estimated_cost": alternative.estimated_cost,
                "feasibility_score": alternative.feasibility_score,
                "risk_level": alternative.risk_level,
            }
            for alternative in alternatives
        ],
    }