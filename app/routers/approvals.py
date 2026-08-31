from datetime import datetime
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.approval import (
    Approval,
    ApprovalStatus
)

from app.models.decision import Decision
from app.models.user import User

from app.core.enums import (
    UserRole,
    DecisionStatus
)

from app.core.security import get_current_user

from app.services.audit import log_audit


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"]
)


# =========================================================
# SCHEMAS
# =========================================================

class ApprovalCreate(BaseModel):

    decision_id: int = Field(
        ...,
        ge=1
    )

    assigned_to: int = Field(
        ...,
        ge=1
    )

    assigned_role: UserRole


class ApprovalReview(BaseModel):

    comments: Optional[str] = None


# =========================================================
# HELPER
# =========================================================

def approval_to_dict(approval: Approval):

    return {
        "id": approval.id,
        "decision_id": approval.decision_id,
        "assigned_to": approval.assigned_to,
        "assigned_by": approval.assigned_by,
        "assigned_role": (
            approval.assigned_role.value
            if approval.assigned_role
            else None
        ),
        "status": (
            approval.status.value
            if approval.status
            else None
        ),
        "comments": approval.comments,
        "assigned_at": approval.assigned_at.isoformat()
        if approval.assigned_at
        else None,
        "reviewed_at": approval.reviewed_at.isoformat()
        if approval.reviewed_at
        else None
    }


# =========================================================
# CREATE / ASSIGN APPROVAL
# =========================================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED
)
def create_approval(
    approval_data: ApprovalCreate,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # AUTHORIZATION
    # -----------------------------------------------------

    if current_user.role not in {
        UserRole.REVIEWER,
        UserRole.MANAGER,
        UserRole.ADMINISTRATOR
    }:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only Reviewer, Manager or "
                "Administrator can assign approvals"
            )
        )

    # -----------------------------------------------------
    # CHECK DECISION
    # -----------------------------------------------------

    decision = db.query(
        Decision
    ).filter(
        Decision.id == approval_data.decision_id
    ).first()

    if not decision:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    # -----------------------------------------------------
    # CHECK ASSIGNED USER
    # -----------------------------------------------------

    assigned_user = db.query(
        User
    ).filter(
        User.id == approval_data.assigned_to
    ).first()

    if not assigned_user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found"
        )

    # -----------------------------------------------------
    # VALIDATE ROLE
    # -----------------------------------------------------

    if assigned_user.role != approval_data.assigned_role:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Assigned role does not match "
                "the assigned user's role"
            )
        )

    # -----------------------------------------------------
    # CREATE APPROVAL
    # -----------------------------------------------------

    approval = Approval(
        decision_id=approval_data.decision_id,
        assigned_to=approval_data.assigned_to,
        assigned_by=current_user.id,
        assigned_role=approval_data.assigned_role,
        status=ApprovalStatus.PENDING,
        assigned_at=datetime.utcnow()
    )

    db.add(approval)

    db.flush()

    # -----------------------------------------------------
    # AUDIT - APPROVAL ASSIGNED
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"User {current_user.id} assigned "
            f"Approval {approval.id} for "
            f"Decision {approval.decision_id} "
            f"to User {approval.assigned_to}"
        ),
        new_value=approval_to_dict(approval),
        request_method="POST",
        endpoint="/approvals"
    )

    db.commit()
    db.refresh(approval)

    return {
        "message": "Approval assigned successfully",
        "approval": approval_to_dict(approval)
    }


# =========================================================
# GET APPROVAL
# =========================================================

@router.get(
    "/{approval_id}"
)
def get_approval(
    approval_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):

    approval = db.query(
        Approval
    ).filter(
        Approval.id == approval_id
    ).first()

    if not approval:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )

    # -----------------------------------------------------
    # AUTHORIZATION
    # -----------------------------------------------------

    allowed = (
        current_user.role == UserRole.ADMINISTRATOR
        or current_user.id == approval.assigned_to
        or current_user.id == approval.assigned_by
    )

    if not allowed:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view this approval"
        )

    # -----------------------------------------------------
    # ACCESS AUDIT
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="ACCESS",
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"User {current_user.id} accessed "
            f"Approval {approval.id}"
        ),
        request_method="GET",
        endpoint=f"/approvals/{approval_id}"
    )

    db.commit()

    return approval_to_dict(approval)


# =========================================================
# LIST APPROVALS FOR DECISION
# =========================================================

@router.get(
    "/decision/{decision_id}"
)
def get_decision_approvals(
    decision_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):

    decision = db.query(
        Decision
    ).filter(
        Decision.id == decision_id
    ).first()

    if not decision:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    approvals = db.query(
        Approval
    ).filter(
        Approval.decision_id == decision_id
    ).all()

    # -----------------------------------------------------
    # ACCESS AUDIT
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="ACCESS",
        entity_type="Decision",
        entity_id=decision_id,
        description=(
            f"User {current_user.id} accessed "
            f"approvals for Decision {decision_id}"
        ),
        request_method="GET",
        endpoint=f"/approvals/decision/{decision_id}"
    )

    db.commit()

    return {
        "decision_id": decision_id,
        "count": len(approvals),
        "approvals": [
            approval_to_dict(approval)
            for approval in approvals
        ]
    }


