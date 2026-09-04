from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.approval import Approval, ApprovalStatus
from app.models.audit import AuditLog
from app.models.decision import Decision, DecisionStatus
from app.models.user import User, UserRole

from app.schemas.approval import ApprovalResponse
from app.schemas.dashboard import (
    ActivityResponse,
    EmployeeDashboardResponse,
)
from datetime import date, datetime, time

from sqlalchemy import func
from app.schemas.decision import DecisionResponse

from app.services.auth import get_current_user, require_role

from app.schemas.analytics import DecisionAnalyticsResponse

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

# Organization helpers
def require_organization_id(current_user: User) -> int:
    """Return the current user's organization ID or reject unassigned users."""
    if current_user.organization_id is None:
        raise HTTPException(
            status_code=403,
            detail="You are not assigned to an organization"
        )
    return current_user.organization_id


def organization_decisions_query(db: Session, current_user: User):
    organization_id = require_organization_id(current_user)
    return db.query(Decision).filter(
        Decision.organization_id == organization_id
    )


def organization_users_query(db: Session, current_user: User):
    organization_id = require_organization_id(current_user)
    return db.query(User).filter(
        User.organization_id == organization_id
    )


def organization_approvals_query(db: Session, current_user: User):
    organization_id = require_organization_id(current_user)
    return (
        db.query(Approval)
        .join(Decision, Approval.decision_id == Decision.id)
        .filter(Decision.organization_id == organization_id)
    )


# Employee Dashboard
@router.get(
    "/employee",
    response_model=EmployeeDashboardResponse
)
def get_employee_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decisions_query = (
        db.query(Decision)
        .filter(Decision.created_by == current_user.id)
    )

    total_decisions = decisions_query.count()

    draft_decisions = (
        decisions_query
        .filter(Decision.status == DecisionStatus.DRAFT)
        .count()
    )

    under_review = (
        decisions_query
        .filter(Decision.status == DecisionStatus.UNDER_REVIEW)
        .count()
    )

    approved_decisions = (
        decisions_query
        .filter(Decision.status == DecisionStatus.APPROVED)
        .count()
    )

    rejected_decisions = (
        decisions_query
        .filter(Decision.status == DecisionStatus.REJECTED)
        .count()
    )

    pending_reviews = (
        db.query(Approval)
        .filter(
            Approval.reviewer_id == current_user.id,
            Approval.status == ApprovalStatus.PENDING
        )
        .count()
    )

    recent_activities = (
        db.query(AuditLog)
        .filter(AuditLog.user_id == current_user.id)
        .order_by(AuditLog.created_at.desc())
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


# Employee Decisions
@router.get(
    "/employee/decisions",
    response_model=list[DecisionResponse]
)
def get_employee_decisions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    offset = (page - 1) * page_size

    decisions = (
        db.query(Decision)
        .filter(Decision.created_by == current_user.id)
        .order_by(Decision.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return decisions


# Employee Pending Reviews
@router.get(
    "/employee/pending-reviews",
    response_model=list[ApprovalResponse]
)
def get_employee_pending_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Approval)
        .filter(
            Approval.reviewer_id == current_user.id,
            Approval.status == ApprovalStatus.PENDING
        )
        .order_by(Approval.created_at.desc())
        .all()
    )


# Employee Recent Activities
@router.get(
    "/employee/recent-activities",
    response_model=list[ActivityResponse]
)
def get_employee_recent_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(AuditLog)
        .filter(AuditLog.user_id == current_user.id)
        .order_by(AuditLog.created_at.desc())
        .limit(10)
        .all()
    )


# Manager Dashboard
@router.get(
    "/manager"
)
def get_manager_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.MANAGER)
    )
):
    total_decisions = (
        organization_decisions_query(db, current_user)
        .count()
    )

    draft_decisions = (
        organization_decisions_query(db, current_user)
        .filter(Decision.status == DecisionStatus.DRAFT)
        .count()
    )

    under_review = (
        organization_decisions_query(db, current_user)
        .filter(Decision.status == DecisionStatus.UNDER_REVIEW)
        .count()
    )

    approved_decisions = (
        organization_decisions_query(db, current_user)
        .filter(Decision.status == DecisionStatus.APPROVED)
        .count()
    )

    rejected_decisions = (
        organization_decisions_query(db, current_user)
        .filter(Decision.status == DecisionStatus.REJECTED)
        .count()
    )

    pending_approvals = (
        organization_approvals_query(db, current_user)
        .filter(Approval.status == ApprovalStatus.PENDING)
        .count()
    )

    return {
        "manager_id": current_user.id,
        "manager_name": current_user.full_name,
        "total_decisions": total_decisions,
        "draft_decisions": draft_decisions,
        "under_review": under_review,
        "approved_decisions": approved_decisions,
        "rejected_decisions": rejected_decisions,
        "pending_approvals": pending_approvals
    }


