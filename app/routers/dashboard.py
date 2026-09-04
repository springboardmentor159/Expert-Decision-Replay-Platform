from datetime import date, datetime, time, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.decision import Decision
from app.models.audit_log import AuditLog
from app.routers.auth import get_current_user


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# ============================================================
# ROLE CHECKS
# ============================================================

def check_role(current_user: User, allowed_roles: list[str]):
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this dashboard"
        )


def check_employee(current_user: User):
    check_role(current_user, ["Employee"])


def check_manager(current_user: User):
    check_role(current_user, ["Manager"])


def check_admin(current_user: User):
    check_role(current_user, ["Administrator"])


# ============================================================
# DATE FILTER HELPER
# ============================================================

def apply_date_filter(
    query,
    column,
    start_date: Optional[date],
    end_date: Optional[date]
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )

    if start_date:
        query = query.filter(
            column >= datetime.combine(start_date, time.min)
        )

    if end_date:
        query = query.filter(
            column <= datetime.combine(end_date, time.max)
        )

    return query


# ============================================================
# ACTIVITY SERIALIZER
# ============================================================

def serialize_activity(activity: AuditLog):
    return {
        "id": activity.id,
        "user_id": activity.user_id,
        "action": activity.action,
        "entity_type": activity.entity_type,
        "entity_id": activity.entity_id,
        "description": activity.description,
        "created_at": activity.created_at
    }


# ============================================================
# 1. EMPLOYEE DASHBOARD
# ============================================================