# =========================================================
# APPROVE
# =========================================================

@router.post(
    "/{approval_id}/approve"
)
def approve(
    approval_id: int,

    review_data: ApprovalReview,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):

    approval = db.query(
        Approval
    ).filter(
        Approval.id == approval_id
    ).first()

    if not approval:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )

    # -----------------------------------------------------
    # AUTHORIZATION
    # -----------------------------------------------------

    if current_user.id != approval.assigned_to:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only the assigned user can "
                "approve this request"
            )
        )

    # -----------------------------------------------------
    # STATUS CHECK
    # -----------------------------------------------------

    if approval.status != ApprovalStatus.PENDING:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "This approval has already been reviewed"
            )
        )

    # -----------------------------------------------------
    # SAVE OLD VALUE
    # -----------------------------------------------------

    old_value = approval_to_dict(approval)

    # -----------------------------------------------------
    # APPROVE
    # -----------------------------------------------------

    approval.status = ApprovalStatus.APPROVED

    approval.comments = review_data.comments

    approval.reviewed_at = datetime.utcnow()

    db.flush()

    new_value = approval_to_dict(approval)

    # -----------------------------------------------------
    # UPDATE DECISION
    # -----------------------------------------------------

    decision = db.query(
        Decision
    ).filter(
        Decision.id == approval.decision_id
    ).first()

    if decision:

        decision.status = DecisionStatus.APPROVED

        db.flush()

    # -----------------------------------------------------
    # AUDIT
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="APPROVE",
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"User {current_user.id} approved "
            f"Approval {approval.id} for "
            f"Decision {approval.decision_id}"
        ),
        old_value=old_value,
        new_value=new_value,
        request_method="POST",
        endpoint=f"/approvals/{approval_id}/approve"
    )

    # Also record decision approval.

    log_audit(
        db=db,
        user_id=current_user.id,
        action="APPROVE",
        entity_type="Decision",
        entity_id=approval.decision_id,
        description=(
            f"User {current_user.id} approved "
            f"Decision {approval.decision_id}"
        ),
        old_value={
            "status": old_value["status"]
        },
        new_value={
            "status": DecisionStatus.APPROVED.value
        },
        request_method="POST",
        endpoint=f"/approvals/{approval_id}/approve"
    )

    db.commit()
    db.refresh(approval)

    return {
        "message": "Approval approved successfully",
        "approval": approval_to_dict(approval)
    }


# =========================================================
# REJECT
# =========================================================

@router.post(
    "/{approval_id}/reject"
)
def reject(
    approval_id: int,

    review_data: ApprovalReview,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):

    approval = db.query(
        Approval
    ).filter(
        Approval.id == approval_id
    ).first()

    if not approval:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )

    # -----------------------------------------------------
    # AUTHORIZATION
    # -----------------------------------------------------

    if current_user.id != approval.assigned_to:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only the assigned user can "
                "reject this request"
            )
        )

    # -----------------------------------------------------
    # STATUS CHECK
    # -----------------------------------------------------

    if approval.status != ApprovalStatus.PENDING:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "This approval has already been reviewed"
            )
        )

    # -----------------------------------------------------
    # OLD VALUE
    # -----------------------------------------------------

    old_value = approval_to_dict(approval)

    # -----------------------------------------------------
    # REJECT
    # -----------------------------------------------------

    approval.status = ApprovalStatus.REJECTED

    approval.comments = review_data.comments

    approval.reviewed_at = datetime.utcnow()

    db.flush()

    new_value = approval_to_dict(approval)

    # -----------------------------------------------------
    # UPDATE DECISION
    # -----------------------------------------------------

    decision = db.query(
        Decision
    ).filter(
        Decision.id == approval.decision_id
    ).first()

    if decision:

        decision.status = DecisionStatus.REJECTED

        db.flush()

    # -----------------------------------------------------
    # AUDIT - APPROVAL
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="REJECT",
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"User {current_user.id} rejected "
            f"Approval {approval.id} for "
            f"Decision {approval.decision_id}"
        ),
        old_value=old_value,
        new_value=new_value,
        request_method="POST",
        endpoint=f"/approvals/{approval_id}/reject"
    )

    # -----------------------------------------------------
    # AUDIT - DECISION
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="REJECT",
        entity_type="Decision",
        entity_id=approval.decision_id,
        description=(
            f"User {current_user.id} rejected "
            f"Decision {approval.decision_id}"
        ),
        old_value={
            "status": old_value["status"]
        },
        new_value={
            "status": DecisionStatus.REJECTED.value
        },
        request_method="POST",
        endpoint=f"/approvals/{approval_id}/reject"
    )

    db.commit()
    db.refresh(approval)

    return {
        "message": "Approval rejected successfully",
        "approval": approval_to_dict(approval)
    }