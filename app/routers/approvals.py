from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User
from app.schemas.approval import ApprovalAction, ApprovalCreate, ApprovalResponse, ApprovalStatus
from app.services.activity_logger import log_activity

router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"]
)


@router.post(
    "",
    response_model=ApprovalResponse,
    status_code=http_status.HTTP_201_CREATED,
    summary="Submit decision for approval or create an approval task"
)
def create_approval(
    approval_data: ApprovalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == approval_data.decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    if decision.status == "Archived":
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Cannot submit an archived decision for approval"
        )

    reviewer = db.query(User).filter(User.id == approval_data.reviewer_id).first()
    if not reviewer:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Reviewer not found"
        )

    new_approval = Approval(
        decision_id=decision.id,
        reviewer_id=reviewer.id,
        approval_level=approval_data.approval_level or 1,
        comments=approval_data.comments,
        status="Pending",
        created_at=datetime.utcnow()
    )
    db.add(new_approval)

    if decision.status == "Draft":
        decision.status = "Under Review"

    db.commit()
    db.refresh(new_approval)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="approval_assigned",
        entity_type="Approval",
        entity_id=new_approval.id,
        description=f"User {current_user.full_name} assigned approval for Decision #{decision.id} ({decision.title}) to {reviewer.full_name}"
    )

    return new_approval


@router.get(
    "",
    response_model=List[ApprovalResponse],
    summary="List all approvals with optional filters"
)
def get_approvals(
    decision_id: Optional[int] = Query(None),
    reviewer_id: Optional[int] = Query(None),
    status: Optional[ApprovalStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Approval)
    if decision_id is not None:
        query = query.filter(Approval.decision_id == decision_id)
    if reviewer_id is not None:
        query = query.filter(Approval.reviewer_id == reviewer_id)
    if status is not None:
        query = query.filter(Approval.status == status.value)

    return query.order_by(Approval.created_at.desc()).all()


@router.get(
    "/{approval_id}",
    response_model=ApprovalResponse,
    summary="Get approval details by ID"
)
def get_approval(
    approval_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    approval = db.query(Approval).filter(Approval.id == approval_id).first()
    if not approval:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )
    return approval


@router.post(
    "/{approval_id}/approve",
    response_model=ApprovalResponse,
    summary="Approve a decision"
)
def approve_decision(
    approval_id: int,
    action: Optional[ApprovalAction] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    approval = db.query(Approval).filter(Approval.id == approval_id).first()
    if not approval:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )

    if approval.status != "Pending":
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Approval has already been processed with status '{approval.status}'"
        )

    approval.status = "Approved"
    approval.completed_at = datetime.utcnow()
    if action and action.comments:
        approval.comments = action.comments

    decision = db.query(Decision).filter(Decision.id == approval.decision_id).first()
    if decision:
        decision.status = "Approved"

    db.commit()
    db.refresh(approval)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="approve",
        entity_type="Approval",
        entity_id=approval.id,
        description=f"User {current_user.full_name} approved Decision #{approval.decision_id}"
    )

    return approval


@router.post(
    "/{approval_id}/reject",
    response_model=ApprovalResponse,
    summary="Reject a decision"
)
def reject_decision(
    approval_id: int,
    action: Optional[ApprovalAction] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    approval = db.query(Approval).filter(Approval.id == approval_id).first()
    if not approval:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )

    if approval.status != "Pending":
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Approval has already been processed with status '{approval.status}'"
        )

    approval.status = "Rejected"
    approval.completed_at = datetime.utcnow()
    if action and action.comments:
        approval.comments = action.comments

    decision = db.query(Decision).filter(Decision.id == approval.decision_id).first()
    if decision:
        decision.status = "Rejected"

    db.commit()
    db.refresh(approval)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="reject",
        entity_type="Approval",
        entity_id=approval.id,
        description=f"User {current_user.full_name} rejected Decision #{approval.decision_id}"
    )

    return approval
