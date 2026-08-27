from datetime import datetime, date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.models.user import User
from app.models.approval import Approval
from app.models.activity_log import ActivityLog
from app.schemas.decision import DecisionStatus
from app.schemas.activity import ActivityResponse
from app.schemas.dashboard import (
    EmployeeDashboardResponse,
    EmployeeDecisionItem,
    ManagerDashboardResponse,
    ManagerStatisticsResponse,
    PendingApprovalItem,
    AdminDashboardResponse,
    AnalyticsResponse,
    DecisionStatsBlock,
    UserStatsBlock,
    ApprovalStatsBlock,
    ApprovalPerformanceResponse,
    CompletionRateResponse,
    ActiveUserItem,
)
from app.utils.security import get_current_user, require_role


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# ---------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------

def _status_counts(db: Session, extra_filter=None) -> dict:
    """Returns {status_value: count} for every DecisionStatus, using a
    single grouped SQL query rather than looping over rows in Python."""
    query = db.query(Decision.status, func.count(Decision.id))

    if extra_filter is not None:
        query = query.filter(extra_filter)

    query = query.group_by(Decision.status)

    counts = {s.value: 0 for s in DecisionStatus}
    for status_value, count in query.all():
        counts[status_value] = count

    return counts


def _validate_date_range(start_date: Optional[date], end_date: Optional[date]):
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date must not be after end_date"
        )


def _dept_user_ids_subquery(db: Session, department: str):
    return db.query(User.id).filter(User.department == department).subquery()


# ---------------------------------------------------------------------
# 2-5. EMPLOYEE DASHBOARD
# ---------------------------------------------------------------------

@router.get("/employee", response_model=EmployeeDashboardResponse)
def employee_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    counts = _status_counts(db, Decision.created_by == current_user.id)

    pending_reviews = (
        db.query(func.count(Approval.id))
        .filter(
            Approval.reviewer_id == current_user.id,
            Approval.status == "Pending",
        )
        .scalar()
    )

    recent = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == current_user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
        .all()
    )

    return EmployeeDashboardResponse(
        total_decisions=sum(counts.values()),
        draft_decisions=counts[DecisionStatus.DRAFT.value],
        under_review=counts[DecisionStatus.UNDER_REVIEW.value],
        approved_decisions=counts[DecisionStatus.APPROVED.value],
        rejected_decisions=counts[DecisionStatus.REJECTED.value],
        pending_reviews=pending_reviews or 0,
        recent_activities=[ActivityResponse.model_validate(a) for a in recent],
    )


@router.get("/employee/decisions", response_model=list[EmployeeDecisionItem])
def employee_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Decision)
        .filter(Decision.created_by == current_user.id)
        .order_by(Decision.created_at.desc())
        .all()
    )


@router.get("/employee/pending-reviews", response_model=list[PendingApprovalItem])
def employee_pending_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rows = (
        db.query(Approval, Decision.title)
        .join(Decision, Approval.decision_id == Decision.id)
        .filter(
            Approval.reviewer_id == current_user.id,
            Approval.status == "Pending",
        )
        .order_by(Approval.created_at.asc())
        .all()
    )

    return [
        PendingApprovalItem(
            decision_id=approval.decision_id,
            decision_title=title,
            approval_id=approval.id,
            level=approval.level,
            reviewer_id=approval.reviewer_id,
            status=approval.status,
            created_at=approval.created_at,
        )
        for approval, title in rows
    ]


@router.get("/employee/recent-activities", response_model=list[ActivityResponse])
def employee_recent_activities(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == current_user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(limit)
        .all()
    )


# ---------------------------------------------------------------------
# 6-9. MANAGER DASHBOARD
#
# NOTE: there is no manager->team relationship in the current schema
# (no manager_id / team table). "Team" here means: employees who share
# the manager's `department`. If your real notion of a team is
# different, this is the one thing you'll need to adjust once that
# relationship exists.
# ---------------------------------------------------------------------

@router.get("/manager", response_model=ManagerDashboardResponse)
def manager_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Manager", "Administrator"))
):
    dept_ids = _dept_user_ids_subquery(db, current_user.department)
    counts = _status_counts(db, Decision.created_by.in_(dept_ids))

    pending_approvals = (
        db.query(func.count(Approval.id))
        .filter(
            Approval.reviewer_id == current_user.id,
            Approval.status == "Pending",
        )
        .scalar()
    )

    return ManagerDashboardResponse(
        team_decisions=sum(counts.values()),
        pending_approvals=pending_approvals or 0,
        approved_decisions=counts[DecisionStatus.APPROVED.value],
        rejected_decisions=counts[DecisionStatus.REJECTED.value],
        under_review=counts[DecisionStatus.UNDER_REVIEW.value],
    )


@router.get("/manager/team-decisions", response_model=list[EmployeeDecisionItem])
def manager_team_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Manager", "Administrator"))
):
    dept_ids = _dept_user_ids_subquery(db, current_user.department)

    return (
        db.query(Decision)
        .filter(Decision.created_by.in_(dept_ids))
        .order_by(Decision.created_at.desc())
        .all()
    )


@router.get("/manager/pending-approvals", response_model=list[PendingApprovalItem])
def manager_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Manager", "Administrator"))
):
    rows = (
        db.query(Approval, Decision.title)
        .join(Decision, Approval.decision_id == Decision.id)
        .filter(
            Approval.reviewer_id == current_user.id,
            Approval.status == "Pending",
        )
        .order_by(Approval.created_at.asc())
        .all()
    )

    return [
        PendingApprovalItem(
            decision_id=approval.decision_id,
            decision_title=title,
            approval_id=approval.id,
            level=approval.level,
            reviewer_id=approval.reviewer_id,
            status=approval.status,
            created_at=approval.created_at,
        )
        for approval, title in rows
    ]


@router.get("/manager/statistics", response_model=ManagerStatisticsResponse)
def manager_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Manager", "Administrator"))
):
    dept_ids = _dept_user_ids_subquery(db, current_user.department)
    counts = _status_counts(db, Decision.created_by.in_(dept_ids))

    return ManagerStatisticsResponse(
        total_decisions=sum(counts.values()),
        draft_decisions=counts[DecisionStatus.DRAFT.value],
        under_review=counts[DecisionStatus.UNDER_REVIEW.value],
        approved_decisions=counts[DecisionStatus.APPROVED.value],
        rejected_decisions=counts[DecisionStatus.REJECTED.value],
        archived_decisions=counts[DecisionStatus.ARCHIVED.value],
    )


# ---------------------------------------------------------------------
# 10-15. ADMIN DASHBOARD
# ---------------------------------------------------------------------

@router.get("/admin", response_model=AdminDashboardResponse)
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Administrator"))
):
    counts = _status_counts(db)
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_approvals = db.query(func.count(Approval.id)).scalar() or 0
    pending_approvals = (
        db.query(func.count(Approval.id))
        .filter(Approval.status == "Pending")
        .scalar() or 0
    )

    recent = (
        db.query(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .limit(15)
        .all()
    )

    return AdminDashboardResponse(
        total_users=total_users,
        total_decisions=sum(counts.values()),
        total_approvals=total_approvals,
        pending_approvals=pending_approvals,
        approved_decisions=counts[DecisionStatus.APPROVED.value],
        rejected_decisions=counts[DecisionStatus.REJECTED.value],
        under_review=counts[DecisionStatus.UNDER_REVIEW.value],
        draft_decisions=counts[DecisionStatus.DRAFT.value],
        archived_decisions=counts[DecisionStatus.ARCHIVED.value],
        recent_activities=[ActivityResponse.model_validate(a) for a in recent],
    )


@router.get("/admin/analytics", response_model=AnalyticsResponse)
def admin_analytics(
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Administrator"))
):
    _validate_date_range(start_date, end_date)

    decision_filter = None
    if start_date is not None:
        decision_filter = Decision.created_at >= start_date
    if end_date is not None:
        end_bound = Decision.created_at < (end_date + timedelta(days=1))
        decision_filter = end_bound if decision_filter is None else (decision_filter & end_bound)

    counts = _status_counts(db, decision_filter)

    total_users = db.query(func.count(User.id)).scalar() or 0

    active_cutoff = datetime.utcnow() - timedelta(days=30)
    active_users = (
        db.query(func.count(func.distinct(ActivityLog.user_id)))
        .filter(ActivityLog.created_at >= active_cutoff)
        .scalar() or 0
    )

    role_rows = (
        db.query(User.role, func.count(User.id))
        .group_by(User.role)
        .all()
    )
    users_by_role = {role: count for role, count in role_rows}

    total_approvals = db.query(func.count(Approval.id)).scalar() or 0
    pending = db.query(func.count(Approval.id)).filter(Approval.status == "Pending").scalar() or 0
    approved = db.query(func.count(Approval.id)).filter(Approval.status == "Approved").scalar() or 0
    rejected = db.query(func.count(Approval.id)).filter(Approval.status == "Rejected").scalar() or 0

    return AnalyticsResponse(
        decision_stats=DecisionStatsBlock(
            total_decisions=sum(counts.values()),
            draft_decisions=counts[DecisionStatus.DRAFT.value],
            under_review=counts[DecisionStatus.UNDER_REVIEW.value],
            approved_decisions=counts[DecisionStatus.APPROVED.value],
            rejected_decisions=counts[DecisionStatus.REJECTED.value],
            archived_decisions=counts[DecisionStatus.ARCHIVED.value],
        ),
        user_stats=UserStatsBlock(
            total_users=total_users,
            active_users=active_users,
            users_by_role=users_by_role,
        ),
        approval_stats=ApprovalStatsBlock(
            total_approvals=total_approvals,
            pending_approvals=pending,
            approved_approvals=approved,
            rejected_approvals=rejected,
        ),
    )


@router.get("/admin/decision-activity")
def admin_decision_activity(
    group_by: str = Query(default="day", pattern="^(day|week|month)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Administrator"))
):
    bucket = func.date_trunc(group_by, Decision.created_at).label("bucket")

    rows = (
        db.query(bucket, func.count(Decision.id))
        .group_by(bucket)
        .order_by(bucket)
        .all()
    )

    return {row[0].date().isoformat(): row[1] for row in rows}


@router.get("/admin/approval-statistics", response_model=ApprovalPerformanceResponse)
def admin_approval_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Administrator"))
):
    turnaround_seconds = func.extract(
        "epoch", Approval.completed_at - Approval.created_at
    )

    completed_query = db.query(turnaround_seconds).filter(Approval.completed_at.isnot(None))

    avg_seconds = db.query(func.avg(turnaround_seconds)).filter(
        Approval.completed_at.isnot(None)
    ).scalar()
    min_seconds = db.query(func.min(turnaround_seconds)).filter(
        Approval.completed_at.isnot(None)
    ).scalar()
    max_seconds = db.query(func.max(turnaround_seconds)).filter(
        Approval.completed_at.isnot(None)
    ).scalar()

    pending_count = (
        db.query(func.count(Approval.id))
        .filter(Approval.status == "Pending")
        .scalar() or 0
    )

    def to_hours(seconds):
        return round(seconds / 3600, 2) if seconds is not None else None

    return ApprovalPerformanceResponse(
        average_approval_time_hours=to_hours(avg_seconds),
        fastest_approval_hours=to_hours(min_seconds),
        slowest_approval_hours=to_hours(max_seconds),
        pending_approvals=pending_count,
    )


@router.get("/admin/completion-rate", response_model=CompletionRateResponse)
def admin_completion_rate(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Administrator"))
):
    total = db.query(func.count(Approval.id)).scalar() or 0
    completed = (
        db.query(func.count(Approval.id))
        .filter(Approval.status.in_(["Approved", "Rejected"]))
        .scalar() or 0
    )

    rate = round((completed / total) * 100, 2) if total > 0 else 0.0

    return CompletionRateResponse(
        total_approvals=total,
        completed_approvals=completed,
        completion_rate=rate,
    )


@router.get("/admin/user-activity", response_model=list[ActiveUserItem])
def admin_user_activity(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Administrator"))
):
    cutoff = datetime.utcnow() - timedelta(days=days)

    rows = (
        db.query(
            ActivityLog.user_id,
            func.max(ActivityLog.created_at).label("last_activity"),
            func.count(ActivityLog.id).label("activity_count"),
        )
        .filter(ActivityLog.created_at >= cutoff)
        .group_by(ActivityLog.user_id)
        .order_by(func.max(ActivityLog.created_at).desc())
        .all()
    )

    user_ids = [row.user_id for row in rows]
    users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()}

    return [
        ActiveUserItem(
            user_id=row.user_id,
            full_name=users[row.user_id].full_name if row.user_id in users else "Unknown",
            role=users[row.user_id].role if row.user_id in users else "Unknown",
            last_activity_at=row.last_activity,
            activity_count=row.activity_count,
        )
        for row in rows
    ]
