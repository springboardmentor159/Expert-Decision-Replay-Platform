from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Date, case, func
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.activity_log import ActivityLog
from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User
from app.schemas.activity import ActivityLogResponse
from app.schemas.approval import ApprovalResponse
from app.schemas.dashboard import (
    ActiveUserItem,
    AdminDashboardResponse,
    ApprovalStatisticsResponse,
    ApprovalStats,
    DecisionStats,
    EmployeeDashboardResponse,
    ManagerDashboardResponse,
    ManagerStatisticsResponse,
    SystemAnalyticsResponse,
    UserActivityResponse,
    UserStats,
)
from app.schemas.decision import DecisionResponse

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboards & Analytics"]
)


def _parse_date(date_str: Optional[str], param_name: str) -> Optional[datetime]:
    if not date_str or not date_str.strip():
        return None
    cleaned = date_str.strip()
    try:
        return datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
    except ValueError:
        try:
            return datetime.strptime(cleaned, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid date format for '{param_name}': '{date_str}'. Expected YYYY-MM-DD"
            )


def _validate_date_range(start_date: Optional[str], end_date: Optional[str]):
    start_dt = _parse_date(start_date, "start_date")
    end_dt = _parse_date(end_date, "end_date")
    if start_dt and end_dt and start_dt > end_dt:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )
    return start_dt, end_dt


def _format_activity(act: ActivityLog) -> ActivityLogResponse:
    return ActivityLogResponse(
        id=act.id,
        user_id=act.user_id,
        user_name=act.user.full_name if act.user else None,
        action=act.action,
        entity_type=act.entity_type,
        entity_id=act.entity_id,
        description=act.description,
        created_at=act.created_at
    )


def _format_approval(apprv: Approval) -> ApprovalResponse:
    return ApprovalResponse(
        id=apprv.id,
        decision_id=apprv.decision_id,
        reviewer_id=apprv.reviewer_id,
        approval_level=apprv.approval_level,
        status=apprv.status,
        comments=apprv.comments,
        created_at=apprv.created_at,
        completed_at=apprv.completed_at,
        decision_title=apprv.decision.title if apprv.decision else None,
        reviewer_name=apprv.reviewer.full_name if apprv.reviewer else None
    )


# ==========================================
# 1. EMPLOYEE DASHBOARD
# ==========================================

@router.get(
    "/employee",
    response_model=EmployeeDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Employee Dashboard overview"
)
def get_employee_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stats = db.query(
        func.count(Decision.id).label("total"),
        func.count(case((Decision.status == "Draft", 1))).label("draft"),
        func.count(case((Decision.status == "Under Review", 1))).label("under_review"),
        func.count(case((Decision.status == "Approved", 1))).label("approved"),
        func.count(case((Decision.status == "Rejected", 1))).label("rejected"),
        func.count(case((Decision.status == "Archived", 1))).label("archived")
    ).filter(Decision.created_by == current_user.id).one()

    pending_reviews_count = db.query(func.count(Approval.id)).filter(
        Approval.reviewer_id == current_user.id,
        Approval.status == "Pending"
    ).scalar() or 0

    recent_acts = db.query(ActivityLog).filter(
        ActivityLog.user_id == current_user.id
    ).order_by(ActivityLog.created_at.desc()).limit(10).all()

    return EmployeeDashboardResponse(
        total_decisions=stats.total or 0,
        draft_decisions=stats.draft or 0,
        under_review=stats.under_review or 0,
        approved_decisions=stats.approved or 0,
        rejected_decisions=stats.rejected or 0,
        archived_decisions=stats.archived or 0,
        pending_reviews=pending_reviews_count,
        recent_activities=[_format_activity(a) for a in recent_acts]
    )


@router.get(
    "/employee/decisions",
    response_model=List[DecisionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get decisions created by the current employee"
)
def get_employee_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Decision).filter(Decision.created_by == current_user.id).order_by(Decision.created_at.desc()).all()


@router.get(
    "/employee/pending-reviews",
    response_model=List[ApprovalResponse],
    status_code=status.HTTP_200_OK,
    summary="Get pending review tasks assigned to the employee"
)
def get_employee_pending_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    approvals = db.query(Approval).filter(
        Approval.reviewer_id == current_user.id,
        Approval.status == "Pending"
    ).order_by(Approval.created_at.desc()).all()

    return [_format_approval(a) for a in approvals]


