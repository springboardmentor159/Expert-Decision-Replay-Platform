from datetime import date, datetime, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.db.database import get_db
from app.models.activity_log import ActivityLog
from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User
from app.schemas.dashboard import (
    AdminAnalyticsResponse,
    AdminDashboardResponse,
    ApprovalCompletionRateResponse,
    ApprovalStatisticsResponse,
    DecisionActivityResponse,
    EmployeeActivitySummary,
    EmployeeDashboardResponse,
    EmployeeDecisionSummary,
    EmployeePendingReview,
    ManagerDashboardResponse,
    ManagerDecisionSummary,
    ManagerPendingApproval,
    ManagerStatisticsResponse,
    UserActivityResponse,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


# ============================================================
# DATE HELPERS
# ============================================================

def validate_date_range(
    start_date: date | None,
    end_date: date | None,
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date",
        )


def apply_date_filter(
    query,
    column,
    start_date: date | None,
    end_date: date | None,
):
    """
    Apply an inclusive start-date and inclusive end-date filter.

    End date is handled as the beginning of the following day so that
    records created at any time during end_date are included.
    """

    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time())
        query = query.filter(column >= start_datetime)

    if end_date:
        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            datetime.min.time(),
        )
        query = query.filter(column < end_datetime)

    return query


# ============================================================
# EMPLOYEE DASHBOARD
# ============================================================

@router.get(
    "/employee",
    response_model=EmployeeDashboardResponse,
)
def get_employee_dashboard(
    current_user: dict = Depends(require_role("Employee")),
    db: Session = Depends(get_db),
):
    user_id = int(current_user["sub"])

    my_decisions_query = db.query(Decision).filter(
        Decision.created_by == user_id
    )

    my_decisions = my_decisions_query.count()

    draft_decisions = my_decisions_query.filter(
        Decision.status == "Draft"
    ).count()

    decisions_under_review = my_decisions_query.filter(
        Decision.status == "Under Review"
    ).count()

    approved_decisions = my_decisions_query.filter(
        Decision.status == "Approved"
    ).count()

    rejected_decisions = my_decisions_query.filter(
        Decision.status == "Rejected"
    ).count()

    # Pending reviews assigned TO this employee.
    pending_reviews = db.query(Approval).filter(
        Approval.assigned_to == user_id,
        Approval.status == "Pending",
    ).count()

    recent_activities = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == user_id)
        .order_by(ActivityLog.created_at.desc())
        .limit(5)
        .all()
    )

    return EmployeeDashboardResponse(
        my_decisions=my_decisions,
        draft_decisions=draft_decisions,
        decisions_under_review=decisions_under_review,
        approved_decisions=approved_decisions,
        rejected_decisions=rejected_decisions,
        pending_reviews=pending_reviews,
        recent_activities=recent_activities,
    )


# ============================================================
# EMPLOYEE DECISIONS
# ============================================================

@router.get(
    "/employee/decisions",
    response_model=list[EmployeeDecisionSummary],
)
def get_employee_decisions(
    current_user: dict = Depends(require_role("Employee")),
    db: Session = Depends(get_db),
):
    user_id = int(current_user["sub"])

    return (
        db.query(Decision)
        .filter(Decision.created_by == user_id)
        .order_by(Decision.created_at.desc())
        .all()
    )


# ============================================================
# EMPLOYEE RECENT ACTIVITIES
# ============================================================

@router.get(
    "/employee/recent-activities",
    response_model=list[EmployeeActivitySummary],
)
def get_employee_recent_activities(
    current_user: dict = Depends(require_role("Employee")),
    db: Session = Depends(get_db),
):
    user_id = int(current_user["sub"])

    return (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == user_id)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
        .all()
    )


# ============================================================
# EMPLOYEE PENDING REVIEWS
# ============================================================

@router.get(
    "/employee/pending-reviews",
    response_model=list[EmployeePendingReview],
)
def get_employee_pending_reviews(
    current_user: dict = Depends(require_role("Employee")),
    db: Session = Depends(get_db),
):
    user_id = int(current_user["sub"])

    results = (
        db.query(
            Approval.id,
            Approval.decision_id,
            Decision.title.label("decision_title"),
            Approval.approval_level,
            Approval.status,
            Approval.created_at,
        )
        .join(
            Decision,
            Approval.decision_id == Decision.id,
        )
        .filter(
            Approval.assigned_to == user_id,
            Approval.status == "Pending",
        )
        .order_by(Approval.created_at.desc())
        .all()
    )

    return results


