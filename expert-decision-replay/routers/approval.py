from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User
from app.schemas.approval import ApprovalCreate, ApprovalResponse
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"]
)


# =========================================================
# CREATE APPROVAL
# =========================================================

@router.post(
    "/",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED
)
def create_approval(
    approval: ApprovalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # -----------------------------------------------------
    # Check whether decision exists
    # -----------------------------------------------------

    decision = (
        db.query(Decision)
        .filter(Decision.id == approval.decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    # -----------------------------------------------------
    # Check whether reviewer exists
    # -----------------------------------------------------

    reviewer = (
        db.query(User)
        .filter(User.id == approval.reviewer_id)
        .first()
    )

    if not reviewer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reviewer not found"
        )

    # -----------------------------------------------------
    # Create approval
    # -----------------------------------------------------

    db_approval = Approval(
        decision_id=approval.decision_id,
        reviewer_id=approval.reviewer_id,
        approval_level=approval.approval_level,
        status="Pending"
    )

    db.add(db_approval)
    db.commit()
    db.refresh(db_approval)

    return db_approval


# =========================================================
# GET PENDING APPROVALS FOR CURRENT USER
# =========================================================

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
            Approval.status == "Pending"
        )
        .all()
    )

    return approvals


# =========================================================
# APPROVE DECISION
# =========================================================

@router.put(
    "/{approval_id}/approve",
    response_model=ApprovalResponse
)
def approve_decision(
    approval_id: int,
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

    # -----------------------------------------------------
    # Only assigned reviewer can approve
    # -----------------------------------------------------

    if approval.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to approve this request"
        )

    # -----------------------------------------------------
    # Check approval status
    # -----------------------------------------------------

    if approval.status != "Pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval is already completed"
        )

    # -----------------------------------------------------
    # Approve
    # -----------------------------------------------------

    approval.status = "Approved"
    approval.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(approval)

    return approval


# =========================================================
# REJECT DECISION
# =========================================================

@router.put(
    "/{approval_id}/reject",
    response_model=ApprovalResponse
)
def reject_decision(
    approval_id: int,
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

    # -----------------------------------------------------
    # Only assigned reviewer can reject
    # -----------------------------------------------------

    if approval.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to reject this request"
        )

    # -----------------------------------------------------
    # Check approval status
    # -----------------------------------------------------

    if approval.status != "Pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval is already completed"
        )

    # -----------------------------------------------------
    # Reject
    # -----------------------------------------------------

    approval.status = "Rejected"
    approval.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(approval)

    return approval