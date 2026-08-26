from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from sqlalchemy import Date, cast, func
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.activity_log import ActivityLog
from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User
from app.schemas.activity_log import ActivityLogResponse
from app.schemas.approval import ApprovalResponse
from app.schemas.dashboard import (
    ActiveUserItem,
    AdminAnalyticsResponse,
    AdminDashboardResponse,
    ApprovalPerformanceResponse,
    ApprovalStats,
    DecisionStats,
    EmployeeDashboardResponse,
    ManagerDashboardResponse,
    ManagerStatisticsResponse,
    UserActivityResponse,
    UserStats,
)
from app.schemas.decision import DecisionResponse

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


def _get_team_user_ids(db: Session, manager: User) -> List[int]:
    """
    Returns user IDs belonging to manager's team based on department.
    If manager has department, finds all users in same department.
    Otherwise includes manager himself.
    """
    if manager.department:
        users = db.query(User.id).filter(User.department == manager.department).all()
        return [u[0] for u in users]
    return [manager.id]


# =============================================================================
# 1. EMPLOYEE DASHBOARD
# =============================================================================

@router.get(
    "/employee",
    response_model=EmployeeDashboardResponse,
    summary="Get employee dashboard metrics"
)
def get_employee_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id

    total_decisions = db.query(func.count(Decision.id)).filter(Decision.created_by == user_id).scalar() or 0
    draft_decisions = db.query(func.count(Decision.id)).filter(Decision.created_by == user_id, Decision.status == "Draft").scalar() or 0
    under_review = db.query(func.count(Decision.id)).filter(Decision.created_by == user_id, Decision.status == "Under Review").scalar() or 0
    approved_decisions = db.query(func.count(Decision.id)).filter(Decision.created_by == user_id, Decision.status == "Approved").scalar() or 0
    rejected_decisions = db.query(func.count(Decision.id)).filter(Decision.created_by == user_id, Decision.status == "Rejected").scalar() or 0

    pending_reviews = db.query(func.count(Approval.id)).filter(Approval.reviewer_id == user_id, Approval.status == "Pending").scalar() or 0

    recent_activities = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == user_id)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
        .all()
    )

    return EmployeeDashboardResponse(
        total_decisions=total_decisions,
        draft_decisions=draft_decisions,
        under_review=under_review,
        approved_decisions=approved_decisions,
        rejected_decisions=rejected_decisions,
        pending_reviews=pending_reviews,
        recent_activities=recent_activities
    )


@router.get(
    "/employee/decisions",
    response_model=List[DecisionResponse],
    summary="Get decisions created by the current employee"
)
def get_employee_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Decision)
        .filter(Decision.created_by == current_user.id)
        .order_by(Decision.created_at.desc())
        .all()
    )


@router.get(
    "/employee/pending-reviews",
    response_model=List[ApprovalResponse],
    summary="Get pending reviews assigned to the current employee"
)
def get_employee_pending_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Approval)
        .filter(Approval.reviewer_id == current_user.id, Approval.status == "Pending")
        .order_by(Approval.created_at.desc())
        .all()
    )


@router.get(
    "/employee/recent-activities",
    response_model=List[ActivityLogResponse],
    summary="Get recent activities performed by the current employee"
)
def get_employee_recent_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == current_user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(20)
        .all()
    )


# =============================================================================
# 2. MANAGER DASHBOARD
# =============================================================================

@router.get(
    "/manager",
    response_model=ManagerDashboardResponse,
    summary="Get manager dashboard metrics"
)
def get_manager_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Manager", "Administrator"]:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access restricted to Managers and Administrators"
        )

    team_user_ids = _get_team_user_ids(db, current_user)

    team_decisions = db.query(func.count(Decision.id)).filter(Decision.created_by.in_(team_user_ids)).scalar() or 0
    approved_decisions = db.query(func.count(Decision.id)).filter(Decision.created_by.in_(team_user_ids), Decision.status == "Approved").scalar() or 0
    rejected_decisions = db.query(func.count(Decision.id)).filter(Decision.created_by.in_(team_user_ids), Decision.status == "Rejected").scalar() or 0
    under_review = db.query(func.count(Decision.id)).filter(Decision.created_by.in_(team_user_ids), Decision.status == "Under Review").scalar() or 0

    pending_approvals = (
        db.query(func.count(Approval.id))
        .join(Decision, Approval.decision_id == Decision.id)
        .filter(Decision.created_by.in_(team_user_ids), Approval.status == "Pending")
        .scalar() or 0
    )

    recent_activities = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id.in_(team_user_ids))
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
        .all()
    )

    return ManagerDashboardResponse(
        team_decisions=team_decisions,
        pending_approvals=pending_approvals,
        approved_decisions=approved_decisions,
        rejected_decisions=rejected_decisions,
        under_review=under_review,
        recent_activities=recent_activities
    )


@router.get(
    "/manager/team-decisions",
    response_model=List[DecisionResponse],
    summary="Get decisions created by members of manager's team"
)
def get_manager_team_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Manager", "Administrator"]:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access restricted to Managers and Administrators"
        )

    team_user_ids = _get_team_user_ids(db, current_user)
    return (
        db.query(Decision)
        .filter(Decision.created_by.in_(team_user_ids))
        .order_by(Decision.created_at.desc())
        .all()
    )


