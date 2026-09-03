from datetime import datetime
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.activity import Activity
from app.models.decision import Decision
from app.models.user import User


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# EMPLOYEE DASHBOARD
@router.get("/employee")
def employee_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
        db.query(Activity)
        .filter(Activity.user_id == current_user.id)
        .order_by(Activity.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "total_decisions": total_decisions,
        "draft_decisions": draft_decisions,
        "under_review": under_review,
        "approved_decisions": approved_decisions,
        "rejected_decisions": rejected_decisions,
        "pending_reviews": under_review,
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


# MANAGER DASHBOARD
@router.get("/manager")
def manager_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )

    team_decisions = (
        db.query(Decision)
        .join(User, Decision.created_by == User.id)
        .filter(User.department == current_user.department)
    )

    total_decisions = team_decisions.count()

    draft_decisions = team_decisions.filter(
        Decision.status == "Draft"
    ).count()

    under_review = team_decisions.filter(
        Decision.status == "Under Review"
    ).count()

    approved_decisions = team_decisions.filter(
        Decision.status == "Approved"
    ).count()

    rejected_decisions = team_decisions.filter(
        Decision.status == "Rejected"
    ).count()

    recent_activities = (
        db.query(Activity)
        .join(User, Activity.user_id == User.id)
        .filter(User.department == current_user.department)
        .order_by(Activity.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "department": current_user.department,
        "total_decisions": total_decisions,
        "draft_decisions": draft_decisions,
        "under_review": under_review,
        "approved_decisions": approved_decisions,
        "rejected_decisions": rejected_decisions,
        "pending_approvals": under_review,
        "recent_team_activities": [
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


# ADMIN DASHBOARD
@router.get("/admin")
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required"
        )

    total_users = db.query(User).count()
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

    recent_activities = (
        db.query(Activity)
        .order_by(Activity.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "total_users": total_users,
        "total_decisions": total_decisions,
        "draft_decisions": draft_decisions,
        "under_review": under_review,
        "approved_decisions": approved_decisions,
        "rejected_decisions": rejected_decisions,
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


# DECISION STATISTICS
@router.get("/decision-statistics")
def decision_statistics(
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Manager", "Administrator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or Administrator access required"
        )

    query = db.query(Decision)

    if current_user.role == "Manager":
        query = (
            query
            .join(User, Decision.created_by == User.id)
            .filter(User.department == current_user.department)
        )

    if start_date:
        query = query.filter(
            Decision.created_at >= start_date
        )

    if end_date:
        query = query.filter(
            Decision.created_at <= end_date
        )

    return {
        "total_decisions": query.count(),
        "draft": query.filter(
            Decision.status == "Draft"
        ).count(),
        "under_review": query.filter(
            Decision.status == "Under Review"
        ).count(),
        "approved": query.filter(
            Decision.status == "Approved"
        ).count(),
        "rejected": query.filter(
            Decision.status == "Rejected"
        ).count(),
        "archived": query.filter(
            Decision.status == "Archived"
        ).count()
    }


# ACTIVITY STATISTICS
@router.get("/activity-statistics")
def activity_statistics(
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Manager", "Administrator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or Administrator access required"
        )

    query = db.query(Activity)

    if current_user.role == "Manager":
        query = (
            query
            .join(User, Activity.user_id == User.id)
            .filter(User.department == current_user.department)
        )

    if start_date:
        query = query.filter(
            Activity.created_at >= start_date
        )

    if end_date:
        query = query.filter(
            Activity.created_at <= end_date
        )

    total_activities = query.count()

    active_users = query.with_entities(
        Activity.user_id
    ).distinct().count()

    return {
        "total_activities": total_activities,
        "active_users": active_users
    }


# DECISION ACTIVITY
@router.get("/decision-activity")
def decision_activity(
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Manager", "Administrator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or Administrator access required"
        )

    query = db.query(Decision)

    if current_user.role == "Manager":
        query = (
            query
            .join(User, Decision.created_by == User.id)
            .filter(User.department == current_user.department)
        )

    if start_date:
        query = query.filter(
            Decision.created_at >= start_date
        )

    if end_date:
        query = query.filter(
            Decision.created_at <= end_date
        )

    decisions = (
        query
        .order_by(Decision.created_at.asc())
        .all()
    )

    activity = {}

    for decision in decisions:
        date_key = decision.created_at.date().isoformat()

        if date_key not in activity:
            activity[date_key] = 0

        activity[date_key] += 1

    return [
        {
            "date": date_key,
            "decision_count": count
        }
        for date_key, count in activity.items()
    ]