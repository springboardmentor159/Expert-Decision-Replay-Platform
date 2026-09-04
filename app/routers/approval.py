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
# HELPERS
# ---------------------------------------------------------
def create_decision_version(
    db: Session,
    decision: Decision,
    user_id: int,
) -> DecisionVersion:
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
        created_by=user_id,
    )

    db.add(new_version)

    return new_version


def get_client_ip(request: Request) -> str | None:
    return (
        request.client.host
        if request.client
        else None
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
    # Only Manager/Admin can create approval assignments.
    if current_user.role not in [
        "Manager",
        "Admin",
        "Administrator",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Manager or Admin can assign approvals",
        )

    # Only two approval levels are supported.
    if approval_data.approval_level not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="approval_level must be 1 for Reviewer or 2 for Manager",
        )

    decision = (
        db.query(Decision)
        .filter(
            Decision.id == approval_data.decision_id
        )
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    # Do not assign approvals after final decision.
    if decision.status in ["Approved", "Rejected", "Archived"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Cannot assign approval when decision status "
                f"is '{decision.status}'"
            ),
        )

    assignee = (
        db.query(User)
        .filter(
            User.id == approval_data.assigned_reviewer_id
        )
        .first()
    )

    if not assignee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found",
        )

    # Level 1 must be assigned to a Reviewer.
    if approval_data.approval_level == 1:
        if assignee.role != "Reviewer":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Level 1 approval must be assigned "
                    "to a Reviewer"
                ),
            )

    # Level 2 must be assigned to a Manager.
    if approval_data.approval_level == 2:
        if assignee.role != "Manager":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Level 2 approval must be assigned "
                    "to a Manager"
                ),
            )

    # Prevent duplicate pending approval at the same level.
    existing_pending = (
        db.query(Approval)
        .filter(
            Approval.decision_id == decision.id,
            Approval.approval_level
            == approval_data.approval_level,
            Approval.status == "Pending",
        )
        .first()
    )

    if existing_pending:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"A pending level "
                f"{approval_data.approval_level} approval "
                f"already exists for this decision"
            ),
        )

    approval = Approval(
        decision_id=decision.id,
        assigned_reviewer_id=approval_data.assigned_reviewer_id,
        approval_level=approval_data.approval_level,
        status="Pending",
    )

    db.add(approval)
    db.flush()

    level_name = (
        "Reviewer"
        if approval.approval_level == 1
        else "Manager"
    )

    # Activity log
    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="assigned",
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"User {current_user.id} assigned "
            f"level {approval.approval_level} "
            f"({level_name}) Approval {approval.id} "
            f"for Decision {approval.decision_id} "
            f"to User {assignee.id}"
        ),
    )

    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Approval",
        entity_id=approval.id,
        decision_id=approval.decision_id,
        description=(
            f"Level {approval.approval_level} "
            f"{level_name} approval {approval.id} "
            f"assigned for Decision {approval.decision_id}"
        ),
        ip_address=get_client_ip(request),
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
    # Reviewer can see level 1 approvals.
    # Manager can see level 2 approvals.
    if current_user.role == "Reviewer":
        approvals = (
            db.query(Approval)
            .filter(
                Approval.assigned_reviewer_id
                == current_user.id,
                Approval.approval_level == 1,
                Approval.status == "Pending",
            )
            .order_by(
                Approval.created_at.desc()
            )
            .all()
        )

        return approvals

    if current_user.role == "Manager":
        approvals = (
            db.query(Approval)
            .join(
                Decision,
                Approval.decision_id == Decision.id,
            )
            .join(
                User,
                Decision.created_by == User.id,
            )
            .filter(
                Approval.assigned_reviewer_id
                == current_user.id,
                Approval.approval_level == 2,
                Approval.status == "Pending",
            )
            .order_by(
                Approval.created_at.desc()
            )
            .all()
        )

        return approvals

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=(
            "Only Reviewers and Managers can "
            "view pending approvals"
        ),
    )


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
    approval = (
        db.query(Approval)
        .filter(
            Approval.id == approval_id
        )
        .first()
    )

    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found",
        )

    # -----------------------------------------------------
    # Validate role according to approval level
    # -----------------------------------------------------
    if approval.approval_level == 1:
        if current_user.role != "Reviewer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Only a Reviewer can complete "
                    "a level 1 approval"
                ),
            )

    elif approval.approval_level == 2:
        if current_user.role != "Manager":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Only a Manager can complete "
                    "a level 2 approval"
                ),
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid approval level",
        )

    # -----------------------------------------------------
    # Validate assignee
    # -----------------------------------------------------
    if approval.assigned_reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this approval",
        )

    # -----------------------------------------------------
    # Prevent duplicate completion
    # -----------------------------------------------------
    if approval.status != "Pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval is already completed",
        )

    # -----------------------------------------------------
    # Validate requested action
    # -----------------------------------------------------
    new_status = action.status.strip().capitalize()

    if new_status not in [
        "Approved",
        "Rejected",
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be Approved or Rejected",
        )

    # -----------------------------------------------------
    # Get Decision
    # -----------------------------------------------------
    decision = (
        db.query(Decision)
        .filter(
            Decision.id == approval.decision_id
        )
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    # -----------------------------------------------------
    # Validate decision state
    # -----------------------------------------------------
    if decision.status in [
        "Approved",
        "Rejected",
        "Archived",
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Cannot complete approval because "
                f"decision is already '{decision.status}'"
            ),
        )

    old_value = {
        "id": approval.id,
        "decision_id": approval.decision_id,
        "assigned_reviewer_id": approval.assigned_reviewer_id,
        "approval_level": approval.approval_level,
        "status": approval.status,
    }

    old_decision_status = decision.status

    # -----------------------------------------------------
    # Complete current approval
    # -----------------------------------------------------
    approval.status = new_status
    approval.completed_at = datetime.now(timezone.utc)

    # -----------------------------------------------------
    # REJECTION
    #
    # Either Reviewer or Manager rejection is final.
    # -----------------------------------------------------
    if new_status == "Rejected":
        decision.status = "Rejected"

        create_decision_version(
            db=db,
            decision=decision,
            user_id=current_user.id,
        )

    # -----------------------------------------------------
    # LEVEL 1 REVIEWER APPROVAL
    #
    # Reviewer approval does NOT mean final approval.
    # Decision remains Under Review until Manager approves.
    # -----------------------------------------------------
    elif approval.approval_level == 1:
        decision.status = "Under Review"

        create_decision_version(
            db=db,
            decision=decision,
            user_id=current_user.id,
        )

    # -----------------------------------------------------
    # LEVEL 2 MANAGER APPROVAL
    #
    # Manager approval is the final approval.
    # -----------------------------------------------------
    elif approval.approval_level == 2:
        # A Manager cannot approve unless the level 1
        # Reviewer approval has already been completed.
        reviewer_approval = (
            db.query(Approval)
            .filter(
                Approval.decision_id == decision.id,
                Approval.approval_level == 1,
            )
            .order_by(
                Approval.completed_at.desc()
            )
            .first()
        )

        if (
            not reviewer_approval
            or reviewer_approval.status != "Approved"
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Manager approval requires "
                    "completed Reviewer approval first"
                ),
            )

        decision.status = "Approved"

        create_decision_version(
            db=db,
            decision=decision,
            user_id=current_user.id,
        )

    db.flush()

    new_value = {
        "id": approval.id,
        "decision_id": approval.decision_id,
        "assigned_reviewer_id": approval.assigned_reviewer_id,
        "approval_level": approval.approval_level,
        "status": approval.status,
    }

    client_ip = get_client_ip(request)

    # -----------------------------------------------------
    # Activity Log
    # -----------------------------------------------------
    create_activity_log(
        db=db,
        user_id=current_user.id,
        action=new_status.lower(),
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"User {current_user.id} "
            f"{new_status.lower()} "
            f"level {approval.approval_level} "
            f"Approval {approval.id} "
            f"for Decision {approval.decision_id}"
        ),
    )

    # -----------------------------------------------------
    # Approval Audit
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
            f"Level {approval.approval_level} "
            f"Approval {approval.id} "
            f"{new_status.lower()} "
            f"for Decision {approval.decision_id}"
        ),
        ip_address=client_ip,
        old_value=old_value,
        new_value=new_value,
        request_method=request.method,
        endpoint=request.url.path,
    )

    # -----------------------------------------------------
    # Decision Audit
    # -----------------------------------------------------
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=(
            "STATUS_CHANGE"
            if new_status == "Approved"
            else "REJECT"
        ),
        entity_type="Decision",
        entity_id=decision.id,
        decision_id=decision.id,
        description=(
            f"Decision '{decision.title}' status changed "
            f"from '{old_decision_status}' to "
            f"'{decision.status}' through "
            f"Approval {approval.id}"
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