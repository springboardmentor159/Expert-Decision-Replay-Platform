from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.decision import Decision
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.routers.auth import get_current_user


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# ============================================================
# EMPLOYEE DASHBOARD
# ============================================================

@router.get("/employee")
def employee_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Employee dashboard for the currently logged-in user.
    """

    base_query = db.query(Decision).filter(
        Decision.created_by == current_user.id
    )

    total_decisions = base_query.count()

    draft_decisions = base_query.filter(
        Decision.status == "Draft"
    ).count()

    under_review = base_query.filter(
        Decision.status == "Under Review"
    ).count()

    approved_decisions = base_query.filter(
        Decision.status == "Approved"
    ).count()

    rejected_decisions = base_query.filter(
        Decision.status == "Rejected"
    ).count()

    recent_activities = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == current_user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "user_id": current_user.id,
        "user_name": current_user.full_name,
        "role": current_user.role,

        "total_decisions": total_decisions,
        "draft_decisions": draft_decisions,
        "under_review": under_review,
        "approved_decisions": approved_decisions,
        "rejected_decisions": rejected_decisions,

        "pending_reviews": 0,

        "recent_activities": [
            {
                "id": activity.id,
                "action": activity.action,
                "entity_type": activity.entity_type,
                "entity_id": activity.entity_id,
                "description": activity.description,
                "created_at": activity.created_at
            }
            for activity in recent_activities
        ]
    }


# ============================================================
# EMPLOYEE - MY DECISIONS
# ============================================================

@router.get("/employee/decisions")
def employee_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return only decisions created by the logged-in employee.
    """

    decisions = (
        db.query(Decision)
        .filter(
            Decision.created_by == current_user.id
        )
        .order_by(
            Decision.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": decision.id,
            "title": decision.title,
            "category": decision.category,
            "status": decision.status,
            "created_at": decision.created_at,
            "updated_at": decision.updated_at
        }
        for decision in decisions
    ]


# ============================================================
# EMPLOYEE - RECENT ACTIVITIES
# ============================================================

@router.get("/employee/recent-activities")
def employee_recent_activities(
    limit: int = Query(
        10,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return recent activities performed by the logged-in user.
    """

    activities = (
        db.query(ActivityLog)
        .filter(
            ActivityLog.user_id == current_user.id
        )
        .order_by(
            ActivityLog.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "id": activity.id,
            "action": activity.action,
            "entity_type": activity.entity_type,
            "entity_id": activity.entity_id,
            "description": activity.description,
            "created_at": activity.created_at
        }
        for activity in activities
    ]


# ============================================================
# EMPLOYEE - PENDING REVIEWS
# ============================================================

@router.get("/employee/pending-reviews")
def employee_pending_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Pending reviews will be connected to the existing
    approval workflow when the approval model is available.
    """

    return {
        "pending_reviews": [],
        "count": 0,
        "message": "No approval workflow is currently available."
    }