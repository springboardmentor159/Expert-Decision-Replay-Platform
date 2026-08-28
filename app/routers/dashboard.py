from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.activity_log import ActivityLog
from app.models.approval import Approval
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.user import User
from app.routers.users import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboards"])


def require_roles(*roles):
    def dependency(current_user=Depends(get_current_user)):
        if current_user.get("role") not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return dependency


def _counts(query):
    rows = query.with_entities(Decision.status, func.count(Decision.id)).group_by(Decision.status).all()
    values = {status: count for status, count in rows}
    return {
        "total_decisions": sum(values.values()),
        "draft_decisions": values.get("Draft", 0),
        "under_review": values.get("Under Review", 0),
        "approved_decisions": values.get("Approved", 0),
        "rejected_decisions": values.get("Rejected", 0),
        "archived_decisions": values.get("Archived", 0),
    }


def _activities(db, user_id=None, limit=10):
    query = db.query(ActivityLog).order_by(ActivityLog.created_at.desc())
    if user_id is not None:
        query = query.filter(ActivityLog.user_id == user_id)
    return query.limit(limit).all()


@router.get("/employee")
def employee_dashboard(db: Session = Depends(get_db), user=Depends(require_roles("Employee", "Reviewer", "Manager", "Administrator"))):
    user_id = int(user["sub"])
    result = _counts(db.query(Decision).filter(Decision.created_by == user_id))
    result["pending_reviews"] = db.query(Approval).filter(Approval.reviewer_id == user_id, Approval.status == "Pending").count()
    result["recent_activities"] = _activities(db, user_id)
    return result


@router.get("/employee/decisions")
def employee_decisions(db: Session = Depends(get_db), user=Depends(require_roles("Employee", "Reviewer", "Manager", "Administrator"))):
    return db.query(Decision).filter(Decision.created_by == int(user["sub"])).order_by(Decision.updated_at.desc()).all()


@router.get("/employee/pending-reviews")
def employee_pending_reviews(db: Session = Depends(get_db), user=Depends(require_roles("Employee", "Reviewer", "Manager", "Administrator"))):
    return db.query(Approval).filter(Approval.reviewer_id == int(user["sub"]), Approval.status == "Pending").all()


@router.get("/employee/recent-activities")
def employee_recent_activities(db: Session = Depends(get_db), user=Depends(require_roles("Employee", "Reviewer", "Manager", "Administrator"))):
    return _activities(db, int(user["sub"]), 50)


def _manager_decisions(db, user):
    manager = db.query(User).filter(User.id == int(user["sub"])).first()
    if not manager:
        raise HTTPException(status_code=403, detail="Authenticated user not found")
    return db.query(Decision).join(User, Decision.created_by == User.id).filter(User.department == manager.department)


def _manager(db, user):
    manager = db.query(User).filter(User.id == int(user["sub"])).first()
    if not manager:
        raise HTTPException(status_code=403, detail="Authenticated user not found")
    return manager


@router.get("/manager")
def manager_dashboard(db: Session = Depends(get_db), user=Depends(require_roles("Manager"))):
    manager = _manager(db, user)
    result = _counts(_manager_decisions(db, user))
    result["pending_approvals"] = db.query(Approval).join(User, Approval.reviewer_id == User.id).filter(User.department == manager.department, Approval.status == "Pending").count()
    result["recent_team_activities"] = db.query(ActivityLog).join(User, ActivityLog.user_id == User.id).filter(User.department == manager.department).order_by(ActivityLog.created_at.desc()).limit(20).all()
    return result


@router.get("/manager/team-decisions")
def manager_team_decisions(db: Session = Depends(get_db), user=Depends(require_roles("Manager"))):
    return _manager_decisions(db, user).order_by(Decision.created_at.desc()).all()


@router.get("/manager/pending-approvals")
def manager_pending_approvals(db: Session = Depends(get_db), user=Depends(require_roles("Manager"))):
    manager = _manager(db, user)
    return db.query(Approval).join(User, Approval.reviewer_id == User.id).filter(User.department == manager.department, Approval.status == "Pending").all()


@router.get("/manager/statistics")
def manager_statistics(db: Session = Depends(get_db), user=Depends(require_roles("Manager"))):
    return _counts(_manager_decisions(db, user))


def _date_filter(query, column, start_date, end_date):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=422, detail="start_date must be before end_date")
    if start_date:
        query = query.filter(column >= start_date)
    if end_date:
        query = query.filter(column < end_date + timedelta(days=1))
    return query


@router.get("/admin")
def admin_dashboard(db: Session = Depends(get_db), user=Depends(require_roles("Administrator"))):
    return {"system_analytics": admin_analytics(db, user), "recent_system_activities": _activities(db, limit=20)}


@router.get("/admin/analytics")
def admin_analytics(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, db: Session = Depends(get_db), user=Depends(require_roles("Administrator"))):
    decisions = _date_filter(db.query(Decision), Decision.created_at, start_date, end_date)
    approvals = _date_filter(db.query(Approval), Approval.created_at, start_date, end_date)
    total_approvals = approvals.count()
    completed = approvals.filter(Approval.status.in_(["Approved", "Rejected"])).count()
    active_users = db.query(ActivityLog.user_id).filter(ActivityLog.user_id.isnot(None))
    active_users = _date_filter(active_users, ActivityLog.created_at, start_date, end_date).distinct().count()
    return {"decision_statistics": _counts(decisions), "user_statistics": {"total_users": db.query(User).count(), "active_users": active_users, "users_by_role": dict(db.query(User.role, func.count(User.id)).group_by(User.role).all())}, "approval_statistics": {"total_approvals": total_approvals, "pending_approvals": approvals.filter(Approval.status == "Pending").count(), "approved_approvals": approvals.filter(Approval.status == "Approved").count(), "rejected_approvals": approvals.filter(Approval.status == "Rejected").count(), "completion_rate": round(completed * 100 / total_approvals, 2) if total_approvals else 0}}


@router.get("/admin/decision-activity")
def decision_activity(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, db: Session = Depends(get_db), user=Depends(require_roles("Administrator"))):
    query = _date_filter(db.query(func.date(Decision.created_at), func.count(Decision.id)), Decision.created_at, start_date, end_date)
    return {str(day): count for day, count in query.group_by(func.date(Decision.created_at)).order_by(func.date(Decision.created_at)).all()}


@router.get("/admin/approval-statistics")
def approval_statistics(db: Session = Depends(get_db), user=Depends(require_roles("Administrator"))):
    duration = func.extract("epoch", Approval.completed_at - Approval.created_at)
    average, fastest, slowest = db.query(func.avg(duration), func.min(duration), func.max(duration)).filter(Approval.completed_at.isnot(None)).one()
    return {"average_approval_time_seconds": float(average or 0), "fastest_seconds": float(fastest or 0), "slowest_seconds": float(slowest or 0), "pending_approvals": db.query(Approval).filter(Approval.status == "Pending").count()}


@router.get("/admin/user-activity")
def user_activity(db: Session = Depends(get_db), user=Depends(require_roles("Administrator"))):
    return db.query(ActivityLog.user_id, func.max(ActivityLog.created_at).label("last_activity"), func.count(ActivityLog.id).label("activity_count")).group_by(ActivityLog.user_id).order_by(func.max(ActivityLog.created_at).desc()).all()