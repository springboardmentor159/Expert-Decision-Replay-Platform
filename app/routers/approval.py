from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db

from app.models.approval import Approval
from app.models.approval_status import ApprovalStatus
from app.models.decision import Decision
from app.models.user import User

from app.schemas.approval import (
    ApprovalCreate,
    ApprovalUpdate,
    ApprovalResponse
)

from app.services.activity_log import create_activity_log


router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"]
)


# ==========================================
# CREATE / ASSIGN APPROVAL
# ==========================================
@router.post(
    "/decisions/{decision_id}",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED
)
def create_approval(
    decision_id: int,
    approval_data: ApprovalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check decision
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    # Check reviewer
    reviewer = (
        db.query(User)
        .filter(User.id == approval_data.reviewer_id)
        .first()
    )

    if not reviewer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reviewer not found"
        )

    # Create approval
    approval = Approval(
        decision_id=decision_id,
        reviewer_id=approval_data.reviewer_id,
        approval_level=approval_data.approval_level,
        status=ApprovalStatus.PENDING
    )

    db.add(approval)
    db.flush()

    # Create activity log automatically
    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="approval_assigned",
        entity_type="approval",
        entity_id=approval.id,
        description=(
            f"Assigned approval for decision: {decision.title} "
            f"to user ID {reviewer.id}"
        )
    )

    db.commit()
    db.refresh(approval)

    return approval


# ==========================================
# GET MY PENDING APPROVALS
# ==========================================
@router.get(
    "/pending",
    response_model=list[ApprovalResponse]
)
def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    approvals = (
        db.query(Approval)
        .filter(
            Approval.reviewer_id == current_user.id,
            Approval.status == ApprovalStatus.PENDING
        )
        .order_by(Approval.created_at.desc())
        .all()
    )

    return approvals


# ==========================================
# APPROVE OR REJECT
# ==========================================
@router.patch(
    "/{approval_id}",
    response_model=ApprovalResponse
)
def update_approval(
    approval_id: int,
    approval_data: ApprovalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    approval = (
        db.query(Approval)
        .filter(Approval.id == approval_id)
        .first()
    )

    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )

    # Only assigned reviewer can take action
    if approval.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this approval"
        )

    # Cannot update completed approval
    if approval.status != ApprovalStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This approval has already been completed"
        )

    # Only APPROVED or REJECTED allowed
    if approval_data.status not in [
        ApprovalStatus.APPROVED,
        ApprovalStatus.REJECTED
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval status must be APPROVED or REJECTED"
        )

    approval.status = approval_data.status

    db.flush()

    # Get decision for activity description
    decision = (
        db.query(Decision)
        .filter(Decision.id == approval.decision_id)
        .first()
    )

    if approval_data.status == ApprovalStatus.APPROVED:
        action = "approved"
        description = (
            f"Approved decision: "
            f"{decision.title if decision else approval.decision_id}"
        )
    else:
        action = "rejected"
        description = (
            f"Rejected decision: "
            f"{decision.title if decision else approval.decision_id}"
        )

    # Automatic activity logging
    create_activity_log(
        db=db,
        user_id=current_user.id,
        action=action,
        entity_type="approval",
        entity_id=approval.id,
        description=description
    )

    db.commit()
    db.refresh(approval)

    return approval