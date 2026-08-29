from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.decision import Decision
from app.models.approval import Approval
from app.models.activity_log import ActivityLog

from app.schemas.dashboard import (
    EmployeeDashboardResponse,
    ManagerDashboardResponse,
    AdminDashboardResponse
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


def get_role(current_user):
    return str(current_user.get("role", "")).lower()


# =========================================================
# EMPLOYEE DASHBOARD
# =========================================================

@router.get(
    "/employee",
    response_model=EmployeeDashboardResponse
)
def employee_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user_id = int(current_user["sub"])

    decisions = (
        db.query(Decision)
        .filter(Decision.created_by == user_id)
    )

    total = decisions.count()

    draft = decisions.filter(
        Decision.status == "Draft"
    ).count()

    under_review = decisions.filter(
        Decision.status == "Under Review"
    ).count()

    approved = decisions.filter(
        Decision.status == "Approved"
    ).count()

    rejected = decisions.filter(
        Decision.status == "Rejected"
    ).count()

    archived = decisions.filter(
        Decision.status == "Archived"
    ).count()

    pending_reviews = (
        db.query(Approval)
        .filter(
            Approval.assigned_to == user_id,
            Approval.status == "Pending"
        )
        .count()
    )

    return {
        "total_decisions": total,
        "draft_decisions": draft,
        "under_review": under_review,
        "approved_decisions": approved,
        "rejected_decisions": rejected,
        "archived_decisions": archived,
        "pending_reviews": pending_reviews
    }


# =========================================================
# EMPLOYEE DECISIONS
# =========================================================

@router.get(
    "/employee/decisions"
)
def employee_decisions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user_id = int(current_user["sub"])

    decisions = (
        db.query(Decision)
        .filter(Decision.created_by == user_id)
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
            "updated_at": decision.updated_at
        }
        for decision in decisions
    ]


# =========================================================
# EMPLOYEE PENDING REVIEWS
# =========================================================

