from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User
from app.schemas.approvals.approval import (
    ApprovalCreate,
    ApprovalResponse,
    ApprovalUpdate,
)
from app.schemas.audit_log import AuditAction, AuditEntityType
from app.services.activity_service import log_activity
from app.services.audit_service import log_audit


router = APIRouter(prefix="/approvals", tags=["Approvals"])

VALID_STATUSES = {"Pending", "Under Review", "Approved", "Rejected"}
FINAL_STATUSES = {"Approved", "Rejected"}


def get_decision_or_404(db: Session, decision_id: int) -> Decision:
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return decision


def get_approval_or_404(db: Session, approval_id: int) -> Approval:
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

    return approval


def get_decision_creator(db: Session, decision: Decision) -> User | None:
    return (
        db.query(User)
        .filter(User.id == decision.created_by)
        .first()
    )


def ensure_manager_department_access(
    db: Session,
    current_user: User,
    decision: Decision,
) -> None:
    current_role = (current_user.role or "").strip()

    if current_role != "Manager":
        return

    creator = get_decision_creator(db, decision)

    if not creator or creator.department != current_user.department:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage approvals for decisions in your department",
        )


def ensure_approval_view_access(
    db: Session,
    current_user: User,
    approval: Approval,
) -> Decision:
    current_role = (current_user.role or "").strip()

    decision = get_decision_or_404(
        db,
        approval.decision_id,
    )

    if current_role == "Employee":
        if decision.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        return decision

    if current_role == "Reviewer":
        if approval.reviewer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        return decision

    if current_role == "Manager":
        ensure_manager_department_access(
            db,
            current_user,
            decision,
        )

        return decision

    if current_role == "Administrator":
        return decision

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions",
    )


def ensure_reviewer_can_update(
    current_user: User,
    approval: Approval,
) -> None:
    current_role = (current_user.role or "").strip()

    if (
        current_role == "Reviewer"
        and approval.reviewer_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned reviewer can update this approval",
        )

    if current_role not in {
        "Reviewer",
        "Manager",
        "Administrator",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reviewer, Manager or Administrator access required",
        )


def ensure_approval_stage_can_change(
    db: Session,
    current_user: User,
    approval: Approval,
    new_status: str,
) -> None:
    current_role = (current_user.role or "").strip()

    if approval.status in FINAL_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A completed approval cannot be changed",
        )

    if new_status not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid approval status",
        )

    # Level 1 is the reviewer stage.
    if approval.approval_level == 1:
        if current_role not in {
            "Reviewer",
            "Manager",
            "Administrator",
        }:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this approval stage",
            )

        if (
            current_role == "Reviewer"
            and approval.reviewer_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the assigned reviewer can update this approval",
            )

    # Level 2 is the manager/final approval stage.
    elif approval.approval_level == 2:
        if current_role not in {
            "Manager",
            "Administrator",
        }:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only a manager or administrator can complete the final approval stage",
            )

        prior_approval = (
            db.query(Approval)
            .filter(
                Approval.decision_id == approval.decision_id,
                Approval.approval_level < approval.approval_level,
            )
            .order_by(
                Approval.approval_level.desc()
            )
            .first()
        )

        if (
            not prior_approval
            or prior_approval.status != "Approved"
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Complete the earlier approval stage before updating the final approval stage",
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Approval level must be 1 or 2",
        )

    # Reviewers may not perform final manager approval/rejection.
    if (
        current_role == "Reviewer"
        and approval.approval_level >= 2
        and new_status in FINAL_STATUSES
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only a manager can complete the final approval stage",
        )


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
    current_role = (current_user.role or "").strip()

    if current_role not in {
        "Manager",
        "Administrator",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or Administrator access required",
        )

    if approval_data.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid approval status",
        )

    if approval_data.approval_level not in {1, 2}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Approval level must be 1 or 2",
        )

    decision = get_decision_or_404(
        db,
        approval_data.decision_id,
    )

    if decision.status != "Under Review":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A decision must be submitted for review before approval stages can be assigned",
        )

    ensure_manager_department_access(
        db,
        current_user,
        decision,
    )

    reviewer = (
        db.query(User)
        .filter(User.id == approval_data.reviewer_id)
        .first()
    )

    if not reviewer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reviewer not found",
        )

    if reviewer.role not in {
        "Reviewer",
        "Manager",
        "Administrator",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected user cannot be an approval reviewer",
        )

    if (
        current_role == "Manager"
        and reviewer.department != current_user.department
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only assign users in your department",
        )

    # A final approval stage cannot be created before level 1 exists.
    if approval_data.approval_level == 2:
        first_level = (
            db.query(Approval)
            .filter(
                Approval.decision_id == decision.id,
                Approval.approval_level == 1,
            )
            .first()
        )

        if not first_level:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Create the level 1 approval before assigning the final approval stage",
            )

    existing = (
        db.query(Approval)
        .filter(
            Approval.decision_id == decision.id,
            Approval.approval_level == approval_data.approval_level,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Approval level {approval_data.approval_level} "
                "already exists for this decision"
            ),
        )

    approval = Approval(
        decision_id=decision.id,
        reviewer_id=reviewer.id,
        approval_level=approval_data.approval_level,
        status=approval_data.status,
        assigned_at=datetime.now(timezone.utc),
    )

    db.add(approval)
    db.flush()

    log_audit(
        db,
        current_user.id,
        AuditAction.CREATE,
        AuditEntityType.APPROVAL,
        approval.id,
        (
            f"Approval level {approval.approval_level} "
            f"assigned for Decision {decision.id}"
        ),
        new_value={
            "reviewer_id": reviewer.id,
            "approval_level": approval.approval_level,
            "status": approval.status,
        },
        request_method="POST",
        endpoint="/approvals",
    )

    log_activity(
        db,
        current_user.id,
        "Approval Assigned",
        "Approval",
        approval.id,
        (
            f"Approval level {approval.approval_level} "
            f"assigned for Decision {decision.id}"
        ),
    )

    db.commit()
    db.refresh(approval)

    return approval


