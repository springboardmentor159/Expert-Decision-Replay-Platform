from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.activity import ActivityLog
from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboards"])


def _role(user: User) -> str:
    return str(user.role).lower()


def _require_role(user: User, allowed: set[str]) -> None:
    if _role(user) not in allowed:
        raise HTTPException(status_code=403, detail="Insufficient permission")


def _status_counts(db: Session, query):
    rows = query.with_entities(Decision.status, func.count(Decision.id)).group_by(Decision.status).all()
    return {status: count for status, count in rows}


def _decision_metrics(db: Session, query):
    counts = _status_counts(db, query)
    return {
        "total_decisions": sum(counts.values()),
        "draft_decisions": counts.get("Draft", 0),
        "under_review": counts.get("Under Review", 0),
        "approved_decisions": counts.get("Approved", 0),
        "rejected_decisions": counts.get("Rejected", 0),
        "archived_decisions": counts.get("Archived", 0),
    }


def _date_filter(query, start_date, end_date):
    if start_date:
        query = query.filter(Decision.created_at >= start_date)
    if end_date:
        query = query.filter(Decision.created_at <= end_date)
    return query


@router.get("/employee")
def employee_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Decision).filter(Decision.created_by == current_user.id)
    metrics = _decision_metrics(db, query)
    metrics["pending_reviews"] = db.query(func.count(Approval.id)).filter(Approval.reviewer_id == current_user.id, Approval.status == "Pending").scalar() or 0
    metrics["recent_activities"] = db.query(ActivityLog).filter(ActivityLog.user_id == current_user.id).order_by(ActivityLog.created_at.desc()).limit(10).all()
    return metrics


@router.get("/employee/decisions")
def employee_decisions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Decision).filter(Decision.created_by == current_user.id).order_by(Decision.updated_at.desc()).all()


@router.get("/employee/pending-reviews")
def employee_pending_reviews(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Approval).filter(Approval.reviewer_id == current_user.id, Approval.status == "Pending").order_by(Approval.created_at.asc()).all()


@router.get("/employee/recent-activities")
def employee_recent_activities(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(ActivityLog).filter(ActivityLog.user_id == current_user.id).order_by(ActivityLog.created_at.desc()).limit(50).all()


@router.get("/manager")
def manager_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_role(current_user, {"manager"})
    query = db.query(Decision).join(User, Decision.created_by == User.id).filter(User.department == current_user.department)
    metrics = _decision_metrics(db, query)
    metrics["team_decisions"] = metrics.pop("total_decisions")
    metrics["pending_approvals"] = db.query(func.count(Approval.id)).filter(Approval.status == "Pending").scalar() or 0
    metrics["recent_team_activities"] = []
    return metrics


@router.get("/manager/team-decisions")
def manager_team_decisions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_role(current_user, {"manager"})
    return db.query(Decision).join(User, Decision.created_by == User.id).filter(User.department == current_user.department).order_by(Decision.updated_at.desc()).all()


@router.get("/manager/pending-approvals")
def manager_pending_approvals(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_role(current_user, {"manager"})
    return db.query(Approval).join(Decision, Approval.decision_id == Decision.id).join(User, Decision.created_by == User.id).filter(User.department == current_user.department, Approval.status == "Pending").order_by(Approval.created_at.asc()).all()


@router.get("/manager/statistics")
def manager_statistics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_role(current_user, {"manager"})
    query = db.query(Decision).join(User, Decision.created_by == User.id).filter(User.department == current_user.department)
    return _decision_metrics(db, query)


@router.get("/admin")
def admin_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_role(current_user, {"admin", "administrator"})
    return {"users": db.query(func.count(User.id)).scalar(), "decisions": _decision_metrics(db, db.query(Decision)), "recent_system_activities": db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(20).all()}


@router.get("/admin/analytics")
def admin_analytics(start_date: datetime | None = None, end_date: datetime | None = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_role(current_user, {"admin", "administrator"})
    if start_date and end_date and end_date < start_date:
        raise HTTPException(status_code=422, detail="end_date must be on or after start_date")
    decision_query = _date_filter(db.query(Decision), start_date, end_date)
    metrics = _decision_metrics(db, decision_query)
    approval_query = db.query(Approval)
    if start_date:
        approval_query = approval_query.filter(Approval.created_at >= start_date)
    if end_date:
        approval_query = approval_query.filter(Approval.created_at <= end_date)
    metrics.update({"total_users": db.query(func.count(User.id)).scalar() or 0, "active_users": db.query(func.count(func.distinct(ActivityLog.user_id))).scalar() or 0, "total_approvals": approval_query.count(), "pending_approvals": approval_query.filter(Approval.status == "Pending").count(), "approved_approvals": approval_query.filter(Approval.status == "Approved").count(), "rejected_approvals": approval_query.filter(Approval.status == "Rejected").count()})
    return metrics


@router.get("/admin/decision-activity")
def admin_decision_activity(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_role(current_user, {"admin", "administrator"})
    rows = db.query(func.date(Decision.created_at), func.count(Decision.id)).group_by(func.date(Decision.created_at)).order_by(func.date(Decision.created_at)).all()
    return {str(day): count for day, count in rows}


@router.get("/admin/approval-statistics")
def admin_approval_statistics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_role(current_user, {"admin", "administrator"})
    total = db.query(func.count(Approval.id)).scalar() or 0
    completed = db.query(func.count(Approval.id)).filter(Approval.status.in_(["Approved", "Rejected"])).scalar() or 0
    durations = db.query(func.extract("epoch", Approval.completed_at - Approval.created_at)).filter(Approval.completed_at.isnot(None)).all()
    values = [float(value[0]) for value in durations if value[0] is not None]
    return {"total_approvals": total, "completed_approvals": completed, "completion_rate": round(completed * 100 / total, 2) if total else 0, "average_approval_time": sum(values) / len(values) if values else None, "fastest_approval": min(values) if values else None, "slowest_approval": max(values) if values else None, "pending_approvals": total - completed}


@router.get("/admin/user-activity")
def admin_user_activity(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_role(current_user, {"admin", "administrator"})
    rows = db.query(ActivityLog.user_id, func.count(ActivityLog.id).label("activity_count")).group_by(ActivityLog.user_id).order_by(func.count(ActivityLog.id).desc()).all()
    return [{"user_id": user_id, "activity_count": activity_count} for user_id, activity_count in rows]
