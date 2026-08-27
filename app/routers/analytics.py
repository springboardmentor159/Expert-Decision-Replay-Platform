from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.decision import Decision
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.routers.auth import get_current_user


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


# ============================================================
# 1. OVERALL DECISION STATISTICS
# ============================================================

@router.get("/decisions")
def decision_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return overall decision statistics.
    """

    total_decisions = db.query(Decision).count()

    draft_decisions = db.query(Decision).filter(
        Decision.status == "Draft"
    ).count()

    under_review = db.query(Decision).filter(
        Decision.status == "Under Review"
    ).count()

    approved_decisions = db.query(Decision).filter(
        Decision.status == "Approved"
    ).count()

    rejected_decisions = db.query(Decision).filter(
        Decision.status == "Rejected"
    ).count()

    return {
        "total_decisions": total_decisions,
        "draft_decisions": draft_decisions,
        "under_review": under_review,
        "approved_decisions": approved_decisions,
        "rejected_decisions": rejected_decisions
    }


# ============================================================
# 2. CATEGORY-WISE DECISION ANALYSIS
# ============================================================

@router.get("/decisions/categories")
def category_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return the number of decisions in each category.
    """

    results = (
        db.query(
            Decision.category,
            func.count(Decision.id).label("decision_count")
        )
        .group_by(Decision.category)
        .order_by(
            func.count(Decision.id).desc()
        )
        .all()
    )

    return [
        {
            "category": category,
            "decision_count": decision_count
        }
        for category, decision_count in results
    ]


# ============================================================
# 3. USER-WISE DECISION ANALYSIS
# ============================================================

@router.get("/decisions/users")
def user_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return the number of decisions created by each user.
    """

    results = (
        db.query(
            User.id,
            User.full_name,
            User.email,
            func.count(Decision.id).label("decision_count")
        )
        .outerjoin(
            Decision,
            Decision.created_by == User.id
        )
        .group_by(
            User.id,
            User.full_name,
            User.email
        )
        .order_by(
            func.count(Decision.id).desc()
        )
        .all()
    )

    return [
        {
            "user_id": user_id,
            "user_name": full_name,
            "email": email,
            "decision_count": decision_count
        }
        for user_id, full_name, email, decision_count in results
    ]


# ============================================================
# 4. ACTIVITY STATISTICS
# ============================================================

@router.get("/activities")
def activity_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return overall activity-log statistics.
    """

    total_activities = db.query(ActivityLog).count()

    results = (
        db.query(
            ActivityLog.action,
            func.count(ActivityLog.id).label("activity_count")
        )
        .group_by(ActivityLog.action)
        .order_by(
            func.count(ActivityLog.id).desc()
        )
        .all()
    )

    return {
        "total_activities": total_activities,
        "activities_by_action": [
            {
                "action": action,
                "activity_count": activity_count
            }
            for action, activity_count in results
        ]
    }


# ============================================================
# 5. RECENT DECISIONS
# ============================================================

@router.get("/recent-decisions")
def recent_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return the latest 10 decisions.
    """

    decisions = (
        db.query(Decision)
        .order_by(
            Decision.created_at.desc()
        )
        .limit(10)
        .all()
    )

    return [
        {
            "id": decision.id,
            "title": decision.title,
            "category": decision.category,
            "status": decision.status,
            "created_by": decision.created_by,
            "created_at": decision.created_at,
            "updated_at": decision.updated_at
        }
        for decision in decisions
    ]