from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.models.decision import Decision
from app.models.approval import Approval
from app.models.user import User
from app.models.activity_log import ActivityLog
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# =========================================================
# ROLE HELPER
# =========================================================

def get_role(user):
    return (
        user.role.value
        if hasattr(user.role, "value")
        else user.role
    )


# =========================================================
# EMPLOYEE DASHBOARD
# =========================================================

@router.get("/employee")
def get_employee_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_decisions = (
        db.query(Decision)
        .filter(Decision.created_by == current_user.id)
        .count()
    )

    draft_decisions = (
        db.query(Decision)
        .filter(
            Decision.created_by == current_user.id,
            Decision.status == "Draft"
        )
        .count()
    )

    under_review = (
        db.query(Decision)
        .filter(
            Decision.created_by == current_user.id,
            Decision.status == "Under Review"
        )
        .count()
    )

    approved_decisions = (
        db.query(Decision)
        .filter(
            Decision.created_by == current_user.id,
            Decision.status == "Approved"
        )
        .count()
    )

    rejected_decisions = (
        db.query(Decision)
        .filter(
            Decision.created_by == current_user.id,
            Decision.status == "Rejected"
        )
        .count()
    )

    pending_reviews = (
        db.query(Approval)
        .filter(
            Approval.reviewer_id == current_user.id,
            Approval.status == "Pending"
        )
        .count()
    )

    recent_activities = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == current_user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total_decisions": total_decisions,
        "draft_decisions": draft_decisions,
        "under_review": under_review,
        "approved_decisions": approved_decisions,
        "rejected_decisions": rejected_decisions,
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


# =========================================================
# EMPLOYEE - MY DECISIONS
# =========================================================

@router.get("/employee/decisions")
def get_my_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decisions = (
        db.query(Decision)
        .filter(Decision.created_by == current_user.id)
        .order_by(Decision.updated_at.desc())
        .all()
    )

    return [
        {
            "id": d.id,
            "title": d.title,
            "category": d.category,
            "status": d.status,
            "created_at": d.created_at,
            "updated_at": d.updated_at
        }
        for d in decisions
    ]


# =========================================================
# EMPLOYEE - PENDING REVIEWS
# =========================================================

@router.get("/employee/pending-reviews")
def get_employee_pending_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    approvals = (
        db.query(Approval)
        .filter(
            Approval.reviewer_id == current_user.id,
            Approval.status == "Pending"
        )
        .order_by(Approval.created_at.desc())
        .all()
    )

    return approvals


# =========================================================
# EMPLOYEE - RECENT ACTIVITIES
# =========================================================

@router.get("/employee/recent-activities")
def get_employee_recent_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    activities = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == current_user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
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


# =========================================================
# MANAGER DASHBOARD
# =========================================================

@router.get("/manager")
def get_manager_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    role = get_role(current_user)

    if role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )

    team_filter = (
        Decision.created_by == User.id,
        User.department == current_user.department
    )

    team_decisions = (
        db.query(Decision)
        .join(User, Decision.created_by == User.id)
        .filter(User.department == current_user.department)
    )

    total_decisions = team_decisions.count()

    approved_decisions = (
        team_decisions
        .filter(Decision.status == "Approved")
        .count()
    )

    rejected_decisions = (
        team_decisions
        .filter(Decision.status == "Rejected")
        .count()
    )

    under_review = (
        team_decisions
        .filter(Decision.status == "Under Review")
        .count()
    )

    team_user_ids = (
        db.query(User.id)
        .filter(User.department == current_user.department)
        .subquery()
    )

    pending_approvals = (
        db.query(Approval)
        .filter(
            Approval.reviewer_id.in_(team_user_ids),
            Approval.status == "Pending"
        )
        .count()
    )

    return {
        "team": current_user.department,
        "team_decisions": total_decisions,
        "pending_approvals": pending_approvals,
        "approved_decisions": approved_decisions,
        "rejected_decisions": rejected_decisions,
        "under_review": under_review
    }


# =========================================================
# MANAGER - TEAM DECISIONS
# =========================================================

@router.get("/manager/team-decisions")
def get_team_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    role = get_role(current_user)

    if role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )

    decisions = (
        db.query(Decision)
        .join(User, Decision.created_by == User.id)
        .filter(User.department == current_user.department)
        .order_by(Decision.updated_at.desc())
        .all()
    )

    return [
        {
            "id": d.id,
            "title": d.title,
            "category": d.category,
            "status": d.status,
            "created_by": d.created_by,
            "created_at": d.created_at,
            "updated_at": d.updated_at
        }
        for d in decisions
    ]


