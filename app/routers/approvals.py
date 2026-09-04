from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status as http_status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User
from app.schemas.approval import ApprovalAction, ApprovalCreate, ApprovalResponse, ApprovalStatus
from app.services.audit_service import create_decision_version, get_client_ip, log_audit

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
    request: Request,
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
        create_decision_version(
            db=db,
            decision=decision,
            created_by=current_user.id
        )

    db.commit()
    db.refresh(new_approval)

    client_ip = get_client_ip(request)
    log_audit(
        db=db,
        user_id=current_user.id,
        action="SUBMIT",
        entity_type="Approval",
        entity_id=new_approval.id,
        description=f"User {current_user.full_name} assigned approval for Decision #{decision.id} ({decision.title}) to {reviewer.full_name}",
        new_value={"decision_id": decision.id, "reviewer_id": reviewer.id, "status": "Pending"},
        ip_address=client_ip,
        request_method=request.method,
        endpoint=str(request.url.path)
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
    request: Request,
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

    # Enforce authorization: Only assigned reviewer, Manager, or Administrator can approve
    if current_user.id != approval.reviewer_id and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to approve this decision"
        )

    if approval.status != "Pending":
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Approval has already been processed with status '{approval.status}'"
        )

    old_status = approval.status
    approval.status = "Approved"
    approval.completed_at = datetime.utcnow()
    if action and action.comments:
        approval.comments = action.comments

    decision = db.query(Decision).filter(Decision.id == approval.decision_id).first()
    if decision:
        # Check if other approvals for this decision are still pending (Multi-level approvals)
        other_pending = (
            db.query(Approval)
            .filter(
                Approval.decision_id == decision.id,
                Approval.id != approval.id,
                Approval.status == "Pending"
            )
            .count()
        )
        if other_pending == 0:
            decision.status = "Approved"
            create_decision_version(
                db=db,
                decision=decision,
                created_by=current_user.id
            )
        else:
            decision.status = "Under Review"

    db.commit()
    db.refresh(approval)

    client_ip = get_client_ip(request)
    log_audit(
        db=db,
        user_id=current_user.id,
        action="APPROVE",
        entity_type="Approval",
        entity_id=approval.id,
        description=f"User {current_user.full_name} approved Decision #{approval.decision_id}",
        old_value={"status": old_status},
        new_value={"status": "Approved", "comments": approval.comments},
        ip_address=client_ip,
        request_method=request.method,
        endpoint=str(request.url.path)
    )

    return approval


@router.post(
    "/{approval_id}/reject",
    response_model=ApprovalResponse,
    summary="Reject a decision"
)
def reject_decision(
    approval_id: int,
    request: Request,
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

    # Enforce authorization: Only assigned reviewer, Manager, or Administrator can reject
    if current_user.id != approval.reviewer_id and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to reject this decision"
        )

    old_status = approval.status
    approval.status = "Rejected"
    approval.completed_at = datetime.utcnow()
    if action and action.comments:
        approval.comments = action.comments

    decision = db.query(Decision).filter(Decision.id == approval.decision_id).first()
    if decision:
        decision.status = "Rejected"
        create_decision_version(
            db=db,
            decision=decision,
            created_by=current_user.id
        )

    db.commit()
    db.refresh(approval)

    client_ip = get_client_ip(request)
    log_audit(
        db=db,
        user_id=current_user.id,
        action="REJECT",
        entity_type="Approval",
        entity_id=approval.id,
        description=f"User {current_user.full_name} rejected Decision #{approval.decision_id}",
        old_value={"status": old_status},
        new_value={"status": "Rejected", "comments": approval.comments},
        ip_address=client_ip,
        request_method=request.method,
        endpoint=str(request.url.path)
    )

    return approval

