from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.security import get_current_user
from app.db.database import get_db

from app.models.decision import Decision
from app.models.decision_status import DecisionStatus
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.models.approval import Approval
from app.models.approval_status import ApprovalStatus
from app.models.role import UserRole


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


def ensure_employee(current_user: User) -> None:
    if current_user.role != UserRole.EMPLOYEE:
        raise HTTPException(
            status_code=403,
            detail="Only employees can access this dashboard"
        )


# ============================================================
# EMPLOYEE DASHBOARD
# ============================================================

@router.get("/employee")
def employee_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ensure_employee(current_user)

    total_decisions = db.query(Decision).filter(
        Decision.created_by == current_user.id
    ).count()

    draft_decisions = db.query(Decision).filter(
        Decision.created_by == current_user.id,
        Decision.status == DecisionStatus.DRAFT
    ).count()

    under_review_decisions = db.query(Decision).filter(
        Decision.created_by == current_user.id,
        Decision.status == DecisionStatus.UNDER_REVIEW
    ).count()

    approved_decisions = db.query(Decision).filter(
        Decision.created_by == current_user.id,
        Decision.status == DecisionStatus.APPROVED
    ).count()

    rejected_decisions = db.query(Decision).filter(
        Decision.created_by == current_user.id,
        Decision.status == DecisionStatus.REJECTED
    ).count()

    pending_reviews = db.query(Approval).filter(
        Approval.reviewer_id == current_user.id,
        Approval.status == ApprovalStatus.PENDING
    ).count()

    recent_activities = db.query(ActivityLog).filter(
        ActivityLog.user_id == current_user.id
    ).order_by(
        ActivityLog.created_at.desc()
    ).limit(10).all()

    return {
        "my_decisions": {
            "total": total_decisions,
            "draft": draft_decisions,
            "under_review": under_review_decisions,
            "approved": approved_decisions,
            "rejected": rejected_decisions
        },
        "pending_reviews": pending_reviews,
        "recent_activities": [
            {
                "id": activity.id,
                "action": activity.action,
                "entity_type": activity.entity_type,
                "entity_id": activity.entity_id,
                "description": activity.description,
                "created_at": activity.created_at
            }
            for activity in recent_activities
        ]
    }


# ============================================================
# EMPLOYEE DECISIONS
# ============================================================

@router.get("/employee/decisions")
def employee_decisions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ensure_employee(current_user)

    decisions = db.query(Decision).filter(
        Decision.created_by == current_user.id
    ).order_by(
        Decision.created_at.desc()
    ).all()

    return [
        {
            "id": decision.id,
            "title": decision.title,
            "problem_statement": decision.problem_statement,
            "category": decision.category,
            "status": decision.status.value,
            "created_at": decision.created_at,
            "updated_at": decision.updated_at
        }
        for decision in decisions
    ]


# ============================================================
# EMPLOYEE PENDING REVIEWS
# ============================================================

@router.get("/employee/pending-reviews")
def employee_pending_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ensure_employee(current_user)

    approvals = db.query(Approval).filter(
        Approval.reviewer_id == current_user.id,
        Approval.status == ApprovalStatus.PENDING
    ).order_by(
        Approval.created_at.desc()
    ).all()

    return [
        {
            "approval_id": approval.id,
            "decision_id": approval.decision_id,
            "approval_level": approval.approval_level,
            "status": approval.status.value,
            "created_at": approval.created_at
        }
        for approval in approvals
    ]


# ============================================================
# EMPLOYEE RECENT ACTIVITIES
# ============================================================

