from datetime import datetime, date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.decision import Decision
from app.models.approval import Approval
from app.models.activity import Activity


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# ============================================================
# ROLE CHECKING
# ============================================================

def require_role(current_user: User, allowed_roles: list[str]):
    """
    Allow access only to users whose role matches one of
    the allowed roles.
    """

    user_role = str(current_user.role).strip().lower()

    allowed = [
        role.strip().lower()
        for role in allowed_roles
    ]

    if user_role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this resource"
        )


def validate_date_range(
    start_date: Optional[date],
    end_date: Optional[date]
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )


def apply_decision_date_filter(
    query,
    start_date: Optional[date],
    end_date: Optional[date]
):
    if start_date:
        query = query.filter(
            Decision.created_at >= datetime.combine(
                start_date,
                datetime.min.time()
            )
        )

    if end_date:
        query = query.filter(
            Decision.created_at <
            datetime.combine(
                end_date + timedelta(days=1),
                datetime.min.time()
            )
        )

    return query


# ============================================================
# EMPLOYEE DASHBOARD
# GET /dashboard/employee
# ============================================================

@router.get("/employee")
def employee_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_role(
        current_user,
        ["Employee"]
    )

    total_decisions = (
        db.query(func.count(Decision.id))
        .filter(
            Decision.created_by == current_user.id
        )
        .scalar()
    )

    draft_decisions = (
        db.query(func.count(Decision.id))
        .filter(
            Decision.created_by == current_user.id,
            Decision.status == "Draft"
        )
        .scalar()
    )

    under_review = (
        db.query(func.count(Decision.id))
        .filter(
            Decision.created_by == current_user.id,
            Decision.status == "Under Review"
        )
        .scalar()
    )

    approved_decisions = (
        db.query(func.count(Decision.id))
        .filter(
            Decision.created_by == current_user.id,
            Decision.status == "Approved"
        )
        .scalar()
    )

    rejected_decisions = (
        db.query(func.count(Decision.id))
        .filter(
            Decision.created_by == current_user.id,
            Decision.status == "Rejected"
        )
        .scalar()
    )

    archived_decisions = (
        db.query(func.count(Decision.id))
        .filter(
            Decision.created_by == current_user.id,
            Decision.status == "Archived"
        )
        .scalar()
    )

    pending_approvals = (
        db.query(func.count(Approval.id))
        .join(
            Decision,
            Approval.decision_id == Decision.id
        )
        .filter(
            Decision.created_by == current_user.id,
            Approval.status == "Pending"
        )
        .scalar()
    )

    return {
        "user_id": current_user.id,
        "total_decisions": total_decisions or 0,
        "draft_decisions": draft_decisions or 0,
        "under_review_decisions": under_review or 0,
        "approved_decisions": approved_decisions or 0,
        "rejected_decisions": rejected_decisions or 0,
        "archived_decisions": archived_decisions or 0,
        "pending_approvals": pending_approvals or 0
    }


# ============================================================
# MANAGER DASHBOARD
# GET /dashboard/manager
# ============================================================

@router.get("/manager")
def manager_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_role(
        current_user,
        ["Manager"]
    )

    # Team is identified using the manager's department.
    team_decisions = (
        db.query(func.count(Decision.id))
        .join(
            User,
            Decision.created_by == User.id
        )
        .filter(
            User.department == current_user.department
        )
        .scalar()
    )

    draft_decisions = (
        db.query(func.count(Decision.id))
        .join(
            User,
            Decision.created_by == User.id
        )
        .filter(
            User.department == current_user.department,
            Decision.status == "Draft"
        )
        .scalar()
    )

    under_review = (
        db.query(func.count(Decision.id))
        .join(
            User,
            Decision.created_by == User.id
        )
        .filter(
            User.department == current_user.department,
            Decision.status == "Under Review"
        )
        .scalar()
    )

    approved_decisions = (
        db.query(func.count(Decision.id))
        .join(
            User,
            Decision.created_by == User.id
        )
        .filter(
            User.department == current_user.department,
            Decision.status == "Approved"
        )
        .scalar()
    )

    rejected_decisions = (
        db.query(func.count(Decision.id))
        .join(
            User,
            Decision.created_by == User.id
        )
        .filter(
            User.department == current_user.department,
            Decision.status == "Rejected"
        )
        .scalar()
    )

    archived_decisions = (
        db.query(func.count(Decision.id))
        .join(
            User,
            Decision.created_by == User.id
        )
        .filter(
            User.department == current_user.department,
            Decision.status == "Archived"
        )
        .scalar()
    )

    return {
        "manager_id": current_user.id,
        "department": current_user.department,
        "total_decisions": team_decisions or 0,
        "draft_decisions": draft_decisions or 0,
        "under_review_decisions": under_review or 0,
        "approved_decisions": approved_decisions or 0,
        "rejected_decisions": rejected_decisions or 0,
        "archived_decisions": archived_decisions or 0
    }


