from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db

from app.models.decision import Decision
from app.models.decision_status import DecisionStatus
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.models.approval import Approval
from app.models.approval_status import ApprovalStatus


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# ==========================================
# EMPLOYEE DASHBOARD
# ==========================================
@router.get("/employee")
def employee_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_decisions = (
        db.query(Decision)
        .filter(Decision.created_by == current_user.id)
        .count()
    )

    draft_decisions = (
        db.query(Decision)
        .filter(
            Decision.created_by == current_user.id,
            Decision.status == DecisionStatus.DRAFT
        )
        .count()
    )

    under_review = (
        db.query(Decision)
        .filter(
            Decision.created_by == current_user.id,
            Decision.status == DecisionStatus.UNDER_REVIEW
        )
        .count()
    )

    approved_decisions = (
        db.query(Decision)
        .filter(
            Decision.created_by == current_user.id,
            Decision.status == DecisionStatus.APPROVED
        )
        .count()
    )

    rejected_decisions = (
        db.query(Decision)
        .filter(
            Decision.created_by == current_user.id,
            Decision.status == DecisionStatus.REJECTED
        )
        .count()
    )

    # Pending reviews assigned to current user
    pending_reviews = (
        db.query(Approval)
        .filter(
            Approval.reviewer_id == current_user.id,
            Approval.status == ApprovalStatus.PENDING
        )
        .count()
    )

    recent_activities = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == current_user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "total_decisions": total_decisions,
        "draft_decisions": draft_decisions,
        "under_review": under_review,
        "approved_decisions": approved_decisions,
        "rejected_decisions": rejected_decisions,
        "pending_reviews": pending_reviews,
        "recent_activities": [
            {
                "id": activity.id,
                "user_id": activity.user_id,
                "action": activity.action,
                "entity_type": activity.entity_type,
                "entity_id": activity.entity_id,
                "description": activity.description,
                "created_at": activity.created_at
            }
            for activity in recent_activities
        ]
    }


# ==========================================
# EMPLOYEE - MY DECISIONS
# ==========================================
@router.get("/employee/decisions")
def employee_my_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decisions = (
        db.query(Decision)
        .filter(Decision.created_by == current_user.id)
        .order_by(Decision.created_at.desc())
        .all()
    )

    return [
        {
            "id": decision.id,
            "title": decision.title,
            "category": decision.category,
            "status": decision.status.value,
            "created_at": decision.created_at,
            "updated_at": decision.updated_at
        }
        for decision in decisions
    ]


# ==========================================
# EMPLOYEE - PENDING REVIEWS
# ==========================================
@router.get("/employee/pending-reviews")
def employee_pending_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    approvals = (
        db.query(Approval)
        .filter(
            Approval.reviewer_id == current_user.id,
            Approval.status == ApprovalStatus.PENDING
        )
        .order_by(Approval.created_at.desc())
        .all()
    )

    return [
        {
            "approval_id": approval.id,
            "decision_id": approval.decision_id,
            "status": approval.status.value,
            "created_at": approval.created_at
        }
        for approval in approvals
    ]


# ==========================================
# EMPLOYEE - RECENT ACTIVITIES
# ==========================================
@router.get("/employee/recent-activities")
def employee_recent_activities(
    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    activities = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == current_user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": activity.id,
            "user_id": activity.user_id,
            "action": activity.action,
            "entity_type": activity.entity_type,
            "entity_id": activity.entity_id,
            "description": activity.description,
            "created_at": activity.created_at
        }
        for activity in activities
    ]