@router.get("/employee/recent-activities")
def employee_recent_activities(
    limit: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ensure_employee(current_user)

    activities = db.query(ActivityLog).filter(
        ActivityLog.user_id == current_user.id
    ).order_by(
        ActivityLog.created_at.desc()
    ).limit(limit).all()

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


# ============================================================
# MANAGER DASHBOARD
# ============================================================

@router.get("/manager")
def manager_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=403,
            detail="Only managers can access this dashboard"
        )

    team_decisions_query = db.query(Decision).join(
        User,
        Decision.created_by == User.id
    ).filter(
        User.department == current_user.department
    )

    total_decisions = team_decisions_query.count()

    pending_approvals = db.query(Approval).join(
        Decision,
        Approval.decision_id == Decision.id
    ).join(
        User,
        Decision.created_by == User.id
    ).filter(
        User.department == current_user.department,
        Approval.status == ApprovalStatus.PENDING
    ).count()

    approved_decisions = team_decisions_query.filter(
        Decision.status == DecisionStatus.APPROVED
    ).count()

    rejected_decisions = team_decisions_query.filter(
        Decision.status == DecisionStatus.REJECTED
    ).count()

    under_review_decisions = team_decisions_query.filter(
        Decision.status == DecisionStatus.UNDER_REVIEW
    ).count()

    return {
        "team": {
            "department": current_user.department
        },
        "statistics": {
            "total_decisions": total_decisions,
            "pending_approvals": pending_approvals,
            "approved": approved_decisions,
            "rejected": rejected_decisions,
            "under_review": under_review_decisions
        }
    }


# ============================================================
# MANAGER TEAM DECISIONS
# ============================================================

@router.get("/manager/team-decisions")
def manager_team_decisions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=403,
            detail="Only managers can access team decisions"
        )

    decisions = db.query(Decision).join(
        User,
        Decision.created_by == User.id
    ).filter(
        User.department == current_user.department
    ).order_by(
        Decision.created_at.desc()
    ).all()

    return [
        {
            "id": decision.id,
            "title": decision.title,
            "problem_statement": decision.problem_statement,
            "category": decision.category,
            "status": decision.status.value,
            "created_by": decision.created_by,
            "created_at": decision.created_at,
            "updated_at": decision.updated_at
        }
        for decision in decisions
    ]


# ============================================================
# MANAGER PENDING APPROVALS
# ============================================================

@router.get("/manager/pending-approvals")
def manager_pending_approvals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=403,
            detail="Only managers can access pending approvals"
        )

    approvals = db.query(Approval).join(
        Decision,
        Approval.decision_id == Decision.id
    ).join(
        User,
        Decision.created_by == User.id
    ).filter(
        User.department == current_user.department,
        Approval.status == ApprovalStatus.PENDING
    ).order_by(
        Approval.created_at.desc()
    ).all()

    return [
        {
            "approval_id": approval.id,
            "decision_id": approval.decision_id,
            "reviewer_id": approval.reviewer_id,
            "approval_level": approval.approval_level,
            "status": approval.status.value,
            "created_at": approval.created_at
        }
        for approval in approvals
    ]


# ============================================================
# MANAGER STATISTICS
# ============================================================

@router.get("/manager/statistics")
def manager_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=403,
            detail="Only managers can access statistics"
        )

    team_decisions = db.query(Decision).join(
        User,
        Decision.created_by == User.id
    ).filter(
        User.department == current_user.department
    )

    total_decisions = team_decisions.count()

    draft_decisions = team_decisions.filter(
        Decision.status == DecisionStatus.DRAFT
    ).count()

    under_review_decisions = team_decisions.filter(
        Decision.status == DecisionStatus.UNDER_REVIEW
    ).count()

    approved_decisions = team_decisions.filter(
        Decision.status == DecisionStatus.APPROVED
    ).count()

    rejected_decisions = team_decisions.filter(
        Decision.status == DecisionStatus.REJECTED
    ).count()

    archived_decisions = team_decisions.filter(
        Decision.status == DecisionStatus.ARCHIVED
    ).count()

    return {
        "total_decisions": total_decisions,
        "draft": draft_decisions,
        "under_review": under_review_decisions,
        "approved": approved_decisions,
        "rejected": rejected_decisions,
        "archived": archived_decisions
    }


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@router.get("/admin")
def admin_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can access this dashboard"
        )

    total_decisions = db.query(Decision).count()

    draft_decisions = db.query(Decision).filter(
        Decision.status == DecisionStatus.DRAFT
    ).count()

    under_review_decisions = db.query(Decision).filter(
        Decision.status == DecisionStatus.UNDER_REVIEW
    ).count()

    approved_decisions = db.query(Decision).filter(
        Decision.status == DecisionStatus.APPROVED
    ).count()

    rejected_decisions = db.query(Decision).filter(
        Decision.status == DecisionStatus.REJECTED
    ).count()

    archived_decisions = db.query(Decision).filter(
        Decision.status == DecisionStatus.ARCHIVED
    ).count()

    total_users = db.query(User).count()

    active_users = db.query(
        ActivityLog.user_id
    ).distinct().count()

    total_approvals = db.query(Approval).count()

    pending_approvals = db.query(Approval).filter(
        Approval.status == ApprovalStatus.PENDING
    ).count()

    approved_approvals = db.query(Approval).filter(
        Approval.status == ApprovalStatus.APPROVED
    ).count()

    rejected_approvals = db.query(Approval).filter(
        Approval.status == ApprovalStatus.REJECTED
    ).count()

    completed_approvals = (
        approved_approvals +
        rejected_approvals
    )

    if total_approvals > 0:
        approval_completion_rate = (
            completed_approvals /
            total_approvals
        ) * 100
    else:
        approval_completion_rate = 0

    recent_activities = db.query(ActivityLog).order_by(
        ActivityLog.created_at.desc()
    ).limit(10).all()

    return {
        "organization_statistics": {
            "total_decisions": total_decisions,
            "draft": draft_decisions,
            "under_review": under_review_decisions,
            "approved": approved_decisions,
            "rejected": rejected_decisions,
            "archived": archived_decisions
        },
        "user_activity": {
            "total_users": total_users,
            "active_users": active_users
        },
        "approval_statistics": {
            "total_approvals": total_approvals,
            "pending": pending_approvals,
            "approved": approved_approvals,
            "rejected": rejected_approvals,
            "completion_rate": approval_completion_rate
        },
        "recent_system_activity": [
            {
                "id": activity.id,
                "user_id": activity.user_id,
                "action": activity.action,
                "entity_type": activity.entity_type,
                "entity_id": activity.entity_id,
                "description": activity.description,
                "created_at": activity.created_at
            }
            for activity in recent_activities
        ]
    }


