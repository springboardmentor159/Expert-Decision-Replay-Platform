from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.decision import Decision
from app.models.activity_log import ActivityLog


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


# ============================================================
# EMPLOYEE DASHBOARD
# ============================================================

@router.get("/employee")
def employee_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = (
        db.query(func.count(Decision.id))
        .filter(Decision.created_by == current_user.id)
        .scalar()
    )

    draft = (
        db.query(func.count(Decision.id))
        .filter(
            Decision.created_by == current_user.id,
            Decision.status == "Draft",
        )
        .scalar()
    )

    under_review = (
        db.query(func.count(Decision.id))
        .filter(
            Decision.created_by == current_user.id,
            Decision.status == "Under Review",
        )
        .scalar()
    )

    approved = (
        db.query(func.count(Decision.id))
        .filter(
            Decision.created_by == current_user.id,
            Decision.status == "Approved",
        )
        .scalar()
    )

    rejected = (
        db.query(func.count(Decision.id))
        .filter(
            Decision.created_by == current_user.id,
            Decision.status == "Rejected",
        )
        .scalar()
    )

    recent_activities = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == current_user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "total_decisions": total or 0,
        "draft_decisions": draft or 0,
        "under_review": under_review or 0,
        "approved_decisions": approved or 0,
        "rejected_decisions": rejected or 0,
        "pending_reviews": 0,
        "recent_activities": [
            {
                "id": activity.id,
                "action": activity.action,
                "entity_type": activity.entity_type,
                "entity_id": activity.entity_id,
                "description": activity.description,
                "created_at": activity.created_at,
            }
            for activity in recent_activities
        ],
    }


# ============================================================
# EMPLOYEE - MY DECISIONS
# ============================================================

@router.get("/employee/decisions")
def employee_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
            "status": decision.status,
            "created_at": decision.created_at,
            "updated_at": decision.updated_at,
        }
        for decision in decisions
    ]


# ============================================================
# EMPLOYEE - RECENT ACTIVITIES
# ============================================================

@router.get("/employee/recent-activities")
def employee_recent_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    activities = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == current_user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(20)
        .all()
    )

    return activities


# ============================================================
# MANAGER DASHBOARD
# ============================================================

@router.get("/manager")
def manager_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.lower() != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required",
        )

    total = db.query(func.count(Decision.id)).scalar() or 0

    under_review = (
        db.query(func.count(Decision.id))
        .filter(Decision.status == "Under Review")
        .scalar()
        or 0
    )

    approved = (
        db.query(func.count(Decision.id))
        .filter(Decision.status == "Approved")
        .scalar()
        or 0
    )

    rejected = (
        db.query(func.count(Decision.id))
        .filter(Decision.status == "Rejected")
        .scalar()
        or 0
    )

    return {
        "team_decisions": total,
        "pending_approvals": 0,
        "approved_decisions": approved,
        "rejected_decisions": rejected,
        "under_review": under_review,
    }


# ============================================================
# MANAGER - DECISION STATISTICS
# ============================================================

@router.get("/manager/statistics")
def manager_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.lower() != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required",
        )

    result = {}

    for decision_status in [
        "Draft",
        "Under Review",
        "Approved",
        "Rejected",
        "Archived",
    ]:
        result[decision_status.lower().replace(" ", "_")] = (
            db.query(func.count(Decision.id))
            .filter(Decision.status == decision_status)
            .scalar()
            or 0
        )

    result["total_decisions"] = (
        db.query(func.count(Decision.id)).scalar() or 0
    )

    return result


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@router.get("/admin")
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.lower() not in ["admin", "administrator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )

    total_users = db.query(func.count(User.id)).scalar() or 0
    total_decisions = db.query(func.count(Decision.id)).scalar() or 0
    total_activities = db.query(func.count(ActivityLog.id)).scalar() or 0

    approved = (
        db.query(func.count(Decision.id))
        .filter(Decision.status == "Approved")
        .scalar()
        or 0
    )

    rejected = (
        db.query(func.count(Decision.id))
        .filter(Decision.status == "Rejected")
        .scalar()
        or 0
    )

    under_review = (
        db.query(func.count(Decision.id))
        .filter(Decision.status == "Under Review")
        .scalar()
        or 0
    )

    archived = (
        db.query(func.count(Decision.id))
        .filter(Decision.status == "Archived")
        .scalar()
        or 0
    )

    return {
        "total_users": total_users,
        "total_decisions": total_decisions,
        "approved_decisions": approved,
        "rejected_decisions": rejected,
        "under_review": under_review,
        "archived_decisions": archived,
        "total_activities": total_activities,
    }


# ============================================================
# ADMIN ANALYTICS
# ============================================================

@router.get("/admin/analytics")
def admin_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.lower() not in ["admin", "administrator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )

    query = db.query(Decision)

    if start_date:
        query = query.filter(Decision.created_at >= start_date)

    if end_date:
        query = query.filter(Decision.created_at <= end_date)

    total = query.count()

    approved = query.filter(Decision.status == "Approved").count()
    rejected = query.filter(Decision.status == "Rejected").count()
    under_review = query.filter(Decision.status == "Under Review").count()
    archived = query.filter(Decision.status == "Archived").count()

    total_users = db.query(func.count(User.id)).scalar() or 0

    return {
        "decision_statistics": {
            "total_decisions": total,
            "approved": approved,
            "rejected": rejected,
            "under_review": under_review,
            "archived": archived,
        },
        "user_statistics": {
            "total_users": total_users,
        },
    }


# ============================================================
# ADMIN DECISION ACTIVITY
# ============================================================

@router.get("/admin/decision-activity")
def admin_decision_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.lower() not in ["admin", "administrator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )

    results = (
        db.query(
            func.date(Decision.created_at).label("date"),
            func.count(Decision.id).label("count"),
        )
        .group_by(func.date(Decision.created_at))
        .order_by(func.date(Decision.created_at))
        .all()
    )

    return {
        str(row.date): row.count
        for row in results
    }


# ============================================================
# ADMIN USER ACTIVITY
# ============================================================

@router.get("/admin/user-activity")
def admin_user_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.lower() not in ["admin", "administrator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )

    results = (
        db.query(
            ActivityLog.user_id,
            func.count(ActivityLog.id).label("activity_count"),
        )
        .group_by(ActivityLog.user_id)
        .order_by(func.count(ActivityLog.id).desc())
        .all()
    )

    return [
        {
            "user_id": row.user_id,
            "activity_count": row.activity_count,
        }
        for row in results
    ]


# ============================================================
# ACTIVITIES
# ============================================================

@router.get("/activities")
def get_activities(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ActivityLog)

    if current_user.role.lower() not in ["admin", "administrator"]:
        query = query.filter(ActivityLog.user_id == current_user.id)

    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)

    if action:
        query = query.filter(ActivityLog.action == action)

    if entity_type:
        query = query.filter(ActivityLog.entity_type == entity_type)

    return (
        query
        .order_by(ActivityLog.created_at.desc())
        .limit(100)
        .all()
    )