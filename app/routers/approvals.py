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


router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"]
)


@router.post(
    "",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED
)
def create_approval(
    approval_data: ApprovalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Manager", "Administrator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or Administrator access required"
        )

    decision = (
        db.query(Decision)
        .filter(Decision.id == approval_data.decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    reviewer = (
        db.query(User)
        .filter(User.id == approval_data.reviewer_id)
        .first()
    )

    if not reviewer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reviewer not found"
        )

    if reviewer.role not in ["Reviewer", "Manager", "Administrator"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected user cannot be an approval reviewer"
        )

    approval = Approval(
        decision_id=approval_data.decision_id,
        reviewer_id=approval_data.reviewer_id,
        approval_level=approval_data.approval_level,
        status=approval_data.status,
        assigned_at=datetime.now(timezone.utc)
    )

    db.add(approval)
    db.commit()
    db.refresh(approval)

    return approval


@router.get(
    "",
    response_model=list[ApprovalResponse]
)
def get_approvals(
    decision_id: int | None = None,
    reviewer_id: int | None = None,
    approval_status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Approval)

    if current_user.role == "Employee":
        query = (
            query
            .join(Decision, Approval.decision_id == Decision.id)
            .filter(Decision.created_by == current_user.id)
        )

    elif current_user.role == "Reviewer":
        query = query.filter(
            Approval.reviewer_id == current_user.id
        )

    elif current_user.role not in ["Manager", "Administrator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    if decision_id is not None:
        query = query.filter(
            Approval.decision_id == decision_id
        )

    if reviewer_id is not None:
        query = query.filter(
            Approval.reviewer_id == reviewer_id
        )

    if approval_status:
        query = query.filter(
            Approval.status == approval_status
        )

    return (
        query
        .order_by(Approval.assigned_at.desc())
        .all()
    )


@router.get(
    "/{approval_id}",
    response_model=ApprovalResponse
)
def get_approval(
    approval_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    approval = (
        db.query(Approval)
        .filter(Approval.id == approval_id)
        .first()
    )

    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )

    if current_user.role == "Reviewer":
        if approval.reviewer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    elif current_user.role == "Employee":
        decision = (
            db.query(Decision)
            .filter(Decision.id == approval.decision_id)
            .first()
        )

        if not decision or decision.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    elif current_user.role not in [
        "Manager",
        "Administrator"
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    return approval


@router.patch(
    "/{approval_id}",
    response_model=ApprovalResponse
)
def update_approval(
    approval_id: int,
    approval_data: ApprovalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    approval = (
        db.query(Approval)
        .filter(Approval.id == approval_id)
        .first()
    )

    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )

    if current_user.role == "Reviewer":
        if approval.reviewer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the assigned reviewer can update this approval"
            )

    elif current_user.role not in [
        "Manager",
        "Administrator"
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager, Reviewer or Administrator access required"
        )

    if approval_data.status is not None:
        approval.status = approval_data.status

        if approval_data.status in ["Approved", "Rejected"]:
            approval.completed_at = (
                approval_data.completed_at
                or datetime.now(timezone.utc)
            )
        elif approval_data.completed_at is not None:
            approval.completed_at = approval_data.completed_at

    elif approval_data.completed_at is not None:
        approval.completed_at = approval_data.completed_at

    db.commit()
    db.refresh(approval)

    return approval