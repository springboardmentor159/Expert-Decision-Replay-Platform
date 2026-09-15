from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User
from app.schemas.approval import ApprovalCreate, ApprovalResponse
from app.core.dependencies import get_current_user
from app.core.audit_logger import create_audit_log
from app.core.notification_service import create_notification


router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"],
)


# =========================================================
# CREATE APPROVAL
# =========================================================

@router.post(
    "/",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_approval(
    approval: ApprovalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == approval.decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    if approval.approval_level not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only approval levels 1 and 2 are supported",
        )

    reviewer = (
        db.query(User)
        .filter(User.id == approval.reviewer_id)
        .first()
    )

    if not reviewer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned approval user not found",
        )

    reviewer_role = (
        reviewer.role.value
        if hasattr(reviewer.role, "value")
        else reviewer.role
    )

    if approval.approval_level == 1 and reviewer_role != "Reviewer":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Level 1 approval must be assigned to a Reviewer",
        )

    if approval.approval_level == 2 and reviewer_role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Level 2 approval must be assigned to a Manager",
        )

    if approval.approval_level == 2:
        level_one_approval = (
            db.query(Approval)
            .filter(
                Approval.decision_id == approval.decision_id,
                Approval.approval_level == 1,
            )
            .order_by(Approval.id.desc())
            .first()
        )

        if not level_one_approval:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Level 1 approval must be created first",
            )

        if level_one_approval.status != "Approved":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Manager approval is allowed only after Reviewer approval",
            )

    existing_approval = (
        db.query(Approval)
        .filter(
            Approval.decision_id == approval.decision_id,
            Approval.reviewer_id == approval.reviewer_id,
            Approval.approval_level == approval.approval_level,
            Approval.status == "Pending",
        )
        .first()
    )

    if existing_approval:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pending approval already exists for this user",
        )

    # Default deadline: 24 hours from current local time
    deadline = approval.due_at or (
        datetime.now() + timedelta(hours=24)
    )

    db_approval = Approval(
        decision_id=approval.decision_id,
        reviewer_id=approval.reviewer_id,
        approval_level=approval.approval_level,
        status="Pending",
        due_at=deadline,
        escalated=False,
    )

    db.add(db_approval)
    db.commit()
    db.refresh(db_approval)

    create_notification(
        db=db,
        user_id=reviewer.id,
        title="New Approval Assigned",
        message=(
            f"You have a new approval request for "
            f"Decision {decision.id}. "
            f"Deadline: {deadline}"
        ),
        notification_type="APPROVAL",
    )

    db.commit()

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
            "status": db_approval.status,
            "due_at": (
                db_approval.due_at.isoformat()
                if db_approval.due_at
                else None
            ),
        },
        request_method="POST",
        endpoint="/approvals/",
    )

    db.commit()

    return db_approval


# =========================================================
# GET PENDING APPROVALS
# =========================================================

@router.get(
    "/pending",
    response_model=list[ApprovalResponse],
)
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
        .all()
    )

    return approvals


# =========================================================
# ESCALATE OVERDUE APPROVALS
# =========================================================

@router.post(
    "/escalate-overdue",
)
def escalate_overdue_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user_role = (
        current_user.role.value
        if hasattr(current_user.role, "value")
        else current_user.role
    )

    if current_user_role not in ["Admin", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admin or Manager can escalate approvals",
        )

    # Use local system time consistently with due_at
    now = datetime.now()

    overdue_approvals = (
        db.query(Approval)
        .filter(
            Approval.status == "Pending",
            Approval.due_at.isnot(None),
            Approval.due_at < now,
            Approval.escalated == False,
        )
        .all()
    )

    escalated_count = 0

    for approval in overdue_approvals:
        approval.escalated = True
        approval.escalated_at = now
        approval.escalation_reason = "Approval deadline exceeded"

        create_notification(
            db=db,
            user_id=approval.reviewer_id,
            title="Approval Escalated",
            message=(
                f"Approval {approval.id} for Decision "
                f"{approval.decision_id} has been escalated "
                f"because the deadline was exceeded."
            ),
            notification_type="ESCALATION",
        )

        create_audit_log(
            db=db,
            user_id=current_user.id,
            action="UPDATE",
            entity_type="Approval",
            entity_id=approval.id,
            description=(
                f"Approval {approval.id} escalated because "
                f"the deadline was exceeded"
            ),
            old_value={
                "status": approval.status,
                "escalated": False,
            },
            new_value={
                "status": approval.status,
                "escalated": True,
                "escalation_reason": approval.escalation_reason,
            },
            request_method="POST",
            endpoint="/approvals/escalate-overdue",
        )

        escalated_count += 1

    db.commit()

    return {
        "message": "Overdue approval escalation completed",
        "escalated_count": escalated_count,
    }


