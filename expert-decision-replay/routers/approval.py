from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User
from app.schemas.approval import ApprovalCreate, ApprovalResponse
from app.core.dependencies import get_current_user
from app.core.audit_logger import create_audit_log


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

    # =====================================================
    # AUTOMATIC AUDIT LOG - CREATE APPROVAL
    # =====================================================

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Approval",
        entity_id=db_approval.id,
        description=(
            f"Approval {db_approval.id} created "
            f"for decision {db_approval.decision_id}"
        ),
        new_value={
            "decision_id": db_approval.decision_id,
            "reviewer_id": db_approval.reviewer_id,
            "approval_level": db_approval.approval_level,
            "status": db_approval.status
        },
        request_method="POST",
        endpoint="/approvals/"
    )

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

    # Store old status
    old_status = approval.status

    # -----------------------------------------------------
    # Approve
    # -----------------------------------------------------

    approval.status = "Approved"
    approval.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(approval)

    # =====================================================
    # AUTOMATIC AUDIT LOG - APPROVE
    # =====================================================

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="APPROVE",
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"Approval {approval.id} approved "
            f"for decision {approval.decision_id}"
        ),
        old_value={
            "status": old_status
        },
        new_value={
            "status": approval.status,
            "completed_at": (
                approval.completed_at.isoformat()
                if approval.completed_at
                else None
            )
        },
        request_method="PUT",
        endpoint=f"/approvals/{approval_id}/approve"
    )

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

    # Store old status
    old_status = approval.status

    # -----------------------------------------------------
    # Reject
    # -----------------------------------------------------

    approval.status = "Rejected"
    approval.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(approval)

    # =====================================================
    # AUTOMATIC AUDIT LOG - REJECT
    # =====================================================

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="REJECT",
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"Approval {approval.id} rejected "
            f"for decision {approval.decision_id}"
        ),
        old_value={
            "status": old_status
        },
        new_value={
            "status": approval.status,
            "completed_at": (
                approval.completed_at.isoformat()
                if approval.completed_at
                else None
            )
        },
        request_method="PUT",
        endpoint=f"/approvals/{approval_id}/reject"
    )

    return approval