# Manager Decisions
@router.get(
    "/manager/decisions",
    response_model=list[DecisionResponse]
)
def get_manager_decisions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.MANAGER)
    )
):
    offset = (page - 1) * page_size

    decisions = (
        organization_decisions_query(db, current_user)
        .order_by(Decision.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return decisions


# Admin Dashboard
@router.get(
    "/admin"
)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMINISTRATOR)
    )
):
    total_users = (
        organization_users_query(db, current_user)
        .count()
    )

    total_decisions = (
        organization_decisions_query(db, current_user)
        .count()
    )

    draft_decisions = (
        organization_decisions_query(db, current_user)
        .filter(Decision.status == DecisionStatus.DRAFT)
        .count()
    )

    under_review = (
        organization_decisions_query(db, current_user)
        .filter(Decision.status == DecisionStatus.UNDER_REVIEW)
        .count()
    )

    approved_decisions = (
        organization_decisions_query(db, current_user)
        .filter(Decision.status == DecisionStatus.APPROVED)
        .count()
    )

    rejected_decisions = (
        organization_decisions_query(db, current_user)
        .filter(Decision.status == DecisionStatus.REJECTED)
        .count()
    )

    pending_approvals = (
        organization_approvals_query(db, current_user)
        .filter(Approval.status == ApprovalStatus.PENDING)
        .count()
    )

    return {
        "admin_id": current_user.id,
        "admin_name": current_user.full_name,
        "total_users": total_users,
        "total_decisions": total_decisions,
        "draft_decisions": draft_decisions,
        "under_review": under_review,
        "approved_decisions": approved_decisions,
        "rejected_decisions": rejected_decisions,
        "pending_approvals": pending_approvals
    }
    
@router.get(
    "/admin/users"
)
def get_admin_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMINISTRATOR)
    )
):
    offset = (page - 1) * page_size

    users = (
        organization_users_query(db, current_user)
        .order_by(User.id)
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return users

@router.get(
    "/admin/decisions",
    response_model=list[DecisionResponse]
)
def get_admin_decisions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMINISTRATOR)
    )
):
    offset = (page - 1) * page_size

    decisions = (
        organization_decisions_query(db, current_user)
        .order_by(Decision.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return decisions

# Decision Analytics
@router.get(
    "/analytics",
    response_model=DecisionAnalyticsResponse
)
def get_decision_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMINISTRATOR)
    )
):
    total_decisions = (
        organization_decisions_query(db, current_user)
        .count()
    )

    draft_decisions = (
        organization_decisions_query(db, current_user)
        .filter(
            Decision.status == DecisionStatus.DRAFT
        )
        .count()
    )

    under_review = (
        organization_decisions_query(db, current_user)
        .filter(
            Decision.status == DecisionStatus.UNDER_REVIEW
        )
        .count()
    )

    approved_decisions = (
        organization_decisions_query(db, current_user)
        .filter(
            Decision.status == DecisionStatus.APPROVED
        )
        .count()
    )

    rejected_decisions = (
        organization_decisions_query(db, current_user)
        .filter(
            Decision.status == DecisionStatus.REJECTED
        )
        .count()
    )

    archived_decisions = (
        organization_decisions_query(db, current_user)
        .filter(
            Decision.status == DecisionStatus.ARCHIVED
        )
        .count()
    )

    total_approvals = (
        organization_approvals_query(db, current_user)
        .count()
    )

    pending_approvals = (
        organization_approvals_query(db, current_user)
        .filter(
            Approval.status == ApprovalStatus.PENDING
        )
        .count()
    )

    approved_approvals = (
        organization_approvals_query(db, current_user)
        .filter(
            Approval.status == ApprovalStatus.APPROVED
        )
        .count()
    )

    rejected_approvals = (
        organization_approvals_query(db, current_user)
        .filter(
            Approval.status == ApprovalStatus.REJECTED
        )
        .count()
    )

    return DecisionAnalyticsResponse(
        total_decisions=total_decisions,
        draft_decisions=draft_decisions,
        under_review=under_review,
        approved_decisions=approved_decisions,
        rejected_decisions=rejected_decisions,
        archived_decisions=archived_decisions,
        total_approvals=total_approvals,
        pending_approvals=pending_approvals,
        approved_approvals=approved_approvals,
        rejected_approvals=rejected_approvals
    )
    