# =========================================================
# APPROVE DECISION
# =========================================================

@router.put(
    "/{approval_id}/approve",
    response_model=ApprovalResponse,
)
def approve_decision(
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found",
        )

    if approval.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to approve this request",
        )

    if approval.status != "Pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval is already completed",
        )

    current_user_role = (
        current_user.role.value
        if hasattr(current_user.role, "value")
        else current_user.role
    )

    if approval.approval_level == 1 and current_user_role != "Reviewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only a Reviewer can approve level 1 approval",
        )

    if approval.approval_level == 2 and current_user_role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only a Manager can approve level 2 approval",
        )

    if approval.approval_level == 2:
        level_one_approval = (
            db.query(Approval)
            .filter(
                Approval.decision_id == approval.decision_id,
                Approval.approval_level == 1,
            )
            .order_by(Approval.id.desc())
            .first()
        )

        if not level_one_approval:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Level 1 Reviewer approval not found",
            )

        if level_one_approval.status != "Approved":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reviewer must approve before Manager approval",
            )

    decision = (
        db.query(Decision)
        .filter(Decision.id == approval.decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    old_status = approval.status
    old_decision_status = decision.status

    approval.status = "Approved"
    approval.completed_at = datetime.now()

    db.commit()
    db.refresh(approval)

    all_approvals = (
        db.query(Approval)
        .filter(Approval.decision_id == approval.decision_id)
        .all()
    )

    has_rejected = any(
        item.status == "Rejected"
        for item in all_approvals
    )

    level_one_approved = any(
        item.approval_level == 1
        and item.status == "Approved"
        for item in all_approvals
    )

    level_two_approved = any(
        item.approval_level == 2
        and item.status == "Approved"
        for item in all_approvals
    )

    has_level_two = any(
        item.approval_level == 2
        for item in all_approvals
    )

    if has_rejected:
        decision.status = "Rejected"

    elif has_level_two:
        if level_one_approved and level_two_approved:
            decision.status = "Approved"
        else:
            decision.status = "Under Review"

    else:
        if level_one_approved:
            decision.status = "Approved"
        else:
            decision.status = "Under Review"

    db.commit()
    db.refresh(decision)

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
            "status": old_status,
        },
        new_value={
            "status": approval.status,
            "completed_at": (
                approval.completed_at.isoformat()
                if approval.completed_at
                else None
            ),
        },
        request_method="PUT",
        endpoint=f"/approvals/{approval_id}/approve",
    )

    if old_decision_status != decision.status:
        create_audit_log(
            db=db,
            user_id=current_user.id,
            action="APPROVE",
            entity_type="Decision",
            entity_id=decision.id,
            description=(
                f"Decision {decision.id} status changed "
                f"from {old_decision_status} to {decision.status}"
            ),
            old_value={
                "status": old_decision_status,
            },
            new_value={
                "status": decision.status,
            },
            request_method="PUT",
            endpoint=f"/approvals/{approval_id}/approve",
        )

    db.commit()

    return approval


# =========================================================
# REJECT DECISION
# =========================================================

@router.put(
    "/{approval_id}/reject",
    response_model=ApprovalResponse,
)
def reject_decision(
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found",
        )

    if approval.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to reject this request",
        )

    if approval.status != "Pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval is already completed",
        )

    current_user_role = (
        current_user.role.value
        if hasattr(current_user.role, "value")
        else current_user.role
    )

    if approval.approval_level == 1 and current_user_role != "Reviewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only a Reviewer can reject level 1 approval",
        )

    if approval.approval_level == 2 and current_user_role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only a Manager can reject level 2 approval",
        )

    decision = (
        db.query(Decision)
        .filter(Decision.id == approval.decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    old_status = approval.status
    old_decision_status = decision.status

    approval.status = "Rejected"
    approval.completed_at = datetime.now()

    decision.status = "Rejected"

    db.commit()
    db.refresh(approval)
    db.refresh(decision)

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
            "status": old_status,
        },
        new_value={
            "status": approval.status,
            "completed_at": (
                approval.completed_at.isoformat()
                if approval.completed_at
                else None
            ),
        },
        request_method="PUT",
        endpoint=f"/approvals/{approval_id}/reject",
    )

    if old_decision_status != decision.status:
        create_audit_log(
            db=db,
            user_id=current_user.id,
            action="REJECT",
            entity_type="Decision",
            entity_id=decision.id,
            description=(
                f"Decision {decision.id} status changed "
                f"from {old_decision_status} to Rejected"
            ),
            old_value={
                "status": old_decision_status,
            },
            new_value={
                "status": decision.status,
            },
            request_method="PUT",
            endpoint=f"/approvals/{approval_id}/reject",
        )

    db.commit()

    return approval