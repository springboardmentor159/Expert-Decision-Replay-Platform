from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User

from app.schemas.approval import (
    ApprovalResponse,
    ApprovalStatus,
    ApprovalLevel,
)

from app.core.dependencies import (
    get_current_user,
    require_role,
)

from app.services.activity_log_service import create_activity_log


router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"],
)


# ---------------------------------------------------------
# SUBMIT DECISION FOR APPROVAL
# ---------------------------------------------------------

@router.post(
    "/decisions/{decision_id}/submit",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_decision_for_approval(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_role("Employee")
    ),
):
    user_id = int(current_user["sub"])

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

    # Only the creator can submit the decision
    if decision.created_by != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only submit your own decisions",
        )

    # Decision must be in Draft status
    if decision.status != "Draft":
        raise HTTPException(
            status_code=400,
            detail="Only Draft decisions can be submitted for approval",
        )

    # Find an available reviewer
    reviewer = (
        db.query(User)
        .filter(User.role == "Reviewer")
        .first()
    )

    if not reviewer:
        raise HTTPException(
            status_code=400,
            detail="No reviewer is available",
        )

    # Create approval record
    approval = Approval(
        decision_id=decision.id,
        assigned_to=reviewer.id,
        approval_level=ApprovalLevel.REVIEWER.value,
        status=ApprovalStatus.PENDING.value,
    )

    db.add(approval)

    # Update decision status
    old_status = decision.status
    decision.status = "Under Review"

    db.commit()
    db.refresh(approval)

    # Activity: approval assignment
    create_activity_log(
        db=db,
        user_id=user_id,
        action="APPROVAL_ASSIGNMENT",
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"Decision {decision.id} submitted for review "
            f"and assigned to reviewer {reviewer.id}"
        ),
    )

    # Activity: decision status change
    create_activity_log(
        db=db,
        user_id=user_id,
        action="STATUS_CHANGE",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"Changed decision status from "
            f"{old_status} to {decision.status}"
        ),
    )

    return approval


# ---------------------------------------------------------
# GET PENDING APPROVALS FOR REVIEWER
# ---------------------------------------------------------

@router.get(
    "/pending",
    response_model=list[ApprovalResponse],
)
def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_role("Reviewer")
    ),
):
    user_id = int(current_user["sub"])

    approvals = (
        db.query(Approval)
        .filter(
            Approval.assigned_to == user_id,
            Approval.status == ApprovalStatus.PENDING.value,
        )
        .order_by(Approval.created_at.desc())
        .all()
    )

    return approvals


# ---------------------------------------------------------
# APPROVE
# ---------------------------------------------------------

@router.patch(
    "/{approval_id}/approve",
    response_model=ApprovalResponse,
)
def approve_decision(
    approval_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_role("Reviewer")
    ),
):
    user_id = int(current_user["sub"])

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

    # Only assigned reviewer can approve
    if approval.assigned_to != user_id:
        raise HTTPException(
            status_code=403,
            detail="You are not assigned to this approval",
        )

    if approval.status != ApprovalStatus.PENDING.value:
        raise HTTPException(
            status_code=400,
            detail="Approval has already been completed",
        )

    decision = (
        db.query(Decision)
        .filter(Decision.id == approval.decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found",
        )

    approval.status = ApprovalStatus.APPROVED.value
    approval.completed_at = datetime.utcnow()

    decision.status = "Approved"

    db.commit()
    db.refresh(approval)

    create_activity_log(
        db=db,
        user_id=user_id,
        action="APPROVAL",
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"Approved decision {decision.id}"
        ),
    )

    create_activity_log(
        db=db,
        user_id=user_id,
        action="STATUS_CHANGE",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            "Changed decision status from Under Review to Approved"
        ),
    )

    return approval


# ---------------------------------------------------------
# REJECT
# ---------------------------------------------------------

@router.patch(
    "/{approval_id}/reject",
    response_model=ApprovalResponse,
)
def reject_decision(
    approval_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_role("Reviewer")
    ),
):
    user_id = int(current_user["sub"])

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

    # Only assigned reviewer can reject
    if approval.assigned_to != user_id:
        raise HTTPException(
            status_code=403,
            detail="You are not assigned to this approval",
        )

    if approval.status != ApprovalStatus.PENDING.value:
        raise HTTPException(
            status_code=400,
            detail="Approval has already been completed",
        )

    decision = (
        db.query(Decision)
        .filter(Decision.id == approval.decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found",
        )

    approval.status = ApprovalStatus.REJECTED.value
    approval.completed_at = datetime.utcnow()

    decision.status = "Rejected"

    db.commit()
    db.refresh(approval)

    create_activity_log(
        db=db,
        user_id=user_id,
        action="REJECTION",
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"Rejected decision {decision.id}"
        ),
    )

    create_activity_log(
        db=db,
        user_id=user_id,
        action="STATUS_CHANGE",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            "Changed decision status from Under Review to Rejected"
        ),
    )

    return approval