# Manager Team Decisions
@router.get(
    "/manager/team-decisions",
    response_model=list[DecisionResponse]
)
def get_manager_team_decisions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.MANAGER)
    )
):
    offset = (page - 1) * page_size

    decisions = (
        db.query(Decision)
        .join(User, Decision.created_by == User.id)
        .filter(
            User.department == current_user.department,
            User.organization_id == require_organization_id(current_user)
        )
        .order_by(Decision.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return decisions

# Manager Pending Approvals
@router.get(
    "/manager/pending-approvals",
    response_model=list[ApprovalResponse]
)
def get_manager_pending_approvals(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.MANAGER)
    )
):
    offset = (page - 1) * page_size

    approvals = (
        db.query(Approval)
        .join(
            Decision,
            Approval.decision_id == Decision.id
        )
        .join(
            User,
            Decision.created_by == User.id
        )
        .filter(
            User.department == current_user.department,
            User.organization_id == require_organization_id(current_user),
            Decision.organization_id == require_organization_id(current_user),
            Approval.status == ApprovalStatus.PENDING
        )
        .order_by(Approval.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return approvals
# Manager Decision Statistics
@router.get(
    "/manager/statistics"
)
def get_manager_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.MANAGER)
    )
):
    team_query = (
        db.query(Decision)
        .join(
            User,
            Decision.created_by == User.id
        )
        .filter(
            User.department == current_user.department,
            User.organization_id == require_organization_id(current_user)
        )
    )

    total_decisions = team_query.count()

    draft_decisions = (
        team_query
        .filter(
            Decision.status == DecisionStatus.DRAFT
        )
        .count()
    )

    under_review = (
        team_query
        .filter(
            Decision.status == DecisionStatus.UNDER_REVIEW
        )
        .count()
    )

    approved_decisions = (
        team_query
        .filter(
            Decision.status == DecisionStatus.APPROVED
        )
        .count()
    )

    rejected_decisions = (
        team_query
        .filter(
            Decision.status == DecisionStatus.REJECTED
        )
        .count()
    )

    archived_decisions = (
        team_query
        .filter(
            Decision.status == DecisionStatus.ARCHIVED
        )
        .count()
    )

    return {
        "total_decisions": total_decisions,
        "draft_decisions": draft_decisions,
        "under_review": under_review,
        "approved_decisions": approved_decisions,
        "rejected_decisions": rejected_decisions,
        "archived_decisions": archived_decisions
    }
    
