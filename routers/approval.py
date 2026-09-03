from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.activity import ActivityLog
from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User
from app.schemas.approval import ApprovalAction, ApprovalCreate, ApprovalResponse
from app.services.activity import record_activity

router = APIRouter(tags=["Approvals"])


def _role(user: User) -> str:
    return str(user.role).lower()


def _require_manager(user: User) -> None:
    if _role(user) not in {"manager", "admin", "administrator"}:
        raise HTTPException(status_code=403, detail="Insufficient permission")


@router.post("/decisions/{decision_id}/approvals", response_model=ApprovalResponse, status_code=status.HTTP_201_CREATED)
def assign_approval(decision_id: int, payload: ApprovalCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_manager(current_user)
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    reviewer = db.query(User).filter(User.id == payload.reviewer_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    if not reviewer:
        raise HTTPException(status_code=404, detail="Reviewer not found")
    approval = Approval(decision_id=decision_id, reviewer_id=reviewer.id)
    db.add(approval)
    db.flush()
    record_activity(db, current_user.id, "approval_assigned", "Approval", "Approval assigned", approval.id)
    db.commit()
    db.refresh(approval)
    return approval


@router.get("/approvals", response_model=list[ApprovalResponse])
def list_approvals(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Approval)
    if _role(current_user) not in {"manager", "admin", "administrator"}:
        query = query.filter(Approval.reviewer_id == current_user.id)
    return query.order_by(Approval.created_at.desc()).all()


@router.get("/approvals/pending", response_model=list[ApprovalResponse])
def pending_approvals(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Approval).filter(Approval.status == "Pending")
    if _role(current_user) not in {"manager", "admin", "administrator"}:
        query = query.filter(Approval.reviewer_id == current_user.id)
    return query.order_by(Approval.created_at.asc()).all()


@router.patch("/approvals/{approval_id}", response_model=ApprovalResponse)
def act_on_approval(approval_id: int, payload: ApprovalAction, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    approval = db.query(Approval).filter(Approval.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    if approval.reviewer_id != current_user.id and _role(current_user) not in {"manager", "admin", "administrator"}:
        raise HTTPException(status_code=403, detail="Insufficient permission")
    if approval.status != "Pending":
        raise HTTPException(status_code=409, detail="Approval has already been completed")
    approval.status = payload.status.value
    approval.comments = payload.comments
    approval.completed_at = datetime.now(timezone.utc)
    approval.decision.status = payload.status.value
    record_activity(db, current_user.id, "approval_completed", "Approval", f"Approval {payload.status.value.lower()}", approval.id)
    db.commit()
    db.refresh(approval)
    return approval