@router.get(
    "/manager/pending-approvals",
    response_model=List[ApprovalResponse],
    summary="Get pending approvals for manager's team"
)
def get_manager_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Manager", "Administrator"]:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access restricted to Managers and Administrators"
        )

    team_user_ids = _get_team_user_ids(db, current_user)
    return (
        db.query(Approval)
        .join(Decision, Approval.decision_id == Decision.id)
        .filter(Decision.created_by.in_(team_user_ids), Approval.status == "Pending")
        .order_by(Approval.created_at.desc())
        .all()
    )


@router.get(
    "/manager/statistics",
    response_model=ManagerStatisticsResponse,
    summary="Get statistical decision metrics for manager's team"
)
def get_manager_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Manager", "Administrator"]:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access restricted to Managers and Administrators"
        )

    team_user_ids = _get_team_user_ids(db, current_user)

    total = db.query(func.count(Decision.id)).filter(Decision.created_by.in_(team_user_ids)).scalar() or 0
    draft = db.query(func.count(Decision.id)).filter(Decision.created_by.in_(team_user_ids), Decision.status == "Draft").scalar() or 0
    review = db.query(func.count(Decision.id)).filter(Decision.created_by.in_(team_user_ids), Decision.status == "Under Review").scalar() or 0
    approved = db.query(func.count(Decision.id)).filter(Decision.created_by.in_(team_user_ids), Decision.status == "Approved").scalar() or 0
    rejected = db.query(func.count(Decision.id)).filter(Decision.created_by.in_(team_user_ids), Decision.status == "Rejected").scalar() or 0
    archived = db.query(func.count(Decision.id)).filter(Decision.created_by.in_(team_user_ids), Decision.status == "Archived").scalar() or 0

    return ManagerStatisticsResponse(
        total_decisions=total,
        draft_decisions=draft,
        under_review=review,
        approved_decisions=approved,
        rejected_decisions=rejected,
        archived_decisions=archived
    )


# =============================================================================
# 3. ADMIN DASHBOARD & ANALYTICS
# =============================================================================

@router.get(
    "/admin",
    response_model=AdminDashboardResponse,
    summary="Get organization-wide admin dashboard metrics"
)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Administrator":
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access restricted to Administrators only"
        )

    total_users = db.query(func.count(User.id)).scalar() or 0
    total_decisions = db.query(func.count(Decision.id)).scalar() or 0
    approved_decisions = db.query(func.count(Decision.id)).filter(Decision.status == "Approved").scalar() or 0
    rejected_decisions = db.query(func.count(Decision.id)).filter(Decision.status == "Rejected").scalar() or 0
    under_review = db.query(func.count(Decision.id)).filter(Decision.status == "Under Review").scalar() or 0
    archived_decisions = db.query(func.count(Decision.id)).filter(Decision.status == "Archived").scalar() or 0
    draft_decisions = db.query(func.count(Decision.id)).filter(Decision.status == "Draft").scalar() or 0

    total_approvals = db.query(func.count(Approval.id)).scalar() or 0
    pending_approvals = db.query(func.count(Approval.id)).filter(Approval.status == "Pending").scalar() or 0

    recent_activities = (
        db.query(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
        .all()
    )

    return AdminDashboardResponse(
        total_users=total_users,
        total_decisions=total_decisions,
        approved_decisions=approved_decisions,
        rejected_decisions=rejected_decisions,
        under_review=under_review,
        archived_decisions=archived_decisions,
        draft_decisions=draft_decisions,
        total_approvals=total_approvals,
        pending_approvals=pending_approvals,
        recent_activities=recent_activities
    )


@router.get(
    "/admin/analytics",
    response_model=AdminAnalyticsResponse,
    summary="Get organization analytics with optional date range filtering"
)
def get_admin_analytics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Administrator":
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access restricted to Administrators only"
        )

    # Date parsing
    parsed_start = None
    parsed_end = None
    if start_date:
        try:
            parsed_start = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid start_date format. Expected YYYY-MM-DD"
            )

    if end_date:
        try:
            parsed_end = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        except ValueError:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid end_date format. Expected YYYY-MM-DD"
            )

    if parsed_start and parsed_end and parsed_start > parsed_end:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )

    # Decision query
    d_query = db.query(Decision)
    if parsed_start:
        d_query = d_query.filter(Decision.created_at >= parsed_start)
    if parsed_end:
        d_query = d_query.filter(Decision.created_at <= parsed_end)

    total_decisions = d_query.count()
    approved_decisions = d_query.filter(Decision.status == "Approved").count()
    rejected_decisions = d_query.filter(Decision.status == "Rejected").count()
    under_review = d_query.filter(Decision.status == "Under Review").count()
    archived_decisions = d_query.filter(Decision.status == "Archived").count()
    draft_decisions = d_query.filter(Decision.status == "Draft").count()

    decision_stats = DecisionStats(
        total_decisions=total_decisions,
        approved_decisions=approved_decisions,
        rejected_decisions=rejected_decisions,
        under_review=under_review,
        archived_decisions=archived_decisions,
        draft_decisions=draft_decisions
    )

    # User query
    total_users = db.query(func.count(User.id)).scalar() or 0

    # Active users: users with activities in ActivityLog within date range
    act_query = db.query(ActivityLog.user_id).distinct()
    if parsed_start:
        act_query = act_query.filter(ActivityLog.created_at >= parsed_start)
    if parsed_end:
        act_query = act_query.filter(ActivityLog.created_at <= parsed_end)
    active_users = act_query.count()

    # Users by role
    roles_count = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    users_by_role = {role: count for role, count in roles_count}

    user_stats = UserStats(
        total_users=total_users,
        active_users=active_users,
        users_by_role=users_by_role
    )

    # Approval query
    a_query = db.query(Approval)
    if parsed_start:
        a_query = a_query.filter(Approval.created_at >= parsed_start)
    if parsed_end:
        a_query = a_query.filter(Approval.created_at <= parsed_end)

    total_approvals = a_query.count()
    pending_approvals = a_query.filter(Approval.status == "Pending").count()
    approved_approvals = a_query.filter(Approval.status == "Approved").count()
    rejected_approvals = a_query.filter(Approval.status == "Rejected").count()

    approval_stats = ApprovalStats(
        total_approvals=total_approvals,
        pending_approvals=pending_approvals,
        approved_approvals=approved_approvals,
        rejected_approvals=rejected_approvals
    )

    return AdminAnalyticsResponse(
        decision_statistics=decision_stats,
        user_statistics=user_stats,
        approval_statistics=approval_stats
    )


