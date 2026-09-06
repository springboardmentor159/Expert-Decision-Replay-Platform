from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.approval import Approval
from app.models.user import User
from app.schemas.approval import (
    ApprovalCreate,
    ApprovalUpdate,
    ApprovalResponse,
)
from app.routers.auth import get_current_user


router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"]
)


# ============================================================
# 1. CREATE APPROVAL
# ============================================================

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
    # Only Reviewer, Manager and Administrator can create approvals
    allowed_roles = ["Reviewer", "Manager", "Administrator"]

    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to create approvals"
        )

    new_approval = Approval(
        decision_id=approval.decision_id,
        reviewer_id=approval.reviewer_id,
        approval_level=approval.approval_level,
        status="Pending"
    )

    db.add(new_approval)
    db.commit()
    db.refresh(new_approval)

    return new_approval


# ============================================================
# 2. GET ALL APPROVALS
# ============================================================

@router.get(
    "/",
    response_model=list[ApprovalResponse]
)
def get_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Approval).all()


# ============================================================
# 3. GET APPROVAL BY ID
# ============================================================

@router.get(
    "/{approval_id}",
    response_model=ApprovalResponse
)
def get_approval(
    approval_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    approval = db.query(Approval).filter(
        Approval.id == approval_id
    ).first()

    if not approval:
        raise HTTPException(
            status_code=404,
            detail="Approval not found"
        )

    return approval


# ============================================================
# 4. UPDATE APPROVAL
# ============================================================

@router.put(
    "/{approval_id}",
    response_model=ApprovalResponse
)
def update_approval(
    approval_id: int,
    approval_data: ApprovalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    approval = db.query(Approval).filter(
        Approval.id == approval_id
    ).first()

    if not approval:
        raise HTTPException(
            status_code=404,
            detail="Approval not found"
        )

    # Only Reviewer, Manager and Administrator can approve/reject
    allowed_roles = ["Reviewer", "Manager", "Administrator"]

    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to approve or reject decisions"
        )

    allowed_statuses = ["Pending", "Approved", "Rejected"]

    if approval_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=422,
            detail="Invalid approval status"
        )

    approval.status = approval_data.status

    if approval_data.status in ["Approved", "Rejected"]:
        approval.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(approval)

    return approval