# ============================================================
# ADMIN ANALYTICS
# ============================================================

@router.get("/admin/analytics")
def admin_analytics(
    start_date: date | None = Query(
        default=None,
        description="Start date for analytics filtering"
    ),
    end_date: date | None = Query(
        default=None,
        description="End date for analytics filtering"
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can access analytics"
        )

    # --------------------------------------------------------
    # DATE VALIDATION
    # --------------------------------------------------------

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be later than end_date"
        )

    # --------------------------------------------------------
    # DATE RANGE
    # --------------------------------------------------------

    start_datetime = None
    end_datetime = None

    if start_date:
        start_datetime = datetime.combine(
            start_date,
            time.min
        )

    if end_date:
        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min
        )

    # --------------------------------------------------------
    # DECISION STATISTICS
    # --------------------------------------------------------

    decision_query = db.query(Decision)

    if start_datetime:
        decision_query = decision_query.filter(
            Decision.created_at >= start_datetime
        )

    if end_datetime:
        decision_query = decision_query.filter(
            Decision.created_at < end_datetime
        )

    total_decisions = decision_query.count()

    draft_decisions = decision_query.filter(
        Decision.status == DecisionStatus.DRAFT
    ).count()

    under_review_decisions = decision_query.filter(
        Decision.status == DecisionStatus.UNDER_REVIEW
    ).count()

    approved_decisions = decision_query.filter(
        Decision.status == DecisionStatus.APPROVED
    ).count()

    rejected_decisions = decision_query.filter(
        Decision.status == DecisionStatus.REJECTED
    ).count()

    archived_decisions = decision_query.filter(
        Decision.status == DecisionStatus.ARCHIVED
    ).count()

    # --------------------------------------------------------
    # USER STATISTICS
    # --------------------------------------------------------

    user_query = db.query(User)

    if start_datetime:
        user_query = user_query.filter(
            User.id.in_(
                db.query(ActivityLog.user_id).filter(
                    ActivityLog.created_at >= start_datetime
                )
            )
        )

    if end_datetime:
        user_query = user_query.filter(
            User.id.in_(
                db.query(ActivityLog.user_id).filter(
                    ActivityLog.created_at < end_datetime
                )
            )
        )

    filtered_users = user_query.count()

    # --------------------------------------------------------
    # APPROVAL STATISTICS
    # --------------------------------------------------------

    approval_query = db.query(Approval)

    if start_datetime:
        approval_query = approval_query.filter(
            Approval.created_at >= start_datetime
        )

    if end_datetime:
        approval_query = approval_query.filter(
            Approval.created_at < end_datetime
        )

    total_approvals = approval_query.count()

    pending_approvals = approval_query.filter(
        Approval.status == ApprovalStatus.PENDING
    ).count()

    approved_approvals = approval_query.filter(
        Approval.status == ApprovalStatus.APPROVED
    ).count()

    rejected_approvals = approval_query.filter(
        Approval.status == ApprovalStatus.REJECTED
    ).count()

    completed_approvals = (
        approved_approvals +
        rejected_approvals
    )

    if total_approvals > 0:
        completion_rate = (
            completed_approvals /
            total_approvals
        ) * 100
    else:
        completion_rate = 0

    # --------------------------------------------------------
    # RETURN ANALYTICS
    # --------------------------------------------------------

    return {
        "date_filter": {
            "start_date": start_date,
            "end_date": end_date
        },
        "decision_statistics": {
            "total": total_decisions,
            "draft": draft_decisions,
            "under_review": under_review_decisions,
            "approved": approved_decisions,
            "rejected": rejected_decisions,
            "archived": archived_decisions
        },
        "user_statistics": {
            "total_users": filtered_users
        },
        "approval_statistics": {
            "total": total_approvals,
            "pending": pending_approvals,
            "approved": approved_approvals,
            "rejected": rejected_approvals,
            "completion_rate": completion_rate
        }
    }