# Admin Analytics
@router.get(
    "/admin/analytics"
)
def get_admin_analytics(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMINISTRATOR)
    )
):
    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date"
        )

    decision_query = organization_decisions_query(db, current_user)
    approval_query = organization_approvals_query(db, current_user)

    if start_date is not None:
        start_datetime = datetime.combine(
            start_date,
            time.min
        )

        decision_query = decision_query.filter(
            Decision.created_at >= start_datetime
        )

        approval_query = approval_query.filter(
            Approval.created_at >= start_datetime
        )

    if end_date is not None:
        end_datetime = datetime.combine(
            end_date,
            time.max
        )

        decision_query = decision_query.filter(
            Decision.created_at <= end_datetime
        )

        approval_query = approval_query.filter(
            Approval.created_at <= end_datetime
        )

    total_decisions = decision_query.count()

    approved_decisions = (
        decision_query
        .filter(
            Decision.status == DecisionStatus.APPROVED
        )
        .count()
    )

    rejected_decisions = (
        decision_query
        .filter(
            Decision.status == DecisionStatus.REJECTED
        )
        .count()
    )

    under_review = (
        decision_query
        .filter(
            Decision.status == DecisionStatus.UNDER_REVIEW
        )
        .count()
    )

    archived_decisions = (
        decision_query
        .filter(
            Decision.status == DecisionStatus.ARCHIVED
        )
        .count()
    )

    total_users = organization_users_query(db, current_user).count()

    employees = (
        organization_users_query(db, current_user)
        .filter(User.role == UserRole.EMPLOYEE)
        .count()
    )

    reviewers = (
        organization_users_query(db, current_user)
        .filter(User.role == UserRole.REVIEWER)
        .count()
    )

    managers = (
        organization_users_query(db, current_user)
        .filter(User.role == UserRole.MANAGER)
        .count()
    )

    administrators = (
        organization_users_query(db, current_user)
        .filter(User.role == UserRole.ADMINISTRATOR)
        .count()
    )

    total_approvals = approval_query.count()

    pending_approvals = (
        approval_query
        .filter(
            Approval.status == ApprovalStatus.PENDING
        )
        .count()
    )

    approved_approvals = (
        approval_query
        .filter(
            Approval.status == ApprovalStatus.APPROVED
        )
        .count()
    )

    rejected_approvals = (
        approval_query
        .filter(
            Approval.status == ApprovalStatus.REJECTED
        )
        .count()
    )

    return {
        "decision_statistics": {
            "total_decisions": total_decisions,
            "approved_decisions": approved_decisions,
            "rejected_decisions": rejected_decisions,
            "under_review": under_review,
            "archived_decisions": archived_decisions
        },
        "user_statistics": {
            "total_users": total_users,
            "active_users": None,
            "users_by_role": {
                "Employee": employees,
                "Reviewer": reviewers,
                "Manager": managers,
                "Administrator": administrators
            }
        },
        "approval_statistics": {
            "total_approvals": total_approvals,
            "pending_approvals": pending_approvals,
            "approved_approvals": approved_approvals,
            "rejected_approvals": rejected_approvals
        }
    }
# Admin Decision Activity
@router.get(
    "/admin/decision-activity"
)
def get_admin_decision_activity(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMINISTRATOR)
    )
):
    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date"
        )

    query = (
        organization_decisions_query(db, current_user).with_entities(
            func.date(Decision.created_at).label("date"),
            func.count(Decision.id).label("count")
        )
    )

    if start_date is not None:
        start_datetime = datetime.combine(
            start_date,
            time.min
        )

        query = query.filter(
            Decision.created_at >= start_datetime
        )

    if end_date is not None:
        end_datetime = datetime.combine(
            end_date,
            time.max
        )

        query = query.filter(
            Decision.created_at <= end_datetime
        )

    results = (
        query
        .group_by(func.date(Decision.created_at))
        .order_by(func.date(Decision.created_at))
        .all()
    )

    return {
        "start_date": start_date,
        "end_date": end_date,
        "daily_activity": {
            str(row.date): row.count
            for row in results
        }
    }
    
# Admin Approval Statistics
@router.get(
    "/admin/approval-statistics"
)
def get_admin_approval_statistics(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMINISTRATOR)
    )
):
    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date"
        )

    query = organization_approvals_query(db, current_user)

    if start_date is not None:
        start_datetime = datetime.combine(
            start_date,
            time.min
        )

        query = query.filter(
            Approval.created_at >= start_datetime
        )

    if end_date is not None:
        end_datetime = datetime.combine(
            end_date,
            time.max
        )

        query = query.filter(
            Approval.created_at <= end_datetime
        )

    completed_approvals = (
        query
        .filter(
            Approval.completed_at.isnot(None)
        )
        .all()
    )

    pending_approvals = (
        query
        .filter(
            Approval.status == ApprovalStatus.PENDING
        )
        .count()
    )

    if not completed_approvals:
        return {
            "average_approval_time_hours": 0,
            "fastest_approval_time_hours": 0,
            "slowest_approval_time_hours": 0,
            "pending_approvals": pending_approvals
        }

    turnaround_times = [
        (
            approval.completed_at -
            approval.created_at
        ).total_seconds() / 3600
        for approval in completed_approvals
    ]

    return {
        "average_approval_time_hours": (
            sum(turnaround_times) /
            len(turnaround_times)
        ),
        "fastest_approval_time_hours": min(
            turnaround_times
        ),
        "slowest_approval_time_hours": max(
            turnaround_times
        ),
        "pending_approvals": pending_approvals
    }
    
