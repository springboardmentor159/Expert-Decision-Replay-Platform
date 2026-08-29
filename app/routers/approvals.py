from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user

from app.models.approval import Approval
from app.models.decision import Decision
from app.models.decision_activity import DecisionActivity
from app.models.activity_log import ActivityLog
from app.models.user import User

from app.schemas.approval import (
    ApprovalCreate,
    ApprovalResponse
)


router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"]
)


def get_role(current_user):
    return str(current_user.get("role", "")).lower()


# =========================================================
# ASSIGN APPROVAL
# =========================================================

@router.post(
    "",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED
)
def create_approval(
    data: ApprovalCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    role = get_role(current_user)

    if role not in ["manager", "administrator", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only managers or administrators can assign approvals"
        )

    decision = (
        db.query(Decision)
        .filter(Decision.id == data.decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    reviewer = (
        db.query(User)
        .filter(User.id == data.assigned_to)
        .first()
    )

    if reviewer is None:
        raise HTTPException(
            status_code=404,
            detail="Assigned reviewer not found"
        )

    approval = Approval(
        decision_id=data.decision_id,
        assigned_to=data.assigned_to,
        approval_level=data.approval_level,
        status="Pending"
    )

    db.add(approval)
    db.commit()
    db.refresh(approval)

    # Decision timeline
    activity = DecisionActivity(
        decision_id=decision.id,
        activity_type="Approval Assigned",
        description=f"Approval assigned to user {data.assigned_to}",
        created_by=int(current_user["sub"])
    )

    db.add(activity)

    # Organization activity
    log = ActivityLog(
        user_id=int(current_user["sub"]),
        action="Approval Assigned",
        entity_type="Approval",
        entity_id=approval.id,
        description=f"Approval assigned for Decision {decision.id}"
    )

    db.add(log)

    db.commit()

    return approval


# =========================================================
# GET ALL APPROVALS
# =========================================================

@router.get(
    "",
    response_model=list[ApprovalResponse]
)
def get_approvals(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    approvals = db.query(Approval).all()

    return approvals


# =========================================================
# GET MY PENDING APPROVALS
# =========================================================

@router.get(
    "/pending",
    response_model=list[ApprovalResponse]
)
def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user_id = int(current_user["sub"])

    approvals = (
        db.query(Approval)
        .filter(
            Approval.assigned_to == user_id,
            Approval.status == "Pending"
        )
        .order_by(Approval.created_at.desc())
        .all()
    )

    return approvals


# =========================================================
# APPROVE
# =========================================================

@router.patch(
    "/{approval_id}/approve",
    response_model=ApprovalResponse
)
def approve(
    approval_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user_id = int(current_user["sub"])

    approval = (
        db.query(Approval)
        .filter(Approval.id == approval_id)
        .first()
    )

    if approval is None:
        raise HTTPException(
            status_code=404,
            detail="Approval not found"
        )

    if approval.assigned_to != user_id:
        raise HTTPException(
            status_code=403,
            detail="You are not assigned to this approval"
        )

    if approval.status != "Pending":
        raise HTTPException(
            status_code=400,
            detail="Approval has already been completed"
        )

    approval.status = "Approved"
    approval.completed_at = datetime.utcnow()

    decision = (
        db.query(Decision)
        .filter(Decision.id == approval.decision_id)
        .first()
    )

    if decision:
        pending_count = (
            db.query(Approval)
            .filter(
                Approval.decision_id == decision.id,
                Approval.status == "Pending",
                Approval.id != approval.id
            )
            .count()
        )

        if pending_count == 0:
            decision.status = "Approved"

        activity = DecisionActivity(
            decision_id=decision.id,
            activity_type="Approval Completed",
            description="Decision approval completed",
            created_by=user_id
        )

        db.add(activity)

    log = ActivityLog(
        user_id=user_id,
        action="Approval",
        entity_type="Approval",
        entity_id=approval.id,
        description=f"Approval {approval.id} approved"
    )

    db.add(log)

    db.commit()
    db.refresh(approval)

    return approval


# =========================================================
# REJECT
# =========================================================

@router.patch(
    "/{approval_id}/reject",
    response_model=ApprovalResponse
)
def reject(
    approval_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user_id = int(current_user["sub"])

    approval = (
        db.query(Approval)
        .filter(Approval.id == approval_id)
        .first()
    )

    if approval is None:
        raise HTTPException(
            status_code=404,
            detail="Approval not found"
        )

    if approval.assigned_to != user_id:
        raise HTTPException(
            status_code=403,
            detail="You are not assigned to this approval"
        )

    if approval.status != "Pending":
        raise HTTPException(
            status_code=400,
            detail="Approval has already been completed"
        )

    approval.status = "Rejected"
    approval.completed_at = datetime.utcnow()

    decision = (
        db.query(Decision)
        .filter(Decision.id == approval.decision_id)
        .first()
    )

    if decision:
        decision.status = "Rejected"

        activity = DecisionActivity(
            decision_id=decision.id,
            activity_type="Approval Rejected",
            description="Decision approval rejected",
            created_by=user_id
        )

        db.add(activity)

    log = ActivityLog(
        user_id=user_id,
        action="Rejection",
        entity_type="Approval",
        entity_id=approval.id,
        description=f"Approval {approval.id} rejected"
    )

    db.add(log)

    db.commit()
    db.refresh(approval)

    return approval