@router.get("/employee")
def get_employee_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_employee(current_user)

    base_query = db.query(Decision).filter(
        Decision.created_by == current_user.id
    )

    total_decisions = base_query.count()

    draft_decisions = base_query.filter(
        Decision.status == "Draft"
    ).count()

    under_review = base_query.filter(
        Decision.status == "Under Review"
    ).count()

    approved_decisions = base_query.filter(
        Decision.status == "Approved"
    ).count()

    rejected_decisions = base_query.filter(
        Decision.status == "Rejected"
    ).count()

    recent_activities = (
        db.query(AuditLog)
        .filter(AuditLog.user_id == current_user.id)
        .order_by(AuditLog.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "message": "Employee dashboard retrieved successfully",
        "user": {
            "id": current_user.id,
            "name": current_user.full_name,
            "email": current_user.email,
            "role": current_user.role
        },
        "statistics": {
            "total_decisions": total_decisions,
            "draft_decisions": draft_decisions,
            "under_review": under_review,
            "approved_decisions": approved_decisions,
            "rejected_decisions": rejected_decisions,
            "pending_reviews": 0
        },
        "recent_activities": [
            serialize_activity(activity)
            for activity in recent_activities
        ]
    }


# ============================================================
# 2. EMPLOYEE - MY DECISIONS
# ============================================================

@router.get("/employee/decisions")
def get_my_decisions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_employee(current_user)

    query = (
        db.query(Decision)
        .filter(Decision.created_by == current_user.id)
    )

    total = query.count()

    decisions = (
        query
        .order_by(Decision.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "message": "Employee decisions retrieved successfully",
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": [
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
    }


# ============================================================
# 3. EMPLOYEE - PENDING REVIEWS
# ============================================================

@router.get("/employee/pending-reviews")
def get_employee_pending_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_employee(current_user)

    # Approval module is not currently present in this project.
    # Therefore, no fake approval records are created.
    return {
        "message": "Pending reviews retrieved successfully",
        "total": 0,
        "items": []
    }


# ============================================================
# 4. EMPLOYEE - RECENT ACTIVITIES
# ============================================================

@router.get("/employee/recent-activities")
def get_employee_recent_activities(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_employee(current_user)

    query = (
        db.query(AuditLog)
        .filter(AuditLog.user_id == current_user.id)
    )

    total = query.count()

    activities = (
        query
        .order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "message": "Recent activities retrieved successfully",
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": [
            serialize_activity(activity)
            for activity in activities
        ]
    }


# ============================================================
# 5. MANAGER DASHBOARD
# ============================================================

@router.get("/manager")
def get_manager_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_manager(current_user)

    team_user_ids = (
        db.query(User.id)
        .filter(
            User.department == current_user.department
        )
        .subquery()
    )

    team_query = db.query(Decision).filter(
        Decision.created_by.in_(team_user_ids)
    )

    team_decisions = team_query.count()

    draft_decisions = team_query.filter(
        Decision.status == "Draft"
    ).count()

    under_review = team_query.filter(
        Decision.status == "Under Review"
    ).count()

    approved_decisions = team_query.filter(
        Decision.status == "Approved"
    ).count()

    rejected_decisions = team_query.filter(
        Decision.status == "Rejected"
    ).count()

    recent_activities = (
        db.query(AuditLog)
        .join(User, AuditLog.user_id == User.id)
        .filter(
            User.department == current_user.department
        )
        .order_by(AuditLog.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "message": "Manager dashboard retrieved successfully",
        "manager": {
            "id": current_user.id,
            "name": current_user.full_name,
            "department": current_user.department,
            "role": current_user.role
        },
        "statistics": {
            "team_decisions": team_decisions,
            "draft_decisions": draft_decisions,
            "under_review": under_review,
            "approved_decisions": approved_decisions,
            "rejected_decisions": rejected_decisions,
            "pending_approvals": 0
        },
        "recent_team_activities": [
            serialize_activity(activity)
            for activity in recent_activities
        ]
    }


# ============================================================
# 6. MANAGER - TEAM DECISIONS
# ============================================================

@router.get("/manager/team-decisions")
def get_manager_team_decisions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort: str = Query(
        "created_at",
        pattern="^(created_at|updated_at|title)$"
    ),
    order: str = Query(
        "desc",
        pattern="^(asc|desc)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_manager(current_user)

    team_user_ids = (
        db.query(User.id)
        .filter(
            User.department == current_user.department
        )
        .subquery()
    )

    query = db.query(Decision).filter(
        Decision.created_by.in_(team_user_ids)
    )

    total = query.count()

    if sort == "created_at":
        sort_column = Decision.created_at
    elif sort == "updated_at":
        sort_column = Decision.updated_at
    else:
        sort_column = Decision.title

    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    decisions = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "message": "Team decisions retrieved successfully",
        "department": current_user.department,
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": [
            {
                "id": decision.id,
                "title": decision.title,
                "category": decision.category,
                "status": decision.status,
                "created_by": decision.created_by,
                "created_at": decision.created_at,
                "updated_at": decision.updated_at
            }
            for decision in decisions
        ]
    }


# ============================================================
# 7. MANAGER - PENDING APPROVALS
# ============================================================

@router.get("/manager/pending-approvals")
def get_manager_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_manager(current_user)

    return {
        "message": "Pending approvals retrieved successfully",
        "total": 0,
        "items": []
    }


# ============================================================
# 8. MANAGER - STATISTICS
# ============================================================

@router.get("/manager/statistics")
def get_manager_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_manager(current_user)

    team_user_ids = (
        db.query(User.id)
        .filter(
            User.department == current_user.department
        )
        .subquery()
    )

    query = db.query(Decision).filter(
        Decision.created_by.in_(team_user_ids)
    )

    return {
        "department": current_user.department,
        "total_decisions": query.count(),
        "draft_decisions": query.filter(
            Decision.status == "Draft"
        ).count(),
        "under_review": query.filter(
            Decision.status == "Under Review"
        ).count(),
        "approved_decisions": query.filter(
            Decision.status == "Approved"
        ).count(),
        "rejected_decisions": query.filter(
            Decision.status == "Rejected"
        ).count(),
        "archived_decisions": query.filter(
            Decision.status == "Archived"
        ).count(),
        "pending_approvals": 0
    }


# ============================================================
# 9. ADMIN DASHBOARD
# ============================================================

@router.get("/admin")
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_admin(current_user)

    total_users = db.query(User).count()
    total_decisions = db.query(Decision).count()
    total_activities = db.query(AuditLog).count()

    approved = db.query(Decision).filter(
        Decision.status == "Approved"
    ).count()

    rejected = db.query(Decision).filter(
        Decision.status == "Rejected"
    ).count()

    under_review = db.query(Decision).filter(
        Decision.status == "Under Review"
    ).count()

    archived = db.query(Decision).filter(
        Decision.status == "Archived"
    ).count()

    recent_activities = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "message": "Admin dashboard retrieved successfully",
        "system_statistics": {
            "total_users": total_users,
            "total_decisions": total_decisions,
            "total_activities": total_activities,
            "approved_decisions": approved,
            "rejected_decisions": rejected,
            "under_review": under_review,
            "archived_decisions": archived
        },
        "recent_system_activities": [
            serialize_activity(activity)
            for activity in recent_activities
        ]
    }


# ============================================================
# 10. ADMIN - ANALYTICS
# ============================================================

@router.get("/admin/analytics")
def get_admin_analytics(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_admin(current_user)

    decision_query = db.query(Decision)

    decision_query = apply_date_filter(
        decision_query,
        Decision.created_at,
        start_date,
        end_date
    )

    total_decisions = decision_query.count()

    approved = decision_query.filter(
        Decision.status == "Approved"
    ).count()

    rejected = decision_query.filter(
        Decision.status == "Rejected"
    ).count()

    under_review = decision_query.filter(
        Decision.status == "Under Review"
    ).count()

    archived = decision_query.filter(
        Decision.status == "Archived"
    ).count()

    draft = decision_query.filter(
        Decision.status == "Draft"
    ).count()

    total_users = db.query(User).count()

    users_by_role = (
        db.query(
            User.role,
            func.count(User.id)
        )
        .group_by(User.role)
        .all()
    )

    role_statistics = {
        role: count
        for role, count in users_by_role
    }

    activity_query = db.query(AuditLog)

    activity_query = apply_date_filter(
        activity_query,
        AuditLog.created_at,
        start_date,
        end_date
    )

    total_activities = activity_query.count()

    return {
        "message": "Admin analytics retrieved successfully",
        "date_range": {
            "start_date": start_date,
            "end_date": end_date
        },
        "decision_statistics": {
            "total_decisions": total_decisions,
            "draft_decisions": draft,
            "under_review": under_review,
            "approved_decisions": approved,
            "rejected_decisions": rejected,
            "archived_decisions": archived
        },
        "user_statistics": {
            "total_users": total_users,
            "users_by_role": role_statistics
        },
        "activity_statistics": {
            "total_activities": total_activities
        },
        "approval_statistics": {
            "total_approvals": 0,
            "pending_approvals": 0,
            "completed_approvals": 0,
            "completion_rate": 0
        }
    }


# ============================================================
# 11. ADMIN - DECISION ACTIVITY
# ============================================================

@router.get("/admin/decision-activity")
def get_decision_activity(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_admin(current_user)

    query = db.query(
        func.date(Decision.created_at).label("activity_date"),
        func.count(Decision.id).label("decision_count")
    )

    if start_date:
        query = query.filter(
            Decision.created_at >= datetime.combine(
                start_date,
                time.min
            )
        )

    if end_date:
        query = query.filter(
            Decision.created_at <= datetime.combine(
                end_date,
                time.max
            )
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date"
        )

    results = (
        query
        .group_by(func.date(Decision.created_at))
        .order_by(func.date(Decision.created_at))
        .all()
    )

    return {
        "message": "Decision activity retrieved successfully",
        "items": [
            {
                "date": str(activity_date),
                "count": decision_count
            }
            for activity_date, decision_count in results
        ]
    }


# ============================================================
# 12. ADMIN - APPROVAL STATISTICS
# ============================================================

@router.get("/admin/approval-statistics")
def get_approval_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_admin(current_user)

    # Approval table/model is not currently present.
    return {
        "message": "Approval statistics retrieved successfully",
        "total_approvals": 0,
        "completed_approvals": 0,
        "pending_approvals": 0,
        "completion_rate": 0,
        "average_approval_time_hours": 0,
        "fastest_approval_time_hours": 0,
        "slowest_approval_time_hours": 0
    }


# ============================================================
# 13. ADMIN - USER ACTIVITY
# ============================================================

@router.get("/admin/user-activity")
def get_user_activity(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_admin(current_user)

    query = (
        db.query(
            AuditLog.user_id,
            func.count(AuditLog.id).label("activity_count")
        )
    )

    query = apply_date_filter(
        query,
        AuditLog.created_at,
        start_date,
        end_date
    )

    query = (
        query
        .group_by(AuditLog.user_id)
        .order_by(func.count(AuditLog.id).desc())
    )

    total = query.count()

    results = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []

    for user_id, activity_count in results:
        user = db.query(User).filter(
            User.id == user_id
        ).first()

        items.append({
            "user_id": user_id,
            "user_name": user.full_name if user else None,
            "email": user.email if user else None,
            "activity_count": activity_count
        })

    return {
        "message": "User activity retrieved successfully",
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": items
    }


# ============================================================
# 14. ACTIVITY API
# ============================================================

@router.get("/activities")
def get_activities(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Administrators can see organization-wide activity.
    # Other users can only see their own activities.
    if current_user.role == "Administrator":
        query = db.query(AuditLog)

        if user_id is not None:
            query = query.filter(
                AuditLog.user_id == user_id
            )
    else:
        query = db.query(AuditLog).filter(
            AuditLog.user_id == current_user.id
        )

    if action:
        query = query.filter(
            AuditLog.action == action
        )

    if entity_type:
        query = query.filter(
            AuditLog.entity_type == entity_type
        )

    if entity_id is not None:
        query = query.filter(
            AuditLog.entity_id == entity_id
        )

    query = apply_date_filter(
        query,
        AuditLog.created_at,
        start_date,
        end_date
    )

    total = query.count()

    activities = (
        query
        .order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "message": "Activities retrieved successfully",
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": [
            serialize_activity(activity)
            for activity in activities
        ]
    }


# ============================================================
# EXISTING DASHBOARD ENDPOINT
# ============================================================

@router.get("/")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_decisions = db.query(Decision).count()

    return {
        "message": "Dashboard data retrieved successfully",
        "total_decisions": total_decisions
    }