from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional

from app.models.decision import Decision
from app.models.user import User
from app.models.activity_log import ActivityLog



def get_employee_dashboard(db: Session, user_id: int) -> dict:
    base = db.query(Decision).filter(Decision.created_by == user_id)

    total        = base.count()
    draft        = base.filter(Decision.status == "Draft").count()
    under_review = base.filter(Decision.status == "Under Review").count()
    approved     = base.filter(Decision.status == "Approved").count()
    rejected     = base.filter(Decision.status == "Rejected").count()

    recent = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == user_id)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "total_decisions": total,
        "draft_decisions": draft,
        "under_review": under_review,
        "approved_decisions": approved,
        "rejected_decisions": rejected,
        "pending_reviews": 0,
        "recent_activities": recent,
    }


def get_employee_decisions(db: Session, user_id: int) -> list:
    return (
        db.query(Decision)
        .filter(Decision.created_by == user_id)
        .order_by(Decision.created_at.desc())
        .all()
    )


def get_employee_recent_activities(db: Session, user_id: int) -> list:
    return (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == user_id)
        .order_by(ActivityLog.created_at.desc())
        .limit(20)
        .all()
    )

def get_manager_team_user_ids(db: Session, manager: User) -> list:
    """Get all users in the same department as the manager."""
    if not manager.department:
        return []
    users = (
        db.query(User.id)
        .filter(User.department == manager.department)
        .all()
    )
    return [u.id for u in users]


def get_manager_dashboard(db: Session, manager: User) -> dict:
    team_ids = get_manager_team_user_ids(db, manager)

    if not team_ids:
        return {
            "team_decisions": 0,
            "pending_approvals": 0,
            "approved_decisions": 0,
            "rejected_decisions": 0,
            "under_review": 0,
        }

    base = db.query(Decision).filter(Decision.created_by.in_(team_ids))

    return {
        "team_decisions":    base.count(),
        "pending_approvals": base.filter(Decision.status == "Under Review").count(),
        "approved_decisions": base.filter(Decision.status == "Approved").count(),
        "rejected_decisions": base.filter(Decision.status == "Rejected").count(),
        "under_review":      base.filter(Decision.status == "Under Review").count(),
    }


def get_manager_team_decisions(db: Session, manager: User) -> list:
    team_ids = get_manager_team_user_ids(db, manager)
    if not team_ids:
        return []
    return (
        db.query(Decision)
        .filter(Decision.created_by.in_(team_ids))
        .order_by(Decision.created_at.desc())
        .all()
    )


def get_manager_statistics(db: Session, manager: User) -> dict:
    team_ids = get_manager_team_user_ids(db, manager)
    if not team_ids:
        return {
            "total": 0, "draft": 0, "under_review": 0,
            "approved": 0, "rejected": 0, "archived": 0
        }
    base = db.query(Decision).filter(Decision.created_by.in_(team_ids))
    return {
        "total":        base.count(),
        "draft":        base.filter(Decision.status == "Draft").count(),
        "under_review": base.filter(Decision.status == "Under Review").count(),
        "approved":     base.filter(Decision.status == "Approved").count(),
        "rejected":     base.filter(Decision.status == "Rejected").count(),
        "archived":     base.filter(Decision.status == "Archived").count(),
    }


def get_admin_dashboard(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> dict:
    d_query = db.query(Decision)
    if start_date:
        d_query = d_query.filter(Decision.created_at >= start_date)
    if end_date:
        d_query = d_query.filter(Decision.created_at <= end_date)

    total_decisions  = d_query.count()
    approved         = d_query.filter(Decision.status == "Approved").count()
    rejected         = d_query.filter(Decision.status == "Rejected").count()
    under_review     = d_query.filter(Decision.status == "Under Review").count()
    total_users      = db.query(User).count()

    return {
        "total_users":        total_users,
        "total_decisions":    total_decisions,
        "pending_approvals":  under_review,
        "approved_decisions": approved,
        "rejected_decisions": rejected,
        "under_review":       under_review,
        "total_approvals":    0,
        "completion_rate":    0.0,
    }


def get_admin_analytics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> dict:
    d_query = db.query(Decision)
    if start_date:
        d_query = d_query.filter(Decision.created_at >= start_date)
    if end_date:
        d_query = d_query.filter(Decision.created_at <= end_date)

    total_users  = db.query(User).count()
    active_users = (
        db.query(func.count(func.distinct(ActivityLog.user_id)))
        .filter(ActivityLog.created_at >= datetime.utcnow() - timedelta(days=30))
        .scalar()
    )
    users_by_role = dict(
        db.query(User.role, func.count(User.id))
        .group_by(User.role)
        .all()
    )

    return {
        "decision_statistics": {
            "total":        d_query.count(),
            "approved":     d_query.filter(Decision.status == "Approved").count(),
            "rejected":     d_query.filter(Decision.status == "Rejected").count(),
            "under_review": d_query.filter(Decision.status == "Under Review").count(),
            "archived":     d_query.filter(Decision.status == "Archived").count(),
            "draft":        d_query.filter(Decision.status == "Draft").count(),
        },
        "user_statistics": {
            "total_users":          total_users,
            "active_users_last_30d": active_users,
            "users_by_role":        users_by_role,
        },
    }


def get_decision_activity(
    db: Session,
    group_by: str = "day",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> dict:
    if group_by == "day":
        trunc = func.date_trunc("day", Decision.created_at)
    elif group_by == "week":
        trunc = func.date_trunc("week", Decision.created_at)
    else:
        trunc = func.date_trunc("month", Decision.created_at)

    query = db.query(
        trunc.label("period"),
        func.count(Decision.id).label("count")
    )
    if start_date:
        query = query.filter(Decision.created_at >= start_date)
    if end_date:
        query = query.filter(Decision.created_at <= end_date)

    rows = query.group_by("period").order_by("period").all()
    return {str(row.period.date()): row.count for row in rows}


def get_user_activity(db: Session) -> list:
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    rows = (
        db.query(
            ActivityLog.user_id,
            User.full_name,
            func.max(ActivityLog.created_at).label("last_active"),
            func.count(ActivityLog.id).label("action_count"),
        )
        .join(User, User.id == ActivityLog.user_id)
        .filter(ActivityLog.created_at >= thirty_days_ago)
        .group_by(ActivityLog.user_id, User.full_name)
        .order_by(func.count(ActivityLog.id).desc())
        .all()
    )
    return [
        {
            "user_id":      r.user_id,
            "full_name":    r.full_name,
            "last_active":  r.last_active,
            "action_count": r.action_count,
        }
        for r in rows
    ]