@router.get(
    "/employee/recent-activities",
    response_model=List[ActivityLogResponse],
    status_code=status.HTTP_200_OK,
    summary="Get recent activities performed by the employee"
)
def get_employee_recent_activities(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    acts = db.query(ActivityLog).filter(
        ActivityLog.user_id == current_user.id
    ).order_by(ActivityLog.created_at.desc()).limit(limit).all()

    return [_format_activity(a) for a in acts]


# ==========================================
# 2. MANAGER DASHBOARD
# ==========================================

def _ensure_manager(user: User):
    if user.role not in ["Manager", "Administrator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Manager or Administrator privileges required"
        )


def _get_team_user_ids(db: Session, manager: User) -> List[int]:
    """Retrieve user IDs belonging to the manager's team/department"""
    if manager.department:
        team_users = db.query(User.id).filter(User.department == manager.department).all()
        return [u.id for u in team_users]
    return [manager.id]


@router.get(
    "/manager",
    response_model=ManagerDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Manager Dashboard overview"
)
def get_manager_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _ensure_manager(current_user)
    team_ids = _get_team_user_ids(db, current_user)

    stats = db.query(
        func.count(Decision.id).label("total"),
        func.count(case((Decision.status == "Draft", 1))).label("draft"),
        func.count(case((Decision.status == "Under Review", 1))).label("under_review"),
        func.count(case((Decision.status == "Approved", 1))).label("approved"),
        func.count(case((Decision.status == "Rejected", 1))).label("rejected"),
        func.count(case((Decision.status == "Archived", 1))).label("archived")
    ).filter(Decision.created_by.in_(team_ids)).one()

    # Pending approvals for team decisions or assigned to manager
    pending_approvals = db.query(func.count(Approval.id)).join(Decision).filter(
        Approval.status == "Pending",
        (Decision.created_by.in_(team_ids)) | (Approval.reviewer_id == current_user.id)
    ).scalar() or 0

    recent_acts = db.query(ActivityLog).filter(
        ActivityLog.user_id.in_(team_ids)
    ).order_by(ActivityLog.created_at.desc()).limit(15).all()

    return ManagerDashboardResponse(
        team_decisions=stats.total or 0,
        pending_approvals=pending_approvals,
        approved_decisions=stats.approved or 0,
        rejected_decisions=stats.rejected or 0,
        under_review=stats.under_review or 0,
        draft_decisions=stats.draft or 0,
        archived_decisions=stats.archived or 0,
        team_members_count=len(team_ids),
        recent_activities=[_format_activity(a) for a in recent_acts]
    )


@router.get(
    "/manager/team-decisions",
    response_model=List[DecisionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get decisions created by the manager's team"
)
def get_manager_team_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _ensure_manager(current_user)
    team_ids = _get_team_user_ids(db, current_user)
    return db.query(Decision).filter(Decision.created_by.in_(team_ids)).order_by(Decision.created_at.desc()).all()


@router.get(
    "/manager/pending-approvals",
    response_model=List[ApprovalResponse],
    status_code=status.HTTP_200_OK,
    summary="Get pending approvals for manager's team"
)
def get_manager_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _ensure_manager(current_user)
    team_ids = _get_team_user_ids(db, current_user)

    approvals = db.query(Approval).join(Decision).filter(
        Approval.status == "Pending",
        (Decision.created_by.in_(team_ids)) | (Approval.reviewer_id == current_user.id)
    ).order_by(Approval.created_at.desc()).all()

    return [_format_approval(a) for a in approvals]


@router.get(
    "/manager/statistics",
    response_model=ManagerStatisticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get manager team decision statistics"
)
def get_manager_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _ensure_manager(current_user)
    team_ids = _get_team_user_ids(db, current_user)

    stats = db.query(
        func.count(Decision.id).label("total"),
        func.count(case((Decision.status == "Draft", 1))).label("draft"),
        func.count(case((Decision.status == "Under Review", 1))).label("under_review"),
        func.count(case((Decision.status == "Approved", 1))).label("approved"),
        func.count(case((Decision.status == "Rejected", 1))).label("rejected"),
        func.count(case((Decision.status == "Archived", 1))).label("archived")
    ).filter(Decision.created_by.in_(team_ids)).one()

    return ManagerStatisticsResponse(
        total_decisions=stats.total or 0,
        draft_decisions=stats.draft or 0,
        under_review=stats.under_review or 0,
        approved_decisions=stats.approved or 0,
        rejected_decisions=stats.rejected or 0,
        archived_decisions=stats.archived or 0
    )


# ==========================================
# 3. ADMIN DASHBOARD & ANALYTICS
# ==========================================

def _ensure_admin(user: User):
    if user.role != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Administrator privileges required"
        )


@router.get(
    "/admin",
    response_model=AdminDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Admin Dashboard overview"
)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _ensure_admin(current_user)

    total_users = db.query(func.count(User.id)).scalar() or 0

    dec_stats = db.query(
        func.count(Decision.id).label("total"),
        func.count(case((Decision.status == "Draft", 1))).label("draft"),
        func.count(case((Decision.status == "Under Review", 1))).label("under_review"),
        func.count(case((Decision.status == "Approved", 1))).label("approved"),
        func.count(case((Decision.status == "Rejected", 1))).label("rejected"),
        func.count(case((Decision.status == "Archived", 1))).label("archived")
    ).one()

    apprv_stats = db.query(
        func.count(Approval.id).label("total"),
        func.count(case((Approval.status == "Pending", 1))).label("pending")
    ).one()

    recent_acts = db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(20).all()

    return AdminDashboardResponse(
        total_users=total_users,
        total_decisions=dec_stats.total or 0,
        total_approvals=apprv_stats.total or 0,
        pending_approvals=apprv_stats.pending or 0,
        approved_decisions=dec_stats.approved or 0,
        rejected_decisions=dec_stats.rejected or 0,
        under_review=dec_stats.under_review or 0,
        draft_decisions=dec_stats.draft or 0,
        archived_decisions=dec_stats.archived or 0,
        recent_activities=[_format_activity(a) for a in recent_acts]
    )


@router.get(
    "/admin/analytics",
    response_model=SystemAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get organization-wide analytics with optional date range filter"
)
def get_admin_analytics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _ensure_admin(current_user)
    start_dt, end_dt = _validate_date_range(start_date, end_date)

    # 1. Decisions Analytics
    dec_query = db.query(
        func.count(Decision.id).label("total"),
        func.count(case((Decision.status == "Draft", 1))).label("draft"),
        func.count(case((Decision.status == "Under Review", 1))).label("under_review"),
        func.count(case((Decision.status == "Approved", 1))).label("approved"),
        func.count(case((Decision.status == "Rejected", 1))).label("rejected"),
        func.count(case((Decision.status == "Archived", 1))).label("archived")
    )
    if start_dt:
        dec_query = dec_query.filter(Decision.created_at >= start_dt)
    if end_dt:
        dec_query = dec_query.filter(Decision.created_at <= end_dt)
    dec_stats = dec_query.one()

    # 2. Users Analytics
    total_users = db.query(func.count(User.id)).scalar() or 0
    role_counts = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    users_by_role = {role: count for role, count in role_counts}

    active_user_query = db.query(func.count(func.distinct(ActivityLog.user_id)))
    if start_dt:
        active_user_query = active_user_query.filter(ActivityLog.created_at >= start_dt)
    if end_dt:
        active_user_query = active_user_query.filter(ActivityLog.created_at <= end_dt)
    active_users = active_user_query.scalar() or 0

    # 3. Approvals Analytics
    apprv_query = db.query(
        func.count(Approval.id).label("total"),
        func.count(case((Approval.status == "Pending", 1))).label("pending"),
        func.count(case((Approval.status == "Approved", 1))).label("approved"),
        func.count(case((Approval.status == "Rejected", 1))).label("rejected")
    )
    if start_dt:
        apprv_query = apprv_query.filter(Approval.created_at >= start_dt)
    if end_dt:
        apprv_query = apprv_query.filter(Approval.created_at <= end_dt)
    apprv_stats = apprv_query.one()

    return SystemAnalyticsResponse(
        decision_statistics=DecisionStats(
            total_decisions=dec_stats.total or 0,
            draft_decisions=dec_stats.draft or 0,
            under_review=dec_stats.under_review or 0,
            approved_decisions=dec_stats.approved or 0,
            rejected_decisions=dec_stats.rejected or 0,
            archived_decisions=dec_stats.archived or 0
        ),
        user_statistics=UserStats(
            total_users=total_users,
            active_users=active_users,
            users_by_role=users_by_role
        ),
        approval_statistics=ApprovalStats(
            total_approvals=apprv_stats.total or 0,
            pending_approvals=apprv_stats.pending or 0,
            approved_approvals=apprv_stats.approved or 0,
            rejected_approvals=apprv_stats.rejected or 0
        )
    )


@router.get(
    "/admin/decision-activity",
    response_model=Dict[str, int],
    status_code=status.HTTP_200_OK,
    summary="Get decision creation activity grouped by day using SQL aggregation"
)
def get_admin_decision_activity(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _ensure_admin(current_user)
    start_dt, end_dt = _validate_date_range(start_date, end_date)

    date_col = func.cast(Decision.created_at, Date)
    query = db.query(date_col.label("day"), func.count(Decision.id).label("count"))

    if start_dt:
        query = query.filter(Decision.created_at >= start_dt)
    if end_dt:
        query = query.filter(Decision.created_at <= end_dt)

    results = query.group_by(date_col).order_by(date_col.asc()).all()
    return {str(r.day): r.count for r in results if r.day}


@router.get(
    "/admin/approval-statistics",
    response_model=ApprovalStatisticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get approval performance metrics including turnaround times and completion rate"
)
def get_admin_approval_statistics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _ensure_admin(current_user)
    start_dt, end_dt = _validate_date_range(start_date, end_date)

    query = db.query(Approval)
    if start_dt:
        query = query.filter(Approval.created_at >= start_dt)
    if end_dt:
        query = query.filter(Approval.created_at <= end_dt)

    all_approvals = query.all()
    total = len(all_approvals)
    completed_list = [a for a in all_approvals if a.completed_at is not None]
    completed_count = len(completed_list)
    pending_count = len([a for a in all_approvals if a.status == "Pending"])
    approved_count = len([a for a in all_approvals if a.status == "Approved"])
    rejected_count = len([a for a in all_approvals if a.status == "Rejected"])

    completion_rate = round((completed_count / total * 100.0), 2) if total > 0 else 0.0

    # Calculate turnaround durations in hours
    durations = [
        (a.completed_at - a.created_at).total_seconds() / 3600.0
        for a in completed_list
        if a.completed_at >= a.created_at
    ]

    avg_time = round(sum(durations) / len(durations), 2) if durations else None
    fastest = round(min(durations), 2) if durations else None
    slowest = round(max(durations), 2) if durations else None

    return ApprovalStatisticsResponse(
        total_approvals=total,
        completed_approvals=completed_count,
        pending_approvals=pending_count,
        approved_count=approved_count,
        rejected_count=rejected_count,
        completion_rate=completion_rate,
        average_approval_time_hours=avg_time,
        fastest_approval_hours=fastest,
        slowest_approval_hours=slowest
    )


@router.get(
    "/admin/user-activity",
    response_model=UserActivityResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user activity report and recent active users"
)
def get_admin_user_activity(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _ensure_admin(current_user)
    start_dt, end_dt = _validate_date_range(start_date, end_date)

    query = db.query(
        User.id,
        User.full_name,
        User.email,
        User.role,
        func.max(ActivityLog.created_at).label("last_active"),
        func.count(ActivityLog.id).label("action_count")
    ).outerjoin(ActivityLog, User.id == ActivityLog.user_id)

    if start_dt:
        query = query.filter((ActivityLog.created_at >= start_dt) | (ActivityLog.id == None))
    if end_dt:
        query = query.filter((ActivityLog.created_at <= end_dt) | (ActivityLog.id == None))

    user_rows = query.group_by(User.id, User.full_name, User.email, User.role).order_by(func.max(ActivityLog.created_at).desc().nullslast()).all()

    active_items = []
    active_count = 0
    for u in user_rows:
        if u.action_count and u.action_count > 0:
            active_count += 1
        active_items.append(
            ActiveUserItem(
                id=u.id,
                full_name=u.full_name,
                email=u.email,
                role=u.role,
                last_active=u.last_active,
                action_count=u.action_count or 0
            )
        )

    return UserActivityResponse(
        active_users_count=active_count,
        active_users=active_items
    )
