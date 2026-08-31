from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.activity_log import ActivityLog
from app.models.decision import Decision
from app.models.enums import DecisionStatus, UserRole
from app.models.user import User
from app.schemas.dashboard import (
    ActivityItem,
    AdminAnalytics,
    AdminDashboard,
    AdminDecisionActivity,
    AdminUserActivity,
    ApprovalStatisticsResponse,
    DecisionActivityItem,
    DecisionStats,
    EmployeeDashboard,
    ManagerStatistics,
    StatusCount,
    UserActivitySummary,
    UserRoleCount,
    UserStats,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


def _require_manager_or_admin(user: User) -> None:
    if user.role not in (UserRole.MANAGER, UserRole.ADMINISTRATOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view manager dashboards",
        )


def _require_admin(user: User) -> None:
    if user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view admin dashboards",
        )


def _parse_date_param(value: str | None) -> datetime | None:
    """Parse a YYYY-MM-DD string into a datetime at midnight UTC. Returns None if value is None."""
    if value is None:
        return None
    try:
        d = date.fromisoformat(value)
        return datetime(d.year, d.month, d.day)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid date format: '{value}'. Expected YYYY-MM-DD.",
        )


def _validate_date_range(start_date: datetime | None, end_date: datetime | None) -> None:
    """Raise 422 if start_date is after end_date when both are provided."""
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date must not be after end_date.",
        )


def _status_breakdown(rows) -> dict:
    """Normalize a list of (status, count) tuples into all known statuses."""
    counts = {s.value: 0 for s in DecisionStatus}
    for status_value, count in rows:
        # status_value may be a DecisionStatus enum or a plain string at runtime
        key = status_value.value if isinstance(status_value, DecisionStatus) else str(status_value)
        if key in counts:
            counts[key] = count
    return counts


@router.get(
    "/employee",
    response_model=EmployeeDashboard,
)
def employee_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    status_rows = (
        db.query(Decision.status, func.count(Decision.id))
        .filter(Decision.created_by == current_user.id)
        .group_by(Decision.status)
        .all()
    )
    counts = _status_breakdown(status_rows)
    decisions_by_status = [
        StatusCount(status=s, count=counts[s]) for s in (s.value for s in DecisionStatus)
    ]
    total_decisions = sum(counts.values())

    recent_activity = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == current_user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(20)
        .all()
    )

    return EmployeeDashboard(
        user_id=current_user.id,
        total_decisions=total_decisions,
        decisions_by_status=decisions_by_status,
        recent_activity=recent_activity,
    )


@router.get(
    "/manager/statistics",
    response_model=ManagerStatistics,
)
def manager_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_manager_or_admin(current_user)

    # NOTE: No team / reporting-line concept exists on the User model yet, so
    # these counts are org-wide. This is a known limitation (see task.md).
    status_rows = (
        db.query(Decision.status, func.count(Decision.id))
        .group_by(Decision.status)
        .all()
    )
    counts = _status_breakdown(status_rows)

    return ManagerStatistics(
        scope="org-wide",
        total=sum(counts.values()),
        draft=counts[DecisionStatus.DRAFT.value],
        under_review=counts[DecisionStatus.UNDER_REVIEW.value],
        approved=counts[DecisionStatus.APPROVED.value],
        rejected=counts[DecisionStatus.REJECTED.value],
        archived=counts[DecisionStatus.ARCHIVED.value],
    )


@router.get(
    "/manager/pending-approvals",
)
def manager_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Authorization gate: only Manager / Administrator may attempt this.
    _require_manager_or_admin(current_user)

    # BLOCKED: the approval workflow (Approval model, approval statuses, assigned
    # reviewers) referenced by the spec does NOT exist in this codebase (verified
    # in Sprint 9 / Part A). There is no data source to read from, so this
    # endpoint is intentionally not implemented rather than fabricated.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            "Pending-approvals dashboard is blocked: the approval workflow "
            "(Approval model, approval statuses, assigned reviewers) has not "
            "been implemented yet. This depends on Part C/D of the overall task."
        ),
    )


