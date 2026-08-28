from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User
from app.models.activity import Activity
from app.schemas.approval import (
    ApprovalCreate,
    ApprovalAction,
    ApprovalResponse,
)
from app.core.security import get_current_user


router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"]
)


# ============================================================
# CREATE / ASSIGN APPROVAL
# POST /approvals
# ============================================================

@router.post(
    "",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED
)
def create_approval(
    approval_data: ApprovalCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

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
            detail="Decision not found"
        )

    reviewer = (
        db.query(User)
        .filter(
            User.id == approval_data.reviewer_id
        )
        .first()
    )

    if not reviewer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reviewer not found"
        )

    # --------------------------------------------------------
    # CREATE APPROVAL
    # --------------------------------------------------------

    new_approval = Approval(
        decision_id=approval_data.decision_id,
        reviewer_id=approval_data.reviewer_id,
        approval_level=approval_data.approval_level,
        status="Pending"
    )

    db.add(new_approval)
    db.commit()
    db.refresh(new_approval)

    # --------------------------------------------------------
    # ACTIVITY LOG
    # --------------------------------------------------------

    activity = Activity(
        user_id=current_user.id,
        action="Approval Assigned",
        entity_type="Approval",
        entity_id=new_approval.id,
        description=(
            f"User {current_user.id} assigned "
            f"Approval {new_approval.id} for "
            f"Decision {approval_data.decision_id}"
        )
    )

    db.add(activity)
    db.commit()

    return new_approval


# ============================================================
# GET ALL APPROVALS
# GET /approvals
# ============================================================

@router.get(
    "",
    response_model=List[ApprovalResponse]
)
def get_approvals(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Approval).all()


# ============================================================
# GET MY PENDING APPROVALS
# GET /approvals/pending
# ============================================================

@router.get(
    "/pending",
    response_model=List[ApprovalResponse]
)
def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return (
        db.query(Approval)
        .filter(
            Approval.reviewer_id == current_user.id,
            Approval.status == "Pending"
        )
        .all()
    )


# ============================================================
# GET APPROVAL BY ID
# GET /approvals/{approval_id}
# ============================================================

@router.get(
    "/{approval_id}",
    response_model=ApprovalResponse
)
def get_approval(
    approval_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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
            detail="Approval not found"
        )

    return approval


# ============================================================
# APPROVE / REJECT
# PATCH /approvals/{approval_id}
# ============================================================

@router.patch(
    "/{approval_id}",
    response_model=ApprovalResponse
)
def update_approval(
    approval_id: int,
    action: ApprovalAction,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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
            detail="Approval not found"
        )

    # --------------------------------------------------------
    # ONLY ASSIGNED REVIEWER CAN ACT
    # --------------------------------------------------------

    if approval.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to act on this approval"
        )

    # --------------------------------------------------------
    # PREVENT DUPLICATE ACTION
    # --------------------------------------------------------

    if approval.status != "Pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval has already been completed"
        )

    # --------------------------------------------------------
    # VALIDATE ACTION
    # --------------------------------------------------------

    if action.status not in [
        "Approved",
        "Rejected"
    ]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Status must be Approved or Rejected"
        )

    # --------------------------------------------------------
    # UPDATE APPROVAL
    # --------------------------------------------------------

    approval.status = action.status
    approval.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(approval)

    # --------------------------------------------------------
    # ACTIVITY LOG
    # --------------------------------------------------------

    activity = Activity(
        user_id=current_user.id,
        action=action.status,
        entity_type="Approval",
        entity_id=approval.id,
        description=(
            f"User {current_user.id} "
            f"{action.status.lower()} "
            f"Approval {approval.id} for "
            f"Decision {approval.decision_id}"
        )
    )

    db.add(activity)
    db.commit()

    return approval