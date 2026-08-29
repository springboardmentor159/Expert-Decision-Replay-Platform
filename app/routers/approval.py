from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User
from app.schemas.dashboard import ApprovalCreate, ApprovalDecision, ApprovalResponse
from app.routers.dashboard import require_roles
from app.utils.activity_logger import log_activity

router = APIRouter(prefix="/approvals", tags=["Approvals"])

@router.post("", response_model=ApprovalResponse, status_code=status.HTTP_201_CREATED)
def assign_approval(data: ApprovalCreate, db: Session = Depends(get_db), user=Depends(require_roles("Manager", "Administrator"))):
    if not db.query(Decision).filter(Decision.id == data.decision_id).first() or not db.query(User).filter(User.id == data.reviewer_id).first():
        raise HTTPException(status_code=404, detail="Decision or reviewer not found")
    approval = Approval(decision_id=data.decision_id, reviewer_id=data.reviewer_id, approval_level=data.approval_level)
    db.add(approval)
    db.flush()
    log_activity(db, int(user["sub"]), "approval_assigned", "Approval", approval.id, f"Approval assigned for Decision {data.decision_id}")
    db.commit(); db.refresh(approval)
    return approval

@router.patch("/{approval_id}", response_model=ApprovalResponse)
def complete_approval(approval_id: int, data: ApprovalDecision, db: Session = Depends(get_db), user=Depends(require_roles("Reviewer", "Manager", "Administrator"))):
    approval = db.query(Approval).filter(Approval.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    if int(user["sub"]) != approval.reviewer_id and user.get("role") not in ("Manager", "Administrator"):
        raise HTTPException(status_code=403, detail="Approval is assigned to another reviewer")
    if approval.status != "Pending":
        raise HTTPException(status_code=409, detail="Approval is already completed")
    if data.decision not in ("Approved", "Rejected"):
        raise HTTPException(status_code=422, detail="Decision must be Approved or Rejected")
    approval.status = data.decision; approval.completed_at = datetime.now(timezone.utc)
    log_activity(db, int(user["sub"]), data.decision.lower(), "Approval", approval.id, f"Approval {data.decision.lower()}")
    db.commit(); db.refresh(approval)
    return approval