# ============================================================
# MANAGER PENDING APPROVALS
# GET /dashboard/manager/pending-approvals
# ============================================================

@router.get("/manager/pending-approvals")
def manager_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_role(
        current_user,
        ["Manager"]
    )

    approvals = (
        db.query(
            Approval.id.label("approval_id"),
            Approval.approval_level,
            Approval.status,
            Approval.created_at,
            Decision.id.label("decision_id"),
            Decision.title.label("decision"),
            User.id.label("reviewer_id"),
            User.full_name.label("assigned_reviewer")
        )
        .join(
            Decision,
            Approval.decision_id == Decision.id
        )
        .join(
            User,
            Approval.reviewer_id == User.id
        )
        .filter(
            Approval.status == "Pending",
            User.department == current_user.department
        )
        .order_by(
            Approval.created_at.desc()
        )
        .all()
    )

    return [
        {
            "approval_id": row.approval_id,
            "decision_id": row.decision_id,
            "decision": row.decision,
            "approval_level": row.approval_level,
            "assigned_reviewer": row.assigned_reviewer,
            "reviewer_id": row.reviewer_id,
            "current_status": row.status,
            "created_date": row.created_at
        }
        for row in approvals
    ]


# ============================================================
# MANAGER STATISTICS
# GET /dashboard/manager/statistics
# ============================================================

@router.get("/manager/statistics")
def manager_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_role(
        current_user,
        ["Manager"]
    )

    base_query = (
        db.query(Decision)
        .join(
            User,
            Decision.created_by == User.id
        )
        .filter(
            User.department == current_user.department
        )
    )

    total = base_query.with_entities(
        func.count(Decision.id)
    ).scalar()

    status_counts = dict(
        base_query.with_entities(
            Decision.status,
            func.count(Decision.id)
        )
        .group_by(Decision.status)
        .all()
    )

    return {
        "department": current_user.department,
        "total_decisions": total or 0,
        "draft_decisions": status_counts.get("Draft", 0),
        "under_review_decisions": status_counts.get(
            "Under Review",
            0
        ),
        "approved_decisions": status_counts.get(
            "Approved",
            0
        ),
        "rejected_decisions": status_counts.get(
            "Rejected",
            0
        ),
        "archived_decisions": status_counts.get(
            "Archived",
            0
        )
    }


# ============================================================
# ADMIN DASHBOARD
# GET /dashboard/admin
# ============================================================

@router.get("/admin")
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_role(
        current_user,
        ["Admin", "Administrator"]
    )

    total_users = (
        db.query(func.count(User.id))
        .scalar()
    )

    total_decisions = (
        db.query(func.count(Decision.id))
        .scalar()
    )

    total_approvals = (
        db.query(func.count(Approval.id))
        .scalar()
    )

    pending_approvals = (
        db.query(func.count(Approval.id))
        .filter(
            Approval.status == "Pending"
        )
        .scalar()
    )

    approved_approvals = (
        db.query(func.count(Approval.id))
        .filter(
            Approval.status == "Approved"
        )
        .scalar()
    )

    rejected_approvals = (
        db.query(func.count(Approval.id))
        .filter(
            Approval.status == "Rejected"
        )
        .scalar()
    )

    status_counts = dict(
        db.query(
            Decision.status,
            func.count(Decision.id)
        )
        .group_by(Decision.status)
        .all()
    )

    return {
        "system_analytics": {
            "total_users": total_users or 0,
            "total_decisions": total_decisions or 0
        },
        "approval_statistics": {
            "total_approvals": total_approvals or 0,
            "pending_approvals": pending_approvals or 0,
            "approved_approvals": approved_approvals or 0,
            "rejected_approvals": rejected_approvals or 0
        },
        "decision_status_statistics": {
            "draft": status_counts.get("Draft", 0),
            "under_review": status_counts.get(
                "Under Review",
                0
            ),
            "approved": status_counts.get(
                "Approved",
                0
            ),
            "rejected": status_counts.get(
                "Rejected",
                0
            ),
            "archived": status_counts.get(
                "Archived",
                0
            )
        }
    }


