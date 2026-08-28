from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User
from app.schemas.approval import ApprovalAction, ApprovalCreate, ApprovalResponse, ApprovalStatus
from app.services.activity_logger import log_activity

router = APIRouter(
    tags=["Approvals"]
)


def _to_response(approval: Approval) -> ApprovalResponse:
    return ApprovalResponse(
        id=approval.id,
        decision_id=approval.decision_id,
        reviewer_id=approval.reviewer_id,
        approval_level=approval.approval_level,
        status=approval.status,
        comments=approval.comments,
        created_at=approval.created_at,
        completed_at=approval.completed_at,
        decision_title=approval.decision.title if approval.decision else None,
        reviewer_name=approval.reviewer.full_name if approval.reviewer else None
    )


@router.post(
    "/decisions/{decision_id}/submit",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a decision for approval / review"
)
def submit_decision_for_approval(
    decision_id: int,
    approval_in: ApprovalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    reviewer = db.query(User).filter(User.id == approval_in.reviewer_id).first()
    if not reviewer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reviewer not found"
        )

    decision.status = "Under Review"

    approval = Approval(
        decision_id=decision_id,
        reviewer_id=approval_in.reviewer_id,
        approval_level=approval_in.approval_level or 1,
        status="Pending",
        comments=approval_in.comments,
        created_at=datetime.utcnow()
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)
    db.refresh(decision)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="submit_for_approval",
        entity_type="approval",
        entity_id=approval.id,
        description=f"User {current_user.full_name} submitted decision '{decision.title}' for review to {reviewer.full_name}"
    )

    return _to_response(approval)


@router.post(
    "/approvals",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an approval request directly"
)
def create_approval(
    approval_in: ApprovalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return submit_decision_for_approval(
        decision_id=approval_in.decision_id,
        approval_in=approval_in,
        db=db,
        current_user=current_user
    )


@router.post(
    "/approvals/{approval_id}/action",
    response_model=ApprovalResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve or Reject an approval request"
)
def process_approval_action(
    approval_id: int,
    action_in: ApprovalAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    approval = db.query(Approval).filter(Approval.id == approval_id).first()
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )

    # Permission check: assigned reviewer, Administrator, or Manager
    if approval.reviewer_id != current_user.id and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to act on this approval"
        )

    new_status = action_in.status.value if hasattr(action_in.status, "value") else str(action_in.status)
    approval.status = new_status
    approval.comments = action_in.comments
    approval.completed_at = datetime.utcnow()

    # Update decision status accordingly
    decision = approval.decision
    if decision:
        decision.status = new_status

    db.commit()
    db.refresh(approval)
    if decision:
        db.refresh(decision)

    action_name = "approve_decision" if new_status == "Approved" else "reject_decision"
    log_activity(
        db=db,
        user_id=current_user.id,
        action=action_name,
        entity_type="approval",
        entity_id=approval.id,
        description=f"User {current_user.full_name} marked approval as '{new_status}' for decision '{decision.title if decision else 'N/A'}'"
    )

    return _to_response(approval)


@router.get(
    "/approvals",
    response_model=List[ApprovalResponse],
    status_code=status.HTTP_200_OK,
    summary="List all approvals"
)
def list_approvals(
    decision_id: Optional[int] = Query(None),
    reviewer_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Approval)
    if decision_id:
        query = query.filter(Approval.decision_id == decision_id)
    if reviewer_id:
        query = query.filter(Approval.reviewer_id == reviewer_id)
    if status_filter:
        query = query.filter(Approval.status == status_filter)

    approvals = query.order_by(Approval.created_at.desc()).all()
    return [_to_response(a) for a in approvals]


@router.get(
    "/decisions/{decision_id}/approvals",
    response_model=List[ApprovalResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all approvals for a decision"
)
def get_decision_approvals(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    approvals = db.query(Approval).filter(Approval.decision_id == decision_id).order_by(Approval.created_at.desc()).all()
    return [_to_response(a) for a in approvals]
