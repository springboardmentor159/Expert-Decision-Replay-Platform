from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.decision import Decision
from app.models.approval import Approval
from app.services.activity import create_activity
from app.services.audit import create_audit_log


router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"],
)


# ============================================================
# CREATE / ASSIGN APPROVAL
# ============================================================

@router.post("/{decision_id}", status_code=status.HTTP_201_CREATED)
def create_approval(
    decision_id: int,
    reviewer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found",
        )

    reviewer = (
        db.query(User)
        .filter(User.id == reviewer_id)
        .first()
    )

    if not reviewer:
        raise HTTPException(
            status_code=404,
            detail="Reviewer not found",
        )

    approval = Approval(
        decision_id=decision_id,
        reviewer_id=reviewer_id,
        status="Pending",
    )

    db.add(approval)
    db.flush()

    # Audit: approval assigned
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"Approval {approval.id} assigned for "
            f"Decision {decision_id} to User {reviewer_id}"
        ),
        new_value={
            "decision_id": decision_id,
            "reviewer_id": reviewer_id,
            "status": "Pending",
        },
        request_method="POST",
        endpoint=f"/approvals/{decision_id}",
    )

    create_activity(
        db=db,
        user_id=current_user.id,
        action="Approval assigned",
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"Approval {approval.id} assigned for "
            f"Decision {decision_id} to User {reviewer_id}"
        ),
    )

    db.commit()
    db.refresh(approval)

    return approval


# ============================================================
# MY PENDING APPROVALS
# ============================================================

@router.get("/pending")
def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    approvals = (
        db.query(Approval)
        .filter(
            Approval.reviewer_id == current_user.id,
            Approval.status == "Pending",
        )
        .order_by(Approval.created_at.desc())
        .all()
    )

    return approvals


# ============================================================
# APPROVE
# ============================================================

@router.patch("/{approval_id}/approve")
def approve(
    approval_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    approval = (
        db.query(Approval)
        .filter(Approval.id == approval_id)
        .first()
    )

    if not approval:
        raise HTTPException(
            status_code=404,
            detail="Approval not found",
        )

    if approval.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to approve this request",
        )

    if approval.status != "Pending":
        raise HTTPException(
            status_code=400,
            detail="Approval is already completed",
        )

    # Capture old value before modification
    old_value = {
        "decision_id": approval.decision_id,
        "reviewer_id": approval.reviewer_id,
        "status": approval.status,
        "completed_at": (
            approval.completed_at.isoformat()
            if approval.completed_at
            else None
        ),
    }

    approval.status = "Approved"
    approval.completed_at = datetime.utcnow()

    decision = (
        db.query(Decision)
        .filter(Decision.id == approval.decision_id)
        .first()
    )

    if decision:
        decision.status = "Approved"

    db.flush()

    # Audit: approval approved
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="APPROVE",
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"User {current_user.id} approved "
            f"Approval {approval.id}"
        ),
        old_value=old_value,
        new_value={
            "decision_id": approval.decision_id,
            "reviewer_id": approval.reviewer_id,
            "status": "Approved",
            "completed_at": approval.completed_at.isoformat(),
        },
        request_method="PATCH",
        endpoint=f"/approvals/{approval_id}/approve",
    )

    create_activity(
        db=db,
        user_id=current_user.id,
        action="Approval",
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"User {current_user.id} approved "
            f"Approval {approval.id}"
        ),
    )

    db.commit()
    db.refresh(approval)

    return approval


# ============================================================
# REJECT
# ============================================================

@router.patch("/{approval_id}/reject")
def reject(
    approval_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    approval = (
        db.query(Approval)
        .filter(Approval.id == approval_id)
        .first()
    )

    if not approval:
        raise HTTPException(
            status_code=404,
            detail="Approval not found",
        )

    if approval.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to reject this request",
        )

    if approval.status != "Pending":
        raise HTTPException(
            status_code=400,
            detail="Approval is already completed",
        )

    # Capture old value before modification
    old_value = {
        "decision_id": approval.decision_id,
        "reviewer_id": approval.reviewer_id,
        "status": approval.status,
        "completed_at": (
            approval.completed_at.isoformat()
            if approval.completed_at
            else None
        ),
    }

    approval.status = "Rejected"
    approval.completed_at = datetime.utcnow()

    decision = (
        db.query(Decision)
        .filter(Decision.id == approval.decision_id)
        .first()
    )

    if decision:
        decision.status = "Rejected"

    db.flush()

    # Audit: approval rejected
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="REJECT",
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"User {current_user.id} rejected "
            f"Approval {approval.id}"
        ),
        old_value=old_value,
        new_value={
            "decision_id": approval.decision_id,
            "reviewer_id": approval.reviewer_id,
            "status": "Rejected",
            "completed_at": approval.completed_at.isoformat(),
        },
        request_method="PATCH",
        endpoint=f"/approvals/{approval_id}/reject",
    )

    create_activity(
        db=db,
        user_id=current_user.id,
        action="Rejection",
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"User {current_user.id} rejected "
            f"Approval {approval.id}"
        ),
    )

    db.commit()
    db.refresh(approval)

    return approval