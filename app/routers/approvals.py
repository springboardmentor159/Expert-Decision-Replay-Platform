from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.approval import Approval, ApprovalStatus
from app.models.audit import AuditAction
from app.models.decision import Decision, DecisionStatus
from app.models.user import User
from app.schemas.approval import (
    ApprovalCreate,
    ApprovalResponse,
    ApprovalStatusUpdate,
)
from app.services.audit import create_audit_log
from app.services.auth import get_current_user


router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"],
)


# ============================================================
# ORGANIZATION ACCESS HELPERS
# ============================================================

def get_decision_or_404(
    decision_id: int,
    db: Session,
    current_user: User,
) -> Decision:
    """
    Get a decision only if it belongs to
    the current user's organization.
    """

    decision = (
        db.query(Decision)
        .filter(
            Decision.id == decision_id,
            Decision.organization_id == current_user.organization_id,
        )
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return decision


def get_approval_or_404(
    approval_id: int,
    db: Session,
    current_user: User,
) -> Approval:
    """
    Get an approval only if its associated decision
    belongs to the current user's organization.
    """

    approval = (
        db.query(Approval)
        .join(
            Decision,
            Approval.decision_id == Decision.id,
        )
        .filter(
            Approval.id == approval_id,
            Decision.organization_id == current_user.organization_id,
        )
        .first()
    )

    if approval is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found",
        )

    return approval


# ============================================================
# CREATE AN APPROVAL REQUEST
# ============================================================

@router.post(
    "",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_approval(
    approval_data: ApprovalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        approval_data.decision_id,
        db,
        current_user,
    )

    # Reviewer must belong to the same organization.
    reviewer = (
        db.query(User)
        .filter(
            User.id == approval_data.reviewer_id,
            User.organization_id == current_user.organization_id,
        )
        .first()
    )

    if reviewer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reviewer not found in your organization",
        )

    # Decision creator cannot review their own decision.
    if reviewer.id == decision.created_by:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision creator cannot be assigned as reviewer",
        )

    # Prevent duplicate pending approvals.
    existing_approval = (
        db.query(Approval)
        .filter(
            Approval.decision_id == decision.id,
            Approval.reviewer_id == reviewer.id,
            Approval.status == ApprovalStatus.PENDING,
        )
        .first()
    )

    if existing_approval is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A pending approval already exists for this reviewer",
        )

    approval = Approval(
        decision_id=decision.id,
        reviewer_id=reviewer.id,
        status=ApprovalStatus.PENDING,
    )

    db.add(approval)
    db.flush()

    # Log approval assignment.
    create_audit_log(
        db=db,
        decision_id=decision.id,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"Approval was assigned to '{reviewer.full_name}' "
            f"for decision '{decision.title}'"
        ),
    )

    db.commit()
    db.refresh(approval)

    return approval


# ============================================================
# GET ALL APPROVALS FOR A DECISION
# ============================================================

@router.get(
    "/decision/{decision_id}",
    response_model=list[ApprovalResponse],
)
def get_decision_approvals(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        decision_id,
        db,
        current_user,
    )

    return (
        db.query(Approval)
        .filter(
            Approval.decision_id == decision.id
        )
        .order_by(Approval.created_at)
        .all()
    )


# ============================================================
# GET APPROVALS ASSIGNED TO CURRENT USER
# ============================================================

@router.get(
    "/my",
    response_model=list[ApprovalResponse],
)
def get_my_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Approval)
        .join(
            Decision,
            Approval.decision_id == Decision.id,
        )
        .filter(
            Approval.reviewer_id == current_user.id,
            Decision.organization_id == current_user.organization_id,
        )
        .order_by(Approval.created_at)
        .all()
    )


# ============================================================
# GET AN APPROVAL BY ID
# ============================================================

@router.get(
    "/{approval_id}",
    response_model=ApprovalResponse,
)
def get_approval(
    approval_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    approval = get_approval_or_404(
        approval_id,
        db,
        current_user,
    )

    return approval


# ============================================================
# APPROVE OR REJECT AN APPROVAL
# ============================================================

@router.patch(
    "/{approval_id}/status",
    response_model=ApprovalResponse,
)
def update_approval_status(
    approval_id: int,
    status_data: ApprovalStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    approval = get_approval_or_404(
        approval_id,
        db,
        current_user,
    )

    # Only the assigned reviewer can approve/reject.
    if approval.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this approval",
        )

    # Approval can only be completed once.
    if approval.status != ApprovalStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Approval has already been completed",
        )

    # Pending is not a valid completion status.
    if status_data.status == ApprovalStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval status must be Approved or Rejected",
        )

    # Get the associated decision.
    decision = get_decision_or_404(
        approval.decision_id,
        db,
        current_user,
    )

    # Update approval.
    approval.status = status_data.status
    approval.completed_at = datetime.utcnow()

    # Update decision status.
    if status_data.status == ApprovalStatus.APPROVED:
        decision.status = DecisionStatus.APPROVED

    elif status_data.status == ApprovalStatus.REJECTED:
        decision.status = DecisionStatus.REJECTED

    # --------------------------------------------------------
    # Log approval status change
    # --------------------------------------------------------

    create_audit_log(
        db=db,
        decision_id=decision.id,
        user_id=current_user.id,
        action=AuditAction.STATUS_CHANGE,
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"Approval was marked "
            f"'{status_data.status.value}' by "
            f"'{current_user.full_name}' "
            f"for decision '{decision.title}'"
        ),
    )

    # --------------------------------------------------------
    # Log decision status change
    # --------------------------------------------------------

    create_audit_log(
        db=db,
        decision_id=decision.id,
        user_id=current_user.id,
        action=AuditAction.STATUS_CHANGE,
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"Decision '{decision.title}' was marked "
            f"'{status_data.status.value}'"
        ),
    )

    db.commit()
    db.refresh(approval)

    return approval