@router.get(
    "/employee/pending-reviews"
)
def employee_pending_reviews(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user_id = int(current_user["sub"])

    approvals = (
        db.query(Approval)
        .filter(
            Approval.assigned_to == user_id,
            Approval.status == "Pending"
        )
        .order_by(Approval.created_at.desc())
        .all()
    )

    return [
        {
            "approval_id": approval.id,
            "decision_id": approval.decision_id,
            "approval_level": approval.approval_level,
            "status": approval.status,
            "created_at": approval.created_at
        }
        for approval in approvals
    ]


# =========================================================
# EMPLOYEE RECENT ACTIVITIES
# =========================================================

@router.get(
    "/employee/recent-activities"
)
def employee_recent_activities(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user_id = int(current_user["sub"])

    activities = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == user_id)
        .order_by(ActivityLog.created_at.desc())
        .limit(20)
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


# =========================================================
# MANAGER DASHBOARD
# =========================================================

@router.get(
    "/manager",
    response_model=ManagerDashboardResponse
)
def manager_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    role = get_role(current_user)

    if role not in ["manager", "administrator", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Manager access required"
        )

    user_id = int(current_user["sub"])

    manager = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if manager is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    team_decisions = (
        db.query(Decision)
        .join(User, Decision.created_by == User.id)
        .filter(User.department == manager.department)
    )

    team_count = team_decisions.count()

    draft = team_decisions.filter(
        Decision.status == "Draft"
    ).count()

    under_review = team_decisions.filter(
        Decision.status == "Under Review"
    ).count()

    approved = team_decisions.filter(
        Decision.status == "Approved"
    ).count()

    rejected = team_decisions.filter(
        Decision.status == "Rejected"
    ).count()

    pending_approvals = (
        db.query(Approval)
        .filter(
            Approval.assigned_to == user_id,
            Approval.status == "Pending"
        )
        .count()
    )

    return {
        "team_decisions": team_count,
        "pending_approvals": pending_approvals,
        "approved_decisions": approved,
        "rejected_decisions": rejected,
        "under_review": under_review,
        "draft_decisions": draft
    }


# =========================================================
# MANAGER TEAM DECISIONS
# =========================================================

@router.get(
    "/manager/team-decisions"
)
def manager_team_decisions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    role = get_role(current_user)

    if role not in ["manager", "administrator", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Manager access required"
        )

    user_id = int(current_user["sub"])

    manager = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if manager is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    decisions = (
        db.query(Decision)
        .join(User, Decision.created_by == User.id)
        .filter(User.department == manager.department)
        .order_by(Decision.created_at.desc())
        .all()
    )

    return [
        {
            "id": decision.id,
            "title": decision.title,
            "category": decision.category,
            "status": decision.status,
            "created_by": decision.created_by,
            "created_at": decision.created_at
        }
        for decision in decisions
    ]


# =========================================================
# MANAGER PENDING APPROVALS
# =========================================================

@router.get(
    "/manager/pending-approvals"
)
def manager_pending_approvals(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    role = get_role(current_user)

    if role not in ["manager", "administrator", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Manager access required"
        )

    user_id = int(current_user["sub"])

    approvals = (
        db.query(Approval)
        .filter(
            Approval.assigned_to == user_id,
            Approval.status == "Pending"
        )
        .order_by(Approval.created_at.desc())
        .all()
    )

    return [
        {
            "approval_id": approval.id,
            "decision_id": approval.decision_id,
            "approval_level": approval.approval_level,
            "assigned_reviewer": approval.assigned_to,
            "status": approval.status,
            "created_at": approval.created_at
        }
        for approval in approvals
    ]


# =========================================================
# MANAGER STATISTICS
# =========================================================

@router.get(
    "/manager/statistics"
)
def manager_statistics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    role = get_role(current_user)

    if role not in ["manager", "administrator", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Manager access required"
        )

    user_id = int(current_user["sub"])

    manager = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if manager is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    base = (
        db.query(Decision)
        .join(User, Decision.created_by == User.id)
        .filter(User.department == manager.department)
    )

    return {
        "total_decisions": base.count(),
        "draft_decisions": base.filter(
            Decision.status == "Draft"
        ).count(),
        "under_review": base.filter(
            Decision.status == "Under Review"
        ).count(),
        "approved_decisions": base.filter(
            Decision.status == "Approved"
        ).count(),
        "rejected_decisions": base.filter(
            Decision.status == "Rejected"
        ).count(),
        "archived_decisions": base.filter(
            Decision.status == "Archived"
        ).count()
    }


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@router.get(
    "/admin",
    response_model=AdminDashboardResponse
)
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    role = get_role(current_user)

    if role not in ["administrator", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Administrator access required"
        )

    return {
        "total_users": db.query(User).count(),
        "total_decisions": db.query(Decision).count(),
        "approved_decisions": db.query(Decision).filter(
            Decision.status == "Approved"
        ).count(),
        "rejected_decisions": db.query(Decision).filter(
            Decision.status == "Rejected"
        ).count(),
        "under_review": db.query(Decision).filter(
            Decision.status == "Under Review"
        ).count(),
        "pending_approvals": db.query(Approval).filter(
            Approval.status == "Pending"
        ).count()
    }


# =========================================================
# ADMIN ANALYTICS
# =========================================================

@router.get(
    "/admin/analytics"
)
def admin_analytics(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    role = get_role(current_user)

    if role not in ["administrator", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Administrator access required"
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date must be before end_date"
        )

    decision_query = db.query(Decision)

    if start_date:
        decision_query = decision_query.filter(
            Decision.created_at >= start_date
        )

    if end_date:
        decision_query = decision_query.filter(
            Decision.created_at <= end_date
        )

    return {
        "decision_statistics": {
            "total_decisions": decision_query.count(),
            "approved": decision_query.filter(
                Decision.status == "Approved"
            ).count(),
            "rejected": decision_query.filter(
                Decision.status == "Rejected"
            ).count(),
            "under_review": decision_query.filter(
                Decision.status == "Under Review"
            ).count(),
            "archived": decision_query.filter(
                Decision.status == "Archived"
            ).count()
        },
        "user_statistics": {
            "total_users": db.query(User).count(),
            "employee_users": db.query(User).filter(
                func.lower(User.role) == "employee"
            ).count(),
            "reviewer_users": db.query(User).filter(
                func.lower(User.role) == "reviewer"
            ).count(),
            "manager_users": db.query(User).filter(
                func.lower(User.role) == "manager"
            ).count(),
            "administrator_users": db.query(User).filter(
                func.lower(User.role).in_(
                    ["administrator", "admin"]
                )
            ).count()
        },
        "approval_statistics": {
            "total_approvals": db.query(Approval).count(),
            "pending_approvals": db.query(Approval).filter(
                Approval.status == "Pending"
            ).count(),
            "approved_approvals": db.query(Approval).filter(
                Approval.status == "Approved"
            ).count(),
            "rejected_approvals": db.query(Approval).filter(
                Approval.status == "Rejected"
            ).count()
        }
    }


# =========================================================
# DECISION ACTIVITY STATISTICS
# =========================================================

@router.get(
    "/admin/decision-activity"
)
def decision_activity_statistics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    role = get_role(current_user)

    if role not in ["administrator", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Administrator access required"
        )

    results = (
        db.query(
            func.date(Decision.created_at).label("date"),
            func.count(Decision.id).label("count")
        )
        .group_by(
            func.date(Decision.created_at)
        )
        .order_by(
            func.date(Decision.created_at)
        )
        .all()
    )

    return {
        str(row.date): row.count
        for row in results
    }


# =========================================================
# APPROVAL STATISTICS
# =========================================================

@router.get(
    "/admin/approval-statistics"
)
def approval_statistics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    role = get_role(current_user)

    if role not in ["administrator", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Administrator access required"
        )

    total = db.query(Approval).count()

    completed = db.query(Approval).filter(
        Approval.status.in_(["Approved", "Rejected"])
    ).count()

    pending = db.query(Approval).filter(
        Approval.status == "Pending"
    ).count()

    completion_rate = (
        (completed / total) * 100
        if total > 0
        else 0
    )

    completed_approvals = (
        db.query(Approval)
        .filter(
            Approval.completed_at.isnot(None)
        )
        .all()
    )

    turnaround_times = []

    for approval in completed_approvals:
        if approval.completed_at and approval.created_at:
            seconds = (
                approval.completed_at -
                approval.created_at
            ).total_seconds()

            turnaround_times.append(seconds)

    average_hours = (
        sum(turnaround_times) /
        len(turnaround_times) /
        3600
        if turnaround_times
        else 0
    )

    fastest_hours = (
        min(turnaround_times) / 3600
        if turnaround_times
        else 0
    )

    slowest_hours = (
        max(turnaround_times) / 3600
        if turnaround_times
        else 0
    )

    return {
        "total_approvals": total,
        "completed_approvals": completed,
        "pending_approvals": pending,
        "completion_rate": round(completion_rate, 2),
        "average_approval_time_hours": round(
            average_hours,
            2
        ),
        "fastest_approval_hours": round(
            fastest_hours,
            2
        ),
        "slowest_approval_hours": round(
            slowest_hours,
            2
        )
    }


# =========================================================
# USER ACTIVITY
# =========================================================

@router.get(
    "/admin/user-activity"
)
def user_activity(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    role = get_role(current_user)

    if role not in ["administrator", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Administrator access required"
        )

    activities = (
        db.query(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .limit(50)
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