@router.get(
    "/admin",
    response_model=AdminDashboard,
)
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)

    total_users = db.query(func.count(User.id)).scalar()
    total_decisions = db.query(func.count(Decision.id)).scalar()

    status_rows = (
        db.query(Decision.status, func.count(Decision.id))
        .group_by(Decision.status)
        .all()
    )
    counts = _status_breakdown(status_rows)

    decision_stats = DecisionStats(
        total=total_decisions,
        draft=counts[DecisionStatus.DRAFT.value],
        under_review=counts[DecisionStatus.UNDER_REVIEW.value],
        approved=counts[DecisionStatus.APPROVED.value],
        rejected=counts[DecisionStatus.REJECTED.value],
        archived=counts[DecisionStatus.ARCHIVED.value],
    )

    # Approval workflow not implemented - return None
    approval_stats = None

    recent_activity = (
        db.query(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .limit(20)
        .all()
    )

    return AdminDashboard(
        total_users=total_users,
        total_decisions=total_decisions,
        decision_stats=decision_stats,
        approval_stats=approval_stats,
        recent_activity=recent_activity,
    )


@router.get(
    "/admin/analytics",
    response_model=AdminAnalytics,
)
def admin_analytics(
    start_date: Optional[str] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)

    sd = _parse_date_param(start_date)
    ed = _parse_date_param(end_date)
    _validate_date_range(sd, ed)

    decision_query = db.query(Decision)
    if sd:
        decision_query = decision_query.filter(Decision.created_at >= sd)
    if ed:
        from datetime import timedelta
        decision_query = decision_query.filter(Decision.created_at < ed + timedelta(days=1))

    # Decision stats (scoped to date range)
    status_rows = (
        decision_query
        .with_entities(Decision.status, func.count(Decision.id))
        .group_by(Decision.status)
        .all()
    )
    counts = _status_breakdown(status_rows)
    total_decisions = sum(counts.values())

    decision_stats = DecisionStats(
        total=total_decisions,
        draft=counts[DecisionStatus.DRAFT.value],
        under_review=counts[DecisionStatus.UNDER_REVIEW.value],
        approved=counts[DecisionStatus.APPROVED.value],
        rejected=counts[DecisionStatus.REJECTED.value],
        archived=counts[DecisionStatus.ARCHIVED.value],
    )

    # User stats - using SQL GROUP BY (org-wide, not date-filtered)
    total_users = db.query(func.count(User.id)).scalar()

    # Active users: users who have created at least one decision (in date range)
    active_users = (
        decision_query
        .with_entities(func.count(func.distinct(Decision.created_by)))
        .scalar()
    )

    role_rows = (
        db.query(User.role, func.count(User.id))
        .group_by(User.role)
        .all()
    )
    by_role = [
        UserRoleCount(role=str(role).split(".")[-1] if hasattr(role, "value") else str(role), count=count)
        for role, count in role_rows
    ]

    user_stats = UserStats(
        total=total_users,
        active=active_users,
        by_role=by_role,
    )

    # Approval stats - not implemented
    approval_stats = None

    return AdminAnalytics(
        decision_stats=decision_stats,
        user_stats=user_stats,
        approval_stats=approval_stats,
    )


@router.get(
    "/admin/decision-activity",
    response_model=AdminDecisionActivity,
)
def admin_decision_activity(
    granularity: str = Query("day", pattern="^(day|week|month)$"),
    start_date: Optional[str] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)

    sd = _parse_date_param(start_date)
    ed = _parse_date_param(end_date)
    _validate_date_range(sd, ed)

    # SQL date truncation + GROUP BY - do not count in Python
    # Use dialect-aware approach for cross-database compatibility
    dialect_name = db.bind.dialect.name
    if dialect_name == "postgresql":
        if granularity == "day":
            date_trunc = func.date_trunc("day", Decision.created_at)
        elif granularity == "week":
            date_trunc = func.date_trunc("week", Decision.created_at)
        else:  # month
            date_trunc = func.date_trunc("month", Decision.created_at)
    else:  # SQLite (testing) - use strftime
        if granularity == "day":
            date_trunc = func.strftime("%Y-%m-%d", Decision.created_at)
        elif granularity == "week":
            date_trunc = func.strftime("%Y-%W", Decision.created_at)
        else:  # month
            date_trunc = func.strftime("%Y-%m", Decision.created_at)

    query = db.query(date_trunc.label("period"), func.count(Decision.id))
    if sd:
        query = query.filter(Decision.created_at >= sd)
    if ed:
        from datetime import timedelta
        query = query.filter(Decision.created_at < ed + timedelta(days=1))

    rows = (
        query
        .group_by("period")
        .order_by("period")
        .all()
    )

    data = [
        DecisionActivityItem(period=str(period), count=count)
        for period, count in rows
    ]

    return AdminDecisionActivity(granularity=granularity, data=data)


@router.get(
    "/admin/approval-statistics",
)
def admin_approval_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """BLOCKED: approval workflow not implemented.

    Returns 501 with a clear explanation. Authorization gate (Admin only) is
    enforced first so non-admins still get 403.
    """
    _require_admin(current_user)

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            "Approval statistics are blocked: the approval workflow "
            "(Approval model, approval statuses, assigned reviewers) has not "
            "been implemented yet. This depends on Part C/D of the overall task."
        ),
    )


@router.get(
    "/admin/user-activity",
    response_model=AdminUserActivity,
)
def admin_user_activity(
    start_date: Optional[str] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)

    sd = _parse_date_param(start_date)
    ed = _parse_date_param(end_date)
    _validate_date_range(sd, ed)

    query = db.query(ActivityLog)
    if sd:
        query = query.filter(ActivityLog.created_at >= sd)
    if ed:
        # Include the entire end date by adding 1 day
        from datetime import timedelta
        query = query.filter(ActivityLog.created_at < ed + timedelta(days=1))

    # Get all activity rows (for aggregation)
    activities = query.all()

    # Aggregate by user
    user_map: dict[int, dict] = {}
    for act in activities:
        uid = act.user_id
        if uid not in user_map:
            user_map[uid] = {"total_actions": 0, "actions_by_type": {}, "last_active": None}
        user_map[uid]["total_actions"] += 1
        key = f"{act.action}:{act.entity_type}"
        user_map[uid]["actions_by_type"][key] = user_map[uid]["actions_by_type"].get(key, 0) + 1
        if user_map[uid]["last_active"] is None or act.created_at > user_map[uid]["last_active"]:
            user_map[uid]["last_active"] = act.created_at

    # Fetch user details for active users
    user_ids = list(user_map.keys())
    users = db.query(User).filter(User.id.in_(user_ids)).all() if user_ids else []
    user_lookup = {u.id: u for u in users}

    summaries = []
    for uid, data in user_map.items():
        u = user_lookup.get(uid)
        if u is None:
            continue
        summaries.append(
            UserActivitySummary(
                user_id=uid,
                full_name=u.full_name,
                email=u.email,
                role=u.role.value if hasattr(u.role, "value") else str(u.role),
                total_actions=data["total_actions"],
                actions_by_type=data["actions_by_type"],
                last_active=data["last_active"],
            )
        )

    summaries.sort(key=lambda s: s.total_actions, reverse=True)

    return AdminUserActivity(
        total_active_users=len(summaries),
        users=summaries,
    )