# Admin Approval Completion Rate
@router.get(
    "/admin/approval-completion-rate"
)
def get_admin_approval_completion_rate(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMINISTRATOR)
    )
):
    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date"
        )

    query = organization_approvals_query(db, current_user)

    if start_date is not None:
        query = query.filter(
            Approval.created_at >= datetime.combine(
                start_date,
                time.min
            )
        )

    if end_date is not None:
        query = query.filter(
            Approval.created_at <= datetime.combine(
                end_date,
                time.max
            )
        )

    total_approvals = query.count()

    completed_approvals = (
        query
        .filter(
            Approval.status.in_(
                [
                    ApprovalStatus.APPROVED,
                    ApprovalStatus.REJECTED
                ]
            )
        )
        .count()
    )

    if total_approvals == 0:
        completion_rate = 0
    else:
        completion_rate = (
            completed_approvals / total_approvals
        ) * 100

    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_approvals": total_approvals,
        "completed_approvals": completed_approvals,
        "completion_rate": completion_rate
    }


# Admin User Activity
@router.get(
    "/admin/user-activity"
)
def get_admin_user_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMINISTRATOR)
    )
):
    active_users = (
        db.query(
            User.id.label("user_id"),
            User.full_name.label("full_name"),
            User.email.label("email"),
            User.role.label("role"),
            func.max(AuditLog.created_at).label(
                "last_activity"
            )
        )
        .join(
            AuditLog,
            AuditLog.user_id == User.id
        )
        .filter(User.organization_id == require_organization_id(current_user))
        .group_by(
            User.id,
            User.full_name,
            User.email,
            User.role
        )
        .order_by(
            func.max(AuditLog.created_at).desc()
        )
        .all()
    )

    return {
        "active_users": [
            {
                "user_id": user.user_id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role.value
                    if hasattr(user.role, "value")
                    else user.role,
                "last_activity": user.last_activity
            }
            for user in active_users
        ],
        "active_user_count": len(active_users)
    }
    
# Admin Decision Category Analytics
@router.get(
    "/admin/analytics/categories"
)
def get_admin_category_analytics(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMINISTRATOR)
    )
):
    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date"
        )

    query = (
        organization_decisions_query(db, current_user).with_entities(
            Decision.category.label("category"),
            func.count(Decision.id).label("count")
        )
    )

    if start_date is not None:
        query = query.filter(
            Decision.created_at >= datetime.combine(
                start_date,
                time.min
            )
        )

    if end_date is not None:
        query = query.filter(
            Decision.created_at <= datetime.combine(
                end_date,
                time.max
            )
        )

    results = (
        query
        .group_by(Decision.category)
        .order_by(func.count(Decision.id).desc())
        .all()
    )

    return {
        "categories": [
            {
                "category": row.category,
                "count": row.count
            }
            for row in results
        ]
    }
    
# Admin Decision Status Analytics
@router.get(
    "/admin/analytics/status"
)
def get_admin_status_analytics(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMINISTRATOR)
    )
):
    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date"
        )

    query = (
        organization_decisions_query(db, current_user).with_entities(
            Decision.status.label("status"),
            func.count(Decision.id).label("count")
        )
    )

    if start_date is not None:
        query = query.filter(
            Decision.created_at >= datetime.combine(
                start_date,
                time.min
            )
        )

    if end_date is not None:
        query = query.filter(
            Decision.created_at <= datetime.combine(
                end_date,
                time.max
            )
        )

    results = (
        query
        .group_by(Decision.status)
        .order_by(Decision.status)
        .all()
    )

    return {
        "statuses": [
            {
                "status": (
                    row.status.value
                    if hasattr(row.status, "value")
                    else row.status
                ),
                "count": row.count
            }
            for row in results
        ]
    }
    
# Admin User Role Analytics
@router.get(
    "/admin/analytics/users"
)
def get_admin_user_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMINISTRATOR)
    )
):
    results = (
        organization_users_query(db, current_user).with_entities(
            User.role.label("role"),
            func.count(User.id).label("count")
        )
        .group_by(User.role)
        .order_by(User.role)
        .all()
    )

    return {
        "total_users": organization_users_query(db, current_user).count(),
        "users_by_role": [
            {
                "role": (
                    row.role.value
                    if hasattr(row.role, "value")
                    else row.role
                ),
                "count": row.count
            }
            for row in results
        ]
    }