@router.get(
    "/admin/decision-activity",
    response_model=Dict[str, int],
    summary="Get daily decision creation breakdown"
)
def get_decision_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Administrator":
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access restricted to Administrators only"
        )

    # SQL aggregation: group by date
    if db.bind.dialect.name == "sqlite":
        date_expr = func.strftime("%Y-%m-%d", Decision.created_at)
    else:
        date_expr = func.to_char(Decision.created_at, "YYYY-MM-DD")

    results = (
        db.query(
            date_expr.label("creation_date"),
            func.count(Decision.id).label("count")
        )
        .group_by(date_expr)
        .order_by(date_expr.asc())
        .all()
    )

    return {str(row.creation_date): row.count for row in results if row.creation_date is not None}


@router.get(
    "/admin/approval-statistics",
    response_model=ApprovalPerformanceResponse,
    summary="Get approval performance and turnaround metrics"
)
def get_approval_performance_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Administrator":
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access restricted to Administrators only"
        )

    total_approvals = db.query(func.count(Approval.id)).scalar() or 0
    completed_approvals = db.query(func.count(Approval.id)).filter(Approval.status.in_(["Approved", "Rejected"])).scalar() or 0
    pending_approvals = db.query(func.count(Approval.id)).filter(Approval.status == "Pending").scalar() or 0

    # Safe completion rate calculation (handle division by zero)
    if total_approvals > 0:
        completion_rate = round((completed_approvals / total_approvals) * 100.0, 2)
    else:
        completion_rate = 0.0

    # Turnaround time calculations
    completed_records = (
        db.query(Approval)
        .filter(Approval.completed_at.isnot(None))
        .all()
    )

    durations_hours = []
    for app in completed_records:
        if app.completed_at and app.created_at:
            diff = (app.completed_at - app.created_at).total_seconds() / 3600.0
            durations_hours.append(max(0.0, diff))

    if durations_hours:
        avg_time = round(sum(durations_hours) / len(durations_hours), 2)
        fastest_time = round(min(durations_hours), 2)
        slowest_time = round(max(durations_hours), 2)
    else:
        avg_time = None
        fastest_time = None
        slowest_time = None

    return ApprovalPerformanceResponse(
        total_approvals=total_approvals,
        completed_approvals=completed_approvals,
        pending_approvals=pending_approvals,
        completion_rate=completion_rate,
        average_approval_time_hours=avg_time,
        fastest_approval_hours=fastest_time,
        slowest_approval_hours=slowest_time
    )


@router.get(
    "/admin/user-activity",
    response_model=UserActivityResponse,
    summary="Get active users and their activity metrics"
)
def get_admin_user_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Administrator":
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access restricted to Administrators only"
        )

    # Activity count & last activity per user
    user_stats = (
        db.query(
            User.id,
            User.full_name,
            User.email,
            User.role,
            func.count(ActivityLog.id).label("action_count"),
            func.max(ActivityLog.created_at).label("last_action_at")
        )
        .join(ActivityLog, User.id == ActivityLog.user_id)
        .group_by(User.id, User.full_name, User.email, User.role)
        .order_by(func.count(ActivityLog.id).desc())
        .all()
    )

    active_items = [
        ActiveUserItem(
            user_id=row.id,
            full_name=row.full_name,
            email=row.email,
            role=row.role,
            action_count=row.action_count,
            last_action_at=row.last_action_at
        )
        for row in user_stats
    ]

    return UserActivityResponse(
        active_users_count=len(active_items),
        active_users=active_items
    )