# ============================================================
# ADMIN DECISION ACTIVITY
# ============================================================

@router.get("/admin/decision-activity")
def admin_decision_activity(
    start_date: date | None = Query(
        default=None,
        description="Start date for activity filtering"
    ),
    end_date: date | None = Query(
        default=None,
        description="End date for activity filtering"
    ),
    group_by: str = Query(
        default="day",
        description="Group activity by day, week, or month"
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # --------------------------------------------------------
    # ADMIN AUTHORIZATION
    # --------------------------------------------------------

    if current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can access decision activity"
        )

    # --------------------------------------------------------
    # DATE VALIDATION
    # --------------------------------------------------------

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be later than end_date"
        )

    # --------------------------------------------------------
    # GROUP BY VALIDATION
    # --------------------------------------------------------

    if group_by not in ["day", "week", "month"]:
        raise HTTPException(
            status_code=422,
            detail="group_by must be day, week, or month"
        )

    # --------------------------------------------------------
    # DATE RANGE
    # --------------------------------------------------------

    start_datetime = None
    end_datetime = None

    if start_date:
        start_datetime = datetime.combine(
            start_date,
            time.min
        )

    if end_date:
        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min
        )

    # --------------------------------------------------------
    # DATABASE AGGREGATION
    # --------------------------------------------------------

    activity_period = func.date_trunc(
        group_by,
        ActivityLog.created_at
    )

    query = db.query(
        activity_period.label("period"),
        func.count(ActivityLog.id).label("activity_count")
    )

    # --------------------------------------------------------
    # DATE FILTERING
    # --------------------------------------------------------

    if start_datetime:
        query = query.filter(
            ActivityLog.created_at >= start_datetime
        )

    if end_datetime:
        query = query.filter(
            ActivityLog.created_at < end_datetime
        )

    # --------------------------------------------------------
    # GROUP AND ORDER
    # --------------------------------------------------------

    results = query.group_by(
        activity_period
    ).order_by(
        activity_period
    ).all()

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "date_filter": {
            "start_date": start_date,
            "end_date": end_date
        },
        "group_by": group_by,
        "activity": [
            {
                "period": period,
                "activity_count": activity_count
            }
            for period, activity_count in results
        ]
    }


# ============================================================
# ADMIN APPROVAL STATISTICS
# ============================================================

