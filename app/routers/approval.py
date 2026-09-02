from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user

from app.models.approval import Approval
from app.models.decision import Decision
from app.models.decision_version import DecisionVersion
from app.models.user import User

from app.schemas.approval import (
    ApprovalCreate,
    ApprovalResponse,
    ApprovalAction,
)

from app.services.activity import create_activity_log
from app.services.audit import create_audit_log


router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"],
)


# ---------------------------------------------------------
# ASSIGN APPROVAL
# ---------------------------------------------------------
@router.post(
    "",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_approval(
    approval_data: ApprovalCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role not in [
        "Manager",
        "Admin",
        "Administrator",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Manager or Admin can assign approvals",
        )

    decision = (
        db.query(Decision)
        .filter(Decision.id == approval_data.decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    reviewer = (
        db.query(User)
        .filter(User.id == approval_data.assigned_reviewer_id)
        .first()
    )

    if not reviewer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reviewer not found",
        )

    if reviewer.role != "Reviewer":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assigned user must have Reviewer role",
        )

    approval = Approval(
        decision_id=approval_data.decision_id,
        assigned_reviewer_id=approval_data.assigned_reviewer_id,
        approval_level=approval_data.approval_level,
        status="Pending",
    )

    db.add(approval)
    db.flush()

    # Existing Sprint 10 activity logging
    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="assigned",
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"User {current_user.id} assigned Approval "
            f"{approval.id} for Decision {approval.decision_id} "
            f"to Reviewer {reviewer.id}"
        ),
    )

    # Sprint 11 audit logging
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Approval",
        entity_id=approval.id,
        decision_id=approval.decision_id,
        description=(
            f"Approval {approval.id} assigned for "
            f"Decision {approval.decision_id}"
        ),
        ip_address=(
            request.client.host
            if request.client
            else None
        ),
        new_value={
            "id": approval.id,
            "decision_id": approval.decision_id,
            "assigned_reviewer_id": approval.assigned_reviewer_id,
            "approval_level": approval.approval_level,
            "status": approval.status,
        },
        request_method=request.method,
        endpoint=request.url.path,
    )

    db.commit()
    db.refresh(approval)

    return approval


# ---------------------------------------------------------
# GET PENDING APPROVALS
# ---------------------------------------------------------
@router.get(
    "/pending",
    response_model=list[ApprovalResponse],
)
def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "Reviewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Reviewers can view pending approvals",
        )

    approvals = (
        db.query(Approval)
        .filter(
            Approval.assigned_reviewer_id == current_user.id,
            Approval.status == "Pending",
        )
        .order_by(Approval.created_at.desc())
        .all()
    )

    return approvals


# ---------------------------------------------------------
# APPROVE / REJECT
# ---------------------------------------------------------
@router.patch(
    "/{approval_id}",
    response_model=ApprovalResponse,
)
def complete_approval(
    approval_id: int,
    action: ApprovalAction,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "Reviewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Reviewers can approve or reject",
        )

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

    if approval.assigned_reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this approval",
        )

    if approval.status != "Pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval is already completed",
        )

    new_status = action.status.strip().capitalize()

    if new_status not in ["Approved", "Rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be Approved or Rejected",
        )

    # -----------------------------------------------------
    # Get Decision BEFORE capturing old values
    # -----------------------------------------------------
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

    # -----------------------------------------------------
    # Capture old values
    # -----------------------------------------------------
    old_value = {
        "id": approval.id,
        "decision_id": approval.decision_id,
        "assigned_reviewer_id": approval.assigned_reviewer_id,
        "approval_level": approval.approval_level,
        "status": approval.status,
    }

    old_decision_status = decision.status

    # -----------------------------------------------------
    # Update Approval
    # -----------------------------------------------------
    approval.status = new_status
    approval.completed_at = datetime.now(timezone.utc)

    # -----------------------------------------------------
    # Update Decision status
    # -----------------------------------------------------
    decision.status = new_status

    db.flush()

    # -----------------------------------------------------
    # Create next Decision Version
    # -----------------------------------------------------
    latest_version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision.id
        )
        .order_by(
            DecisionVersion.version_number.desc()
        )
        .first()
    )

    next_version_number = (
        latest_version.version_number + 1
        if latest_version
        else 1
    )

    new_version = DecisionVersion(
        decision_id=decision.id,
        version_number=next_version_number,
        title=decision.title,
        problem_statement=decision.problem_statement,
        description=None,
        category=decision.category,
        status=decision.status,
        created_by=current_user.id,
    )

    db.add(new_version)

    # -----------------------------------------------------
    # New Approval values
    # -----------------------------------------------------
    new_value = {
        "id": approval.id,
        "decision_id": approval.decision_id,
        "assigned_reviewer_id": approval.assigned_reviewer_id,
        "approval_level": approval.approval_level,
        "status": approval.status,
    }

    client_ip = (
        request.client.host
        if request.client
        else None
    )

    # -----------------------------------------------------
    # Existing Sprint 10 Activity Log
    # -----------------------------------------------------
    create_activity_log(
        db=db,
        user_id=current_user.id,
        action=new_status.lower(),
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"User {current_user.id} {new_status.lower()} "
            f"Approval {approval.id} for Decision "
            f"{approval.decision_id}"
        ),
    )

    # -----------------------------------------------------
    # Sprint 11 Approval Audit
    # -----------------------------------------------------
    audit_action = (
        "APPROVE"
        if new_status == "Approved"
        else "REJECT"
    )

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=audit_action,
        entity_type="Approval",
        entity_id=approval.id,
        decision_id=approval.decision_id,
        description=(
            f"Approval {approval.id} {new_status.lower()} "
            f"for Decision {approval.decision_id}"
        ),
        ip_address=client_ip,
        old_value=old_value,
        new_value=new_value,
        request_method=request.method,
        endpoint=request.url.path,
    )

    # -----------------------------------------------------
    # Sprint 11 Decision Audit
    # -----------------------------------------------------
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=audit_action,
        entity_type="Decision",
        entity_id=decision.id,
        decision_id=decision.id,
        description=(
            f"Decision '{decision.title}' was "
            f"{new_status.lower()} through Approval "
            f"{approval.id} "
            f"(status changed from "
            f"'{old_decision_status}' to "
            f"'{decision.status}')"
        ),
        ip_address=client_ip,
        old_value={
            "status": old_decision_status,
        },
        new_value={
            "status": decision.status,
        },
        request_method=request.method,
        endpoint=request.url.path,
    )

    # -----------------------------------------------------
    # Commit everything together
    # -----------------------------------------------------
    db.commit()
    db.refresh(approval)

    return approval