# =========================================================
# MANAGER - PENDING APPROVALS
# =========================================================

@router.get("/manager/pending-approvals")
def get_manager_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    role = get_role(current_user)

    if role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )

    approvals = (
        db.query(Approval)
        .join(User, Approval.reviewer_id == User.id)
        .filter(
            User.department == current_user.department,
            Approval.status == "Pending"
        )
        .order_by(Approval.created_at.desc())
        .all()
    )

    return [
        {
            "id": approval.id,
            "decision_id": approval.decision_id,
            "approval_level": approval.approval_level,
            "assigned_reviewer": approval.reviewer_id,
            "current_status": approval.status,
            "created_at": approval.created_at
        }
        for approval in approvals
    ]


# =========================================================
# MANAGER - STATISTICS
# =========================================================

@router.get("/manager/statistics")
def get_manager_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    role = get_role(current_user)

    if role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )

    base_query = (
        db.query(Decision)
        .join(User, Decision.created_by == User.id)
        .filter(User.department == current_user.department)
    )

    return {
        "total_decisions": base_query.count(),

        "draft_decisions": base_query
            .filter(Decision.status == "Draft")
            .count(),

        "under_review": base_query
            .filter(Decision.status == "Under Review")
            .count(),

        "approved_decisions": base_query
            .filter(Decision.status == "Approved")
            .count(),

        "rejected_decisions": base_query
            .filter(Decision.status == "Rejected")
            .count(),

        "archived_decisions": base_query
            .filter(Decision.status == "Archived")
            .count()
    }


# =========================================================
# MANAGER - RECENT TEAM ACTIVITIES
# =========================================================

@router.get("/manager/recent-activities")
def get_manager_recent_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    role = get_role(current_user)

    if role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )

    team_user_ids = (
        db.query(User.id)
        .filter(User.department == current_user.department)
        .subquery()
    )

    activities = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id.in_(team_user_ids))
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
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


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@router.get("/admin")
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    role = get_role(current_user)

    if role != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    total_users = db.query(User).count()
    total_decisions = db.query(Decision).count()
    total_approvals = db.query(Approval).count()

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

    pending_approvals = (
        db.query(Approval)
        .filter(Approval.status == "Pending")
        .count()
    )

    recent_activities = (
        db.query(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "total_users": total_users,
        "total_decisions": total_decisions,
        "approved_decisions": approved_decisions,
        "rejected_decisions": rejected_decisions,
        "pending_approvals": pending_approvals,
        "total_approvals": total_approvals,
        "recent_system_activities": [
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


# =========================================================
# ADMIN - ANALYTICS
# =========================================================

@router.get("/admin/analytics")
def get_admin_analytics(
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    role = get_role(current_user)

    if role != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be greater than end_date"
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

    approval_query = db.query(Approval)

    if start_date:
        approval_query = approval_query.filter(
            Approval.created_at >= start_date
        )

    if end_date:
        approval_query = approval_query.filter(
            Approval.created_at <= end_date
        )

    total_users = db.query(User).count()

    users_by_role = (
        db.query(User.role, func.count(User.id))
        .group_by(User.role)
        .all()
    )

    return {
        "decision_statistics": {
            "total": decision_query.count(),

            "approved": decision_query
                .filter(Decision.status == "Approved")
                .count(),

            "rejected": decision_query
                .filter(Decision.status == "Rejected")
                .count(),

            "under_review": decision_query
                .filter(Decision.status == "Under Review")
                .count(),

            "archived": decision_query
                .filter(Decision.status == "Archived")
                .count()
        },

        "user_statistics": {
            "total_users": total_users,
            "users_by_role": {
                str(role): count
                for role, count in users_by_role
            }
        },

        "approval_statistics": {
            "total": approval_query.count(),

            "pending": approval_query
                .filter(Approval.status == "Pending")
                .count(),

            "approved": approval_query
                .filter(Approval.status == "Approved")
                .count(),

            "rejected": approval_query
                .filter(Approval.status == "Rejected")
                .count()
        }
    }


# =========================================================
# ADMIN - DECISION ACTIVITY
# =========================================================

# =========================================================
# ADMIN - DECISION ACTIVITY
# =========================================================

@router.get("/admin/decision-activity")
def get_decision_activity(
    period: str = Query(
        default="day",
        pattern="^(day|week|month)$"
    ),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    role = get_role(current_user)

    if role != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be greater than end_date"
        )

    # -----------------------------------------------------
    # PostgreSQL date grouping
    # -----------------------------------------------------

    if period == "day":
        date_group = func.date(Decision.created_at)

    elif period == "week":
        date_group = func.date_trunc(
            "week",
            Decision.created_at
        )

    else:
        date_group = func.date_trunc(
            "month",
            Decision.created_at
        )

    query = (
        db.query(
            date_group.label("period"),
            func.count(Decision.id).label("count")
        )
    )

    if start_date:
        query = query.filter(
            Decision.created_at >= start_date
        )

    if end_date:
        query = query.filter(
            Decision.created_at <= end_date
        )

    results = (
        query
        .group_by(date_group)
        .order_by(date_group)
        .all()
    )

    if period == "day":
        return {
            str(row.period): row.count
            for row in results
        }

    if period == "week":
        return {
            row.period.strftime("%Y-%m-%d"): row.count
            for row in results
        }

    return {
        row.period.strftime("%Y-%m"): row.count
        for row in results
    }

# =========================================================
# ADMIN - APPROVAL STATISTICS
# =========================================================
# =========================================================
# ADMIN - APPROVAL STATISTICS
# =========================================================

@router.get("/admin/approval-statistics")
def get_approval_statistics(
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    role = get_role(current_user)

    if role != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be greater than end_date"
        )

    query = db.query(Approval)

    if start_date:
        query = query.filter(
            Approval.created_at >= start_date
        )

    if end_date:
        query = query.filter(
            Approval.created_at <= end_date
        )

    total_approvals = query.count()

    completed_approvals = (
        query
        .filter(
            Approval.completed_at.isnot(None),
            Approval.status.in_(["Approved", "Rejected"])
        )
        .count()
    )

    pending_approvals = (
        query
        .filter(
            Approval.status == "Pending"
        )
        .count()
    )

    approved_approvals = (
        query
        .filter(
            Approval.status == "Approved"
        )
        .count()
    )

    rejected_approvals = (
        query
        .filter(
            Approval.status == "Rejected"
        )
        .count()
    )

    # -----------------------------------------------------
    # SQL aggregation for turnaround time
    # -----------------------------------------------------

    turnaround = (
        query
        .filter(
            Approval.completed_at.isnot(None),
            Approval.created_at.isnot(None)
        )
        .with_entities(
            func.avg(
                func.extract(
                    "epoch",
                    Approval.completed_at - Approval.created_at
                )
            ).label("average_seconds"),
            func.min(
                func.extract(
                    "epoch",
                    Approval.completed_at - Approval.created_at
                )
            ).label("fastest_seconds"),
            func.max(
                func.extract(
                    "epoch",
                    Approval.completed_at - Approval.created_at
                )
            ).label("slowest_seconds")
        )
        .first()
    )

    average_seconds = turnaround.average_seconds or 0
    fastest_seconds = turnaround.fastest_seconds or 0
    slowest_seconds = turnaround.slowest_seconds or 0

    completion_rate = (
        completed_approvals / total_approvals * 100
        if total_approvals > 0
        else 0
    )

    return {
        "total_approvals": total_approvals,
        "completed_approvals": completed_approvals,
        "pending_approvals": pending_approvals,
        "approved_approvals": approved_approvals,
        "rejected_approvals": rejected_approvals,
        "completion_rate": round(completion_rate, 2),
        "average_approval_time_hours": round(
            average_seconds / 3600, 2
        ),
        "fastest_approval_hours": round(
            fastest_seconds / 3600, 2
        ),
        "slowest_approval_hours": round(
            slowest_seconds / 3600, 2
        )
    }

# =========================================================
# ADMIN - USER ACTIVITY
# =========================================================
# =========================================================
# ADMIN - USER ACTIVITY
# =========================================================

@router.get("/admin/user-activity")
def get_admin_user_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    role = get_role(current_user)

    if role != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    activities = (
        db.query(
            ActivityLog.user_id,
            func.count(ActivityLog.id).label("activity_count")
        )
        .group_by(ActivityLog.user_id)
        .order_by(func.count(ActivityLog.id).desc())
        .all()
    )

    return {
        "active_users": len(activities),
        "users": [
            {
                "user_id": user_id,
                "activity_count": activity_count
            }
            for user_id, activity_count in activities
        ]
    }