@router.get(
    "",
    response_model=list[ApprovalResponse],
)
def get_approvals(
    decision_id: int | None = None,
    reviewer_id: int | None = None,
    approval_status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_role = (current_user.role or "").strip()

    query = db.query(Approval)

    if current_role == "Employee":
        query = (
            query
            .join(
                Decision,
                Approval.decision_id == Decision.id,
            )
            .filter(
                Decision.created_by == current_user.id,
            )
        )

    elif current_role == "Reviewer":
        query = query.filter(
            Approval.reviewer_id == current_user.id,
        )

    elif current_role == "Manager":
        query = (
            query
            .join(
                Decision,
                Approval.decision_id == Decision.id,
            )
            .join(
                User,
                Decision.created_by == User.id,
            )
            .filter(
                User.department == current_user.department,
            )
        )

    elif current_role != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    if decision_id is not None:
        query = query.filter(
            Approval.decision_id == decision_id,
        )

    if reviewer_id is not None:
        query = query.filter(
            Approval.reviewer_id == reviewer_id,
        )

    if approval_status:
        normalized_status = approval_status.strip()

        if normalized_status not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid approval status",
            )

        query = query.filter(
            Approval.status == normalized_status,
        )

    return (
        query
        .order_by(
            Approval.decision_id.asc(),
            Approval.approval_level.asc(),
            Approval.assigned_at.asc(),
        )
        .all()
    )


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
        db,
        approval_id,
    )

    ensure_approval_view_access(
        db,
        current_user,
        approval,
    )

    return approval


@router.patch(
    "/{approval_id}",
    response_model=ApprovalResponse,
)
def update_approval(
    approval_id: int,
    approval_data: ApprovalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    approval = get_approval_or_404(
        db,
        approval_id,
    )

    ensure_reviewer_can_update(
        current_user,
        approval,
    )

    decision = get_decision_or_404(
        db,
        approval.decision_id,
    )

    ensure_manager_department_access(
        db,
        current_user,
        decision,
    )

    if (
        approval_data.status is None
        and approval_data.completed_at is None
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide an approval status or completion time",
        )

    old_status = approval.status

    if approval_data.status is not None:
        new_status = approval_data.status

        ensure_approval_stage_can_change(
            db,
            current_user,
            approval,
            new_status,
        )

        # A reviewer can move level 1 through review and complete it.
        if (
            approval.approval_level == 1
            and current_user.role == "Reviewer"
            and new_status == "Rejected"
        ):
            decision.status = "Rejected"

        elif new_status == "Rejected":
            decision.status = "Rejected"

        elif (
            new_status == "Approved"
            and approval.approval_level == 1
        ):
            decision.status = "Under Review"

        elif (
            new_status == "Approved"
            and approval.approval_level == 2
        ):
            decision.status = "Approved"

        elif new_status == "Under Review":
            decision.status = "Under Review"

        elif new_status == "Pending":
            decision.status = "Under Review"

        approval.status = new_status

        if new_status in FINAL_STATUSES:
            approval.completed_at = (
                approval_data.completed_at
                or datetime.now(timezone.utc)
            )
        else:
            approval.completed_at = None

        if new_status == "Approved":
            audit_action = AuditAction.APPROVE
        elif new_status == "Rejected":
            audit_action = AuditAction.REJECT
        else:
            audit_action = AuditAction.UPDATE

        log_audit(
            db,
            current_user.id,
            audit_action,
            AuditEntityType.APPROVAL,
            approval.id,
            (
                f"Approval {approval.id} changed "
                f"from {old_status} to {approval.status}"
            ),
            old_value={
                "status": old_status,
            },
            new_value={
                "status": approval.status,
                "decision_status": decision.status,
            },
            request_method="PATCH",
            endpoint=f"/approvals/{approval.id}",
        )

        log_activity(
            db,
            current_user.id,
            f"Approval {new_status}",
            "Approval",
            approval.id,
            (
                f"Approval level {approval.approval_level} "
                f"for Decision {decision.id} marked {approval.status}"
            ),
        )

    elif approval_data.completed_at is not None:
        if approval.status not in FINAL_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Completion time can only be changed for a completed approval",
            )

        old_completed_at = approval.completed_at

        approval.completed_at = approval_data.completed_at

        log_audit(
            db,
            current_user.id,
            AuditAction.UPDATE,
            AuditEntityType.APPROVAL,
            approval.id,
            f"Completion time updated for Approval {approval.id}",
            old_value={
                "completed_at": (
                    old_completed_at.isoformat()
                    if old_completed_at
                    else None
                ),
            },
            new_value={
                "completed_at": (
                    approval_data.completed_at.isoformat()
                ),
            },
            request_method="PATCH",
            endpoint=f"/approvals/{approval.id}",
        )

    db.commit()
    db.refresh(approval)

    return approval