from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User
from app.schemas.approval import ApprovalCreate, ApprovalActionRequest, ApprovalResponse
from app.schemas.decision import DecisionStatus
from app.utils.security import get_current_user, require_role
from app.utils.activity_logger import log_activity


router = APIRouter(tags=["Approvals"])


def get_decision_or_404(decision_id: int, db: Session) -> Decision:
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )
    return decision


def get_approval_or_404(approval_id: int, db: Session) -> Approval:
    approval = db.query(Approval).filter(Approval.id == approval_id).first()
    if approval is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )
    return approval


# ASSIGN A DECISION TO A REVIEWER (Manager / Administrator only)
@router.post(
    "/decisions/{decision_id}/approvals",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED
)
def assign_approval(
    decision_id: int,
    payload: ApprovalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Manager", "Administrator"))
):
    decision = get_decision_or_404(decision_id, db)

    reviewer = db.query(User).filter(User.id == payload.reviewer_id).first()
    if reviewer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reviewer not found"
        )

    new_approval = Approval(
        decision_id=decision_id,
        level=payload.level,
        reviewer_id=payload.reviewer_id,
        status="Pending",
    )
    db.add(new_approval)

    decision.status = DecisionStatus.UNDER_REVIEW.value
    decision.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(new_approval)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="approval_assigned",
        entity_type="Approval",
        entity_id=new_approval.id,
        description=(
            f"Decision '{decision.title}' assigned to reviewer "
            f"{reviewer.full_name} for approval"
        ),
    )

    return new_approval


# APPROVE OR REJECT (only the assigned reviewer, or an Administrator)
@router.patch(
    "/approvals/{approval_id}",
    response_model=ApprovalResponse
)
def act_on_approval(
    approval_id: int,
    payload: ApprovalActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    approval = get_approval_or_404(approval_id, db)

    if (
        approval.reviewer_id != current_user.id
        and current_user.role != "Administrator"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the assigned reviewer for this approval"
        )

    if approval.status != "Pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This approval has already been completed"
        )

    if payload.decision.value not in ("Approved", "Rejected"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="decision must be 'Approved' or 'Rejected'"
        )

    approval.status = payload.decision.value
    approval.comments = payload.comments
    approval.completed_at = datetime.utcnow()

    decision = get_decision_or_404(approval.decision_id, db)
    decision.status = payload.decision.value
    decision.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(approval)

    log_activity(
        db=db,
        user_id=current_user.id,
        action=(
            "approval_completed" if payload.decision.value == "Approved"
            else "approval_rejected"
        ),
        entity_type="Approval",
        entity_id=approval.id,
        description=f"Decision '{decision.title}' was {payload.decision.value.lower()}",
    )

    return approval


# LIST APPROVALS ASSIGNED TO THE CURRENT USER
@router.get(
    "/approvals/pending",
    response_model=list[ApprovalResponse]
)
def get_my_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Approval)
        .filter(
            Approval.reviewer_id == current_user.id,
            Approval.status == "Pending",
        )
        .order_by(Approval.created_at.asc())
        .all()
    )