@router.get("/admin/approval-statistics")
def admin_approval_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # --------------------------------------------------------
    # ADMIN AUTHORIZATION
    # --------------------------------------------------------

    if current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can access approval statistics"
        )

    # --------------------------------------------------------
    # TOTAL APPROVALS
    # --------------------------------------------------------

    total_approvals = (
        db.query(func.count(Approval.id))
        .scalar()
    ) or 0

    # --------------------------------------------------------
    # PENDING APPROVALS
    # --------------------------------------------------------

    pending_approvals = (
        db.query(func.count(Approval.id))
        .filter(
            Approval.status == ApprovalStatus.PENDING
        )
        .scalar()
    ) or 0

    # --------------------------------------------------------
    # COMPLETED APPROVALS
    # --------------------------------------------------------

    completed_approvals = (
        db.query(func.count(Approval.id))
        .filter(
            Approval.status.in_([
                ApprovalStatus.APPROVED,
                ApprovalStatus.REJECTED
            ])
        )
        .scalar()
    ) or 0

    # --------------------------------------------------------
    # COMPLETION RATE
    # --------------------------------------------------------

    if total_approvals == 0:
        completion_rate = 0.0
    else:
        completion_rate = (
            completed_approvals /
            total_approvals
        ) * 100

    # --------------------------------------------------------
    # APPROVAL TURNAROUND
    #
    # created_at = approval assigned
    # updated_at = approval completed
    #
    # The existing approval workflow changes the status
    # from Pending to Approved/Rejected, which updates
    # updated_at automatically.
    # --------------------------------------------------------

    turnaround = (
        db.query(
            func.avg(
                func.extract(
                    "epoch",
                    Approval.updated_at - Approval.created_at
                )
            ).label("average_seconds"),
            func.min(
                func.extract(
                    "epoch",
                    Approval.updated_at - Approval.created_at
                )
            ).label("fastest_seconds"),
            func.max(
                func.extract(
                    "epoch",
                    Approval.updated_at - Approval.created_at
                )
            ).label("slowest_seconds")
        )
        .filter(
            Approval.status.in_([
                ApprovalStatus.APPROVED,
                ApprovalStatus.REJECTED
            ])
        )
        .first()
    )

    average_seconds = turnaround.average_seconds or 0
    fastest_seconds = turnaround.fastest_seconds or 0
    slowest_seconds = turnaround.slowest_seconds or 0

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "total_approvals": total_approvals,
        "completed_approvals": completed_approvals,
        "pending_approvals": pending_approvals,
        "completion_rate": round(
            completion_rate,
            2
        ),
        "average_turnaround_hours": round(
            average_seconds / 3600,
            2
        ),
        "fastest_turnaround_hours": round(
            fastest_seconds / 3600,
            2
        ),
        "slowest_turnaround_hours": round(
            slowest_seconds / 3600,
            2
        )
    }


# ============================================================
# ADMIN USER ACTIVITY
# ============================================================

@router.get("/admin/user-activity")
def admin_user_activity(
    limit: int = Query(
        default=50,
        ge=1,
        le=100
    ),
    start_date: date | None = Query(
        default=None,
        description="Start date for activity filtering"
    ),
    end_date: date | None = Query(
        default=None,
        description="End date for activity filtering"
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # --------------------------------------------------------
    # ADMIN AUTHORIZATION
    # --------------------------------------------------------

    if current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can access user activity"
        )

    # --------------------------------------------------------
    # DATE VALIDATION
    # --------------------------------------------------------

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be later than end_date"
        )

    # --------------------------------------------------------
    # DATE RANGE
    # --------------------------------------------------------

    start_datetime = None
    end_datetime = None

    if start_date:
        start_datetime = datetime.combine(
            start_date,
            time.min
        )

    if end_date:
        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min
        )

    # --------------------------------------------------------
    # USER ACTIVITY QUERY
    # --------------------------------------------------------

    query = (
        db.query(
            ActivityLog,
            User.full_name,
            User.email
        )
        .join(
            User,
            ActivityLog.user_id == User.id
        )
    )

    # --------------------------------------------------------
    # DATE FILTERING
    # --------------------------------------------------------

    if start_datetime:
        query = query.filter(
            ActivityLog.created_at >= start_datetime
        )

    if end_datetime:
        query = query.filter(
            ActivityLog.created_at < end_datetime
        )

    # --------------------------------------------------------
    # ORDER AND LIMIT
    # --------------------------------------------------------

    activities = (
        query
        .order_by(
            ActivityLog.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "date_filter": {
            "start_date": start_date,
            "end_date": end_date
        },
        "count": len(activities),
        "activities": [
            {
                "id": activity.id,
                "user_id": activity.user_id,
                "user_name": full_name,
                "user_email": email,
                "action": activity.action,
                "entity_type": activity.entity_type,
                "entity_id": activity.entity_id,
                "description": activity.description,
                "created_at": activity.created_at
            }
            for activity, full_name, email in activities
        ]
    }