# ============================================================
# ADMIN ANALYTICS
# GET /dashboard/admin/analytics
# ============================================================

@router.get("/admin/analytics")
def admin_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_role(
        current_user,
        ["Admin", "Administrator"]
    )

    validate_date_range(
        start_date,
        end_date
    )

    decision_query = db.query(Decision)

    decision_query = apply_decision_date_filter(
        decision_query,
        start_date,
        end_date
    )

    total_decisions = decision_query.with_entities(
        func.count(Decision.id)
    ).scalar()

    status_counts = dict(
        decision_query.with_entities(
            Decision.status,
            func.count(Decision.id)
        )
        .group_by(Decision.status)
        .all()
    )

    user_query = db.query(User)

    if start_date or end_date:
        # User table currently has no created_at field.
        # Therefore total users remain organization-wide.
        total_users = user_query.with_entities(
            func.count(User.id)
        ).scalar()
    else:
        total_users = user_query.with_entities(
            func.count(User.id)
        ).scalar()

    active_users = (
        db.query(
            func.count(
                func.distinct(Decision.created_by)
            )
        )
    )

    active_user_query = db.query(
        func.count(
            func.distinct(Decision.created_by)
        )
    ).select_from(Decision)

    active_user_query = apply_decision_date_filter(
        active_user_query,
        start_date,
        end_date
    )

    active_users_count = active_user_query.scalar()

    total_approvals = db.query(
        func.count(Approval.id)
    )

    if start_date:
        total_approvals = total_approvals.filter(
            Approval.created_at >= datetime.combine(
                start_date,
                datetime.min.time()
            )
        )

    if end_date:
        total_approvals = total_approvals.filter(
            Approval.created_at <
            datetime.combine(
                end_date + timedelta(days=1),
                datetime.min.time()
            )
        )

    total_approvals_count = total_approvals.scalar()

    approval_status_query = db.query(
        Approval.status,
        func.count(Approval.id)
    )

    if start_date:
        approval_status_query = approval_status_query.filter(
            Approval.created_at >= datetime.combine(
                start_date,
                datetime.min.time()
            )
        )

    if end_date:
        approval_status_query = approval_status_query.filter(
            Approval.created_at <
            datetime.combine(
                end_date + timedelta(days=1),
                datetime.min.time()
            )
        )

    approval_counts = dict(
        approval_status_query
        .group_by(Approval.status)
        .all()
    )

    return {
        "decision_statistics": {
            "total_decisions": total_decisions or 0,
            "approved_decisions": status_counts.get(
                "Approved",
                0
            ),
            "rejected_decisions": status_counts.get(
                "Rejected",
                0
            ),
            "under_review_decisions": status_counts.get(
                "Under Review",
                0
            ),
            "archived_decisions": status_counts.get(
                "Archived",
                0
            )
        },
        "user_statistics": {
            "total_users": total_users or 0,
            "active_users": active_users_count or 0
        },
        "users_by_role": dict(
            db.query(
                User.role,
                func.count(User.id)
            )
            .group_by(User.role)
            .all()
        ),
        "approval_statistics": {
            "total_approvals": total_approvals_count or 0,
            "pending_approvals": approval_counts.get(
                "Pending",
                0
            ),
            "approved_approvals": approval_counts.get(
                "Approved",
                0
            ),
            "rejected_approvals": approval_counts.get(
                "Rejected",
                0
            )
        }
    }


# ============================================================
# ADMIN DECISION ACTIVITY
# GET /dashboard/admin/decision-activity
# ============================================================

@router.get("/admin/decision-activity")
def decision_activity(
    group_by: str = Query(
        "day",
        pattern="^(day|week|month)$"
    ),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_role(
        current_user,
        ["Admin", "Administrator"]
    )

    validate_date_range(
        start_date,
        end_date
    )

    query = db.query(Decision)

    query = apply_decision_date_filter(
        query,
        start_date,
        end_date
    )

    if group_by == "day":
        group_expression = func.date(
            Decision.created_at
        )

    elif group_by == "week":
        group_expression = func.date_trunc(
            "week",
            Decision.created_at
        )

    else:
        group_expression = func.date_trunc(
            "month",
            Decision.created_at
        )

    results = (
        query.with_entities(
            group_expression.label("period"),
            func.count(Decision.id).label("count")
        )
        .group_by(group_expression)
        .order_by(group_expression)
        .all()
    )

    return {
        str(row.period): row.count
        for row in results
    }


# ============================================================
# ADMIN APPROVAL STATISTICS
# GET /dashboard/admin/approval-statistics
# ============================================================

@router.get("/admin/approval-statistics")
def approval_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_role(
        current_user,
        ["Admin", "Administrator"]
    )

    total_approvals = (
        db.query(func.count(Approval.id))
        .scalar()
    )

    completed_approvals = (
        db.query(func.count(Approval.id))
        .filter(
            Approval.status.in_(
                ["Approved", "Rejected"]
            )
        )
        .scalar()
    )

    pending_approvals = (
        db.query(func.count(Approval.id))
        .filter(
            Approval.status == "Pending"
        )
        .scalar()
    )

    average_time = (
        db.query(
            func.avg(
                func.extract(
                    "epoch",
                    Approval.completed_at -
                    Approval.created_at
                )
            )
        )
        .filter(
            Approval.completed_at.isnot(None)
        )
        .scalar()
    )

    fastest_time = (
        db.query(
            func.min(
                func.extract(
                    "epoch",
                    Approval.completed_at -
                    Approval.created_at
                )
            )
        )
        .filter(
            Approval.completed_at.isnot(None)
        )
        .scalar()
    )

    slowest_time = (
        db.query(
            func.max(
                func.extract(
                    "epoch",
                    Approval.completed_at -
                    Approval.created_at
                )
            )
        )
        .filter(
            Approval.completed_at.isnot(None)
        )
        .scalar()
    )

    completion_rate = (
        completed_approvals / total_approvals * 100
        if total_approvals
        else 0
    )

    def seconds_to_hours(value):
        if value is None:
            return None

        return round(
            float(value) / 3600,
            2
        )

    return {
        "total_approvals": total_approvals or 0,
        "completed_approvals": completed_approvals or 0,
        "pending_approvals": pending_approvals or 0,
        "completion_rate": round(
            completion_rate,
            2
        ),
        "average_approval_time_hours":
            seconds_to_hours(average_time),
        "fastest_approval_hours":
            seconds_to_hours(fastest_time),
        "slowest_approval_hours":
            seconds_to_hours(slowest_time)
    }
# ============================================================
# EMPLOYEE RECENT ACTIVITIES
# GET /dashboard/employee/recent-activities
# ============================================================

@router.get("/employee/recent-activities")
def employee_recent_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_role(
        current_user,
        ["Employee"]
    )

    activities = (
        db.query(Activity)
        .filter(
            Activity.user_id == current_user.id
        )
        .order_by(
            Activity.created_at.desc()
        )
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
# ============================================================
# MANAGER RECENT TEAM ACTIVITIES
# GET /dashboard/manager/recent-activities
# ============================================================

@router.get("/manager/recent-activities")
def manager_recent_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_role(
        current_user,
        ["Manager"]
    )

    activities = (
        db.query(Activity)
        .join(
            User,
            Activity.user_id == User.id
        )
        .filter(
            User.department == current_user.department
        )
        .order_by(
            Activity.created_at.desc()
        )
        .limit(20)
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
# ============================================================
# ADMIN RECENT SYSTEM ACTIVITIES
# GET /dashboard/admin/recent-activities
# ============================================================

@router.get("/admin/recent-activities")
def admin_recent_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_role(
        current_user,
        ["Admin", "Administrator"]
    )

    activities = (
        db.query(Activity)
        .order_by(
            Activity.created_at.desc()
        )
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