# ============================================================
# MANAGER DASHBOARD
# ============================================================

@router.get(
    "/manager",
    response_model=ManagerDashboardResponse,
)
def get_manager_dashboard(
    current_user: dict = Depends(require_role("Manager")),
    db: Session = Depends(get_db),
):
    manager_id = int(current_user["sub"])

    manager = (
        db.query(User)
        .filter(User.id == manager_id)
        .first()
    )

    if not manager:
        raise HTTPException(
            status_code=404,
            detail="Manager not found",
        )

    department = manager.department

    team_decisions_query = (
        db.query(Decision)
        .join(User, Decision.created_by == User.id)
        .filter(User.department == department)
    )

    team_decisions = team_decisions_query.count()

    pending_approvals = (
        db.query(Approval)
        .join(Decision, Approval.decision_id == Decision.id)
        .join(User, Decision.created_by == User.id)
        .filter(
            User.department == department,
            Approval.status == "Pending",
        )
        .count()
    )

    approved_decisions = (
        team_decisions_query
        .filter(Decision.status == "Approved")
        .count()
    )

    rejected_decisions = (
        team_decisions_query
        .filter(Decision.status == "Rejected")
        .count()
    )

    under_review = (
        team_decisions_query
        .filter(Decision.status == "Under Review")
        .count()
    )

    recent_team_activities = (
        db.query(ActivityLog)
        .join(User, ActivityLog.user_id == User.id)
        .filter(User.department == department)
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
        recent_team_activities=recent_team_activities,
    )


# ============================================================
# MANAGER TEAM DECISIONS
# ============================================================

@router.get(
    "/manager/team-decisions",
    response_model=list[ManagerDecisionSummary],
)
def get_manager_team_decisions(
    current_user: dict = Depends(require_role("Manager")),
    db: Session = Depends(get_db),
):
    manager_id = int(current_user["sub"])

    manager = (
        db.query(User)
        .filter(User.id == manager_id)
        .first()
    )

    if not manager:
        raise HTTPException(
            status_code=404,
            detail="Manager not found",
        )

    return (
        db.query(Decision)
        .join(User, Decision.created_by == User.id)
        .filter(User.department == manager.department)
        .order_by(Decision.created_at.desc())
        .all()
    )


# ============================================================
# MANAGER PENDING APPROVALS
# ============================================================

@router.get(
    "/manager/pending-approvals",
    response_model=list[ManagerPendingApproval],
)
def get_manager_pending_approvals(
    current_user: dict = Depends(require_role("Manager")),
    db: Session = Depends(get_db),
):
    manager_id = int(current_user["sub"])

    manager = (
        db.query(User)
        .filter(User.id == manager_id)
        .first()
    )

    if not manager:
        raise HTTPException(
            status_code=404,
            detail="Manager not found",
        )

    results = (
        db.query(
            Approval.id,
            Approval.decision_id,
            Decision.title.label("decision_title"),
            Approval.approval_level,
            Approval.assigned_to,
            Approval.status,
            Approval.created_at,
        )
        .join(
            Decision,
            Approval.decision_id == Decision.id,
        )
        .join(
            User,
            Decision.created_by == User.id,
        )
        .filter(
            User.department == manager.department,
            Approval.status == "Pending",
        )
        .order_by(Approval.created_at.desc())
        .all()
    )

    return results


# ============================================================
# MANAGER STATISTICS
# ============================================================

@router.get(
    "/manager/statistics",
    response_model=ManagerStatisticsResponse,
)
def get_manager_statistics(
    current_user: dict = Depends(require_role("Manager")),
    db: Session = Depends(get_db),
):
    manager_id = int(current_user["sub"])

    manager = (
        db.query(User)
        .filter(User.id == manager_id)
        .first()
    )

    if not manager:
        raise HTTPException(
            status_code=404,
            detail="Manager not found",
        )

    team_decisions_query = (
        db.query(Decision)
        .join(User, Decision.created_by == User.id)
        .filter(User.department == manager.department)
    )

    return ManagerStatisticsResponse(
        total_decisions=team_decisions_query.count(),
        draft_decisions=team_decisions_query.filter(
            Decision.status == "Draft"
        ).count(),
        under_review=team_decisions_query.filter(
            Decision.status == "Under Review"
        ).count(),
        approved_decisions=team_decisions_query.filter(
            Decision.status == "Approved"
        ).count(),
        rejected_decisions=team_decisions_query.filter(
            Decision.status == "Rejected"
        ).count(),
        archived_decisions=team_decisions_query.filter(
            Decision.status == "Archived"
        ).count(),
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@router.get(
    "/admin",
    response_model=AdminDashboardResponse,
)
def get_admin_dashboard(
    current_user: dict = Depends(require_role("Administrator")),
    db: Session = Depends(get_db),
):
    total_users = db.query(User).count()
    total_decisions = db.query(Decision).count()

    pending_approvals = (
        db.query(Approval)
        .filter(Approval.status == "Pending")
        .count()
    )

    approved_decisions = (
        db.query(Decision)
        .filter(Decision.status == "Approved")
        .count()
    )

    rejected_decisions = (
        db.query(Decision)
        .filter(Decision.status == "Rejected")
        .count()
    )

    under_review_decisions = (
        db.query(Decision)
        .filter(Decision.status == "Under Review")
        .count()
    )

    draft_decisions = (
        db.query(Decision)
        .filter(Decision.status == "Draft")
        .count()
    )

    archived_decisions = (
        db.query(Decision)
        .filter(Decision.status == "Archived")
        .count()
    )

    recent_system_activities = (
        db.query(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
        .all()
    )

    return AdminDashboardResponse(
        total_users=total_users,
        total_decisions=total_decisions,
        pending_approvals=pending_approvals,
        approved_decisions=approved_decisions,
        rejected_decisions=rejected_decisions,
        under_review_decisions=under_review_decisions,
        draft_decisions=draft_decisions,
        archived_decisions=archived_decisions,
        recent_system_activities=recent_system_activities,
    )


# ============================================================
# ADMIN ANALYTICS
# ============================================================

@router.get(
    "/admin/analytics",
    response_model=AdminAnalyticsResponse,
)
def get_admin_analytics(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    current_user: dict = Depends(require_role("Administrator")),
    db: Session = Depends(get_db),
):
    validate_date_range(start_date, end_date)

    decision_query = db.query(Decision)

    decision_query = apply_date_filter(
        decision_query,
        Decision.created_at,
        start_date,
        end_date,
    )

    total_decisions = decision_query.count()

    draft_decisions = decision_query.filter(
        Decision.status == "Draft"
    ).count()

    under_review_decisions = decision_query.filter(
        Decision.status == "Under Review"
    ).count()

    approved_decisions = decision_query.filter(
        Decision.status == "Approved"
    ).count()

    rejected_decisions = decision_query.filter(
        Decision.status == "Rejected"
    ).count()

    archived_decisions = decision_query.filter(
        Decision.status == "Archived"
    ).count()

    total_users = db.query(User).count()

    users_by_role_rows = (
        db.query(
            User.role,
            func.count(User.id),
        )
        .group_by(User.role)
        .all()
    )

    users_by_role = {
        role: count
        for role, count in users_by_role_rows
    }

    approval_query = db.query(Approval)

    approval_query = apply_date_filter(
        approval_query,
        Approval.created_at,
        start_date,
        end_date,
    )

    total_approvals = approval_query.count()

    pending_approvals = approval_query.filter(
        Approval.status == "Pending"
    ).count()

    completed_approvals = approval_query.filter(
        Approval.completed_at.isnot(None)
    ).count()

    return AdminAnalyticsResponse(
        total_decisions=total_decisions,
        draft_decisions=draft_decisions,
        under_review_decisions=under_review_decisions,
        approved_decisions=approved_decisions,
        rejected_decisions=rejected_decisions,
        archived_decisions=archived_decisions,
        total_users=total_users,
        users_by_role=users_by_role,
        total_approvals=total_approvals,
        pending_approvals=pending_approvals,
        completed_approvals=completed_approvals,
    )


# ============================================================
# ADMIN DECISION ACTIVITY
# ============================================================

@router.get(
    "/admin/decision-activity",
    response_model=list[DecisionActivityResponse],
)
def get_decision_activity(
    group_by: Literal["day", "week", "month"] = Query("day"),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    current_user: dict = Depends(require_role("Administrator")),
    db: Session = Depends(get_db),
):
    validate_date_range(start_date, end_date)

    query = db.query(
        func.date_trunc(
            group_by,
            Decision.created_at,
        ).label("period"),
        func.count(Decision.id).label("count"),
    )

    query = apply_date_filter(
        query,
        Decision.created_at,
        start_date,
        end_date,
    )

    rows = (
        query
        .group_by("period")
        .order_by("period")
        .all()
    )

    return [
        DecisionActivityResponse(
            period=period.isoformat(),
            count=count,
        )
        for period, count in rows
    ]


# ============================================================
# ADMIN APPROVAL STATISTICS
# ============================================================

@router.get(
    "/admin/approval-statistics",
    response_model=ApprovalStatisticsResponse,
)
def get_approval_statistics(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    current_user: dict = Depends(require_role("Administrator")),
    db: Session = Depends(get_db),
):
    validate_date_range(start_date, end_date)

    approval_query = db.query(Approval)

    approval_query = apply_date_filter(
        approval_query,
        Approval.created_at,
        start_date,
        end_date,
    )

    completed_query = approval_query.filter(
        Approval.completed_at.isnot(None)
    )

    duration_expression = (
        func.extract(
            "epoch",
            Approval.completed_at - Approval.created_at,
        ) / 3600.0
    )

    statistics = (
        completed_query
        .with_entities(
            func.avg(duration_expression),
            func.min(duration_expression),
            func.max(duration_expression),
        )
        .first()
    )

    average_time = float(statistics[0]) if statistics[0] is not None else 0.0
    fastest_time = float(statistics[1]) if statistics[1] is not None else None
    slowest_time = float(statistics[2]) if statistics[2] is not None else None

    pending_approvals = approval_query.filter(
        Approval.status == "Pending"
    ).count()

    return ApprovalStatisticsResponse(
        average_approval_time_hours=round(average_time, 2),
        fastest_approval_time_hours=(
            round(fastest_time, 2)
            if fastest_time is not None
            else None
        ),
        slowest_approval_time_hours=(
            round(slowest_time, 2)
            if slowest_time is not None
            else None
        ),
        pending_approvals=pending_approvals,
    )


# ============================================================
# ADMIN APPROVAL COMPLETION RATE
# ============================================================

@router.get(
    "/admin/approval-completion-rate",
    response_model=ApprovalCompletionRateResponse,
)
def get_approval_completion_rate(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    current_user: dict = Depends(require_role("Administrator")),
    db: Session = Depends(get_db),
):
    validate_date_range(start_date, end_date)

    approval_query = db.query(Approval)

    approval_query = apply_date_filter(
        approval_query,
        Approval.created_at,
        start_date,
        end_date,
    )

    total_approvals = approval_query.count()

    completed_approvals = approval_query.filter(
        Approval.completed_at.isnot(None)
    ).count()

    completion_rate = (
        (completed_approvals / total_approvals) * 100
        if total_approvals > 0
        else 0.0
    )

    return ApprovalCompletionRateResponse(
        total_approvals=total_approvals,
        completed_approvals=completed_approvals,
        completion_rate=round(completion_rate, 2),
    )


# ============================================================
# ADMIN USER ACTIVITY
# ============================================================

@router.get(
    "/admin/user-activity",
    response_model=list[UserActivityResponse],
)
def get_user_activity(
    user_id: int | None = Query(None),
    action: str | None = Query(None),
    entity_type: str | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(require_role("Administrator")),
    db: Session = Depends(get_db),
):
    validate_date_range(start_date, end_date)

    if user_id is not None:
        user_exists = (
            db.query(User.id)
            .filter(User.id == user_id)
            .first()
        )

        if not user_exists:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

    query = (
        db.query(
            ActivityLog.user_id.label("user_id"),
            User.full_name.label("user_name"),
            ActivityLog.action,
            ActivityLog.entity_type,
            ActivityLog.entity_id,
            ActivityLog.description,
            ActivityLog.created_at,
        )
        .join(
            User,
            ActivityLog.user_id == User.id,
        )
    )

    if user_id is not None:
        query = query.filter(
            ActivityLog.user_id == user_id
        )

    if action:
        query = query.filter(
            ActivityLog.action == action
        )

    if entity_type:
        query = query.filter(
            ActivityLog.entity_type == entity_type
        )

    query = apply_date_filter(
        query,
        ActivityLog.created_at,
        start_date,
        end_date,
    )

    offset = (page - 1) * page_size

    return (
        query
        .order_by(ActivityLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )