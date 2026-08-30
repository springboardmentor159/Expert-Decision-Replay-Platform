from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.core.enums import UserRole, DecisionStatus

from app.models.user import User
from app.models.decision import Decision
from app.models.activity_log import ActivityLog
from app.models.comment import Comment
from app.models.alternative import Alternative
from app.models.discussion_thread import DiscussionThread


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# =========================================================
# AUTHORIZATION HELPERS
# =========================================================

def require_manager(
    current_user: User
):
    """
    Allow only Manager users.
    """

    if current_user.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )

    return current_user


def require_admin(
    current_user: User
):
    """
    Allow only Administrator users.
    """

    if current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required"
        )

    return current_user


# =========================================================
# DATE RANGE HELPER
# =========================================================

def validate_date_range(
    start_date: Optional[datetime],
    end_date: Optional[datetime]
):
    """
    Validate dashboard date range.
    """

    if start_date and end_date:

        if start_date > end_date:

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="start_date cannot be after end_date"
            )


# =========================================================
# EMPLOYEE DASHBOARD
# =========================================================

@router.get("/employee")
def employee_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Employee dashboard.

    Shows statistics for the authenticated user only.
    """

    user_id = current_user.id

    # -----------------------------------------------------
    # TOTAL MY DECISIONS
    # -----------------------------------------------------

    total_decisions = db.query(
        func.count(Decision.id)
    ).filter(
        Decision.created_by == user_id
    ).scalar() or 0

    # -----------------------------------------------------
    # DRAFT
    # -----------------------------------------------------

    draft_decisions = db.query(
        func.count(Decision.id)
    ).filter(
        Decision.created_by == user_id,
        Decision.status == DecisionStatus.DRAFT
    ).scalar() or 0

    # -----------------------------------------------------
    # UNDER REVIEW
    # -----------------------------------------------------

    under_review = db.query(
        func.count(Decision.id)
    ).filter(
        Decision.created_by == user_id,
        Decision.status == DecisionStatus.UNDER_REVIEW
    ).scalar() or 0

    # -----------------------------------------------------
    # APPROVED
    # -----------------------------------------------------

    approved_decisions = db.query(
        func.count(Decision.id)
    ).filter(
        Decision.created_by == user_id,
        Decision.status == DecisionStatus.APPROVED
    ).scalar() or 0

    # -----------------------------------------------------
    # REJECTED
    # -----------------------------------------------------

    rejected_decisions = db.query(
        func.count(Decision.id)
    ).filter(
        Decision.created_by == user_id,
        Decision.status == DecisionStatus.REJECTED
    ).scalar() or 0

    # -----------------------------------------------------
    # PENDING REVIEWS
    #
    # Current project does not have an Approval table.
    # This remains 0 until Sprint 8 approval workflow exists.
    # -----------------------------------------------------

    pending_reviews = 0

    # -----------------------------------------------------
    # RECENT ACTIVITIES
    # -----------------------------------------------------

    activities = db.query(
        ActivityLog
    ).filter(
        ActivityLog.user_id == user_id
    ).order_by(
        ActivityLog.created_at.desc()
    ).limit(
        10
    ).all()

    recent_activities = [
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

    return {
        "user": {
            "id": current_user.id,
            "name": current_user.full_name,
            "email": current_user.email,
            "role": current_user.role
        },
        "total_decisions": total_decisions,
        "draft_decisions": draft_decisions,
        "under_review": under_review,
        "approved_decisions": approved_decisions,
        "rejected_decisions": rejected_decisions,
        "pending_reviews": pending_reviews,
        "recent_activities": recent_activities
    }


# =========================================================
# EMPLOYEE - MY DECISIONS
# =========================================================

@router.get("/employee/decisions")
def employee_decisions(
    page: int = Query(
        1,
        ge=1
    ),

    page_size: int = Query(
        20,
        ge=1,
        le=100
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    """
    Return decisions created by the authenticated employee.
    """

    query = db.query(
        Decision
    ).filter(
        Decision.created_by == current_user.id
    )

    total = query.count()

    offset = (
        page - 1
    ) * page_size

    decisions = query.order_by(
        Decision.created_at.desc()
    ).offset(
        offset
    ).limit(
        page_size
    ).all()

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "count": len(decisions),
        "decisions": [
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


# =========================================================
# EMPLOYEE - RECENT ACTIVITIES
# =========================================================

@router.get("/employee/recent-activities")
def employee_recent_activities(
    limit: int = Query(
        20,
        ge=1,
        le=100
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    """
    Return recent activities performed by the authenticated user.
    """

    activities = db.query(
        ActivityLog
    ).filter(
        ActivityLog.user_id == current_user.id
    ).order_by(
        ActivityLog.created_at.desc()
    ).limit(
        limit
    ).all()

    return {
        "count": len(activities),
        "activities": [
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
    }


# =========================================================
# MANAGER DASHBOARD
# =========================================================

@router.get("/manager")
def manager_dashboard(
    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    """
    Manager dashboard.

    Since the current User model does not have a team_id,
    the manager's department is used as the team boundary.
    """

    require_manager(current_user)

    # -----------------------------------------------------
    # TEAM MEMBERS
    #
    # Current schema has department but no team_id.
    # Therefore users in the same department are treated
    # as the manager's team.
    # -----------------------------------------------------

    team_user_ids_query = db.query(
        User.id
    )

    if current_user.department:

        team_user_ids_query = team_user_ids_query.filter(
            User.department == current_user.department
        )

    team_user_ids = [
        row[0]
        for row in team_user_ids_query.all()
    ]

    # -----------------------------------------------------
    # TEAM DECISIONS
    # -----------------------------------------------------

    team_decision_query = db.query(
        Decision
    ).filter(
        Decision.created_by.in_(team_user_ids)
    )

    team_decisions = team_decision_query.count()

    # -----------------------------------------------------
    # APPROVED
    # -----------------------------------------------------

    approved_decisions = team_decision_query.filter(
        Decision.status == DecisionStatus.APPROVED
    ).count()

    # -----------------------------------------------------
    # REJECTED
    # -----------------------------------------------------

    rejected_decisions = team_decision_query.filter(
        Decision.status == DecisionStatus.REJECTED
    ).count()

    # -----------------------------------------------------
    # UNDER REVIEW
    # -----------------------------------------------------

    under_review = team_decision_query.filter(
        Decision.status == DecisionStatus.UNDER_REVIEW
    ).count()

    # -----------------------------------------------------
    # PENDING APPROVALS
    #
    # No Approval table exists currently.
    # -----------------------------------------------------

    pending_approvals = 0

    # -----------------------------------------------------
    # RECENT TEAM ACTIVITIES
    # -----------------------------------------------------

    team_activities = db.query(
        ActivityLog
    ).filter(
        ActivityLog.user_id.in_(team_user_ids)
    ).order_by(
        ActivityLog.created_at.desc()
    ).limit(
        20
    ).all()

    recent_team_activities = [
        {
            "id": activity.id,
            "user_id": activity.user_id,
            "action": activity.action,
            "entity_type": activity.entity_type,
            "entity_id": activity.entity_id,
            "description": activity.description,
            "created_at": activity.created_at
        }
        for activity in team_activities
    ]

    return {
        "manager": {
            "id": current_user.id,
            "name": current_user.full_name,
            "department": current_user.department,
            "role": current_user.role
        },
        "team_decisions": team_decisions,
        "pending_approvals": pending_approvals,
        "approved_decisions": approved_decisions,
        "rejected_decisions": rejected_decisions,
        "under_review": under_review,
        "recent_team_activities": recent_team_activities
    }


# =========================================================
# MANAGER - TEAM DECISIONS
# =========================================================

@router.get("/manager/team-decisions")
def manager_team_decisions(
    page: int = Query(
        1,
        ge=1
    ),

    page_size: int = Query(
        20,
        ge=1,
        le=100
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    """
    Return decisions belonging to the manager's department/team.
    """

    require_manager(current_user)

    # -----------------------------------------------------
    # FIND TEAM MEMBERS
    # -----------------------------------------------------

    team_user_ids_query = db.query(
        User.id
    )

    if current_user.department:

        team_user_ids_query = team_user_ids_query.filter(
            User.department == current_user.department
        )

    team_user_ids = [
        row[0]
        for row in team_user_ids_query.all()
    ]

    # -----------------------------------------------------
    # DECISIONS
    # -----------------------------------------------------

    query = db.query(
        Decision
    ).filter(
        Decision.created_by.in_(team_user_ids)
    )

    total = query.count()

    offset = (
        page - 1
    ) * page_size

    decisions = query.order_by(
        Decision.created_at.desc()
    ).offset(
        offset
    ).limit(
        page_size
    ).all()

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "count": len(decisions),
        "decisions": [
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


# =========================================================
# MANAGER - PENDING APPROVALS
# =========================================================

@router.get("/manager/pending-approvals")
def manager_pending_approvals(
    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    """
    Pending approvals endpoint.

    The current project does not contain an Approval model,
    so this endpoint currently returns an empty list.

    It can later be connected directly to the Sprint 8
    Approval Workflow without creating another mechanism.
    """

    require_manager(current_user)

    return {
        "count": 0,
        "message": (
            "Approval workflow is not currently available "
            "in the database."
        ),
        "pending_approvals": []
    }


# =========================================================
# MANAGER - STATISTICS
# =========================================================

@router.get("/manager/statistics")
def manager_statistics(
    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    """
    Team decision statistics.
    """

    require_manager(current_user)

    # -----------------------------------------------------
    # TEAM MEMBERS
    # -----------------------------------------------------

    team_user_ids_query = db.query(
        User.id
    )

    if current_user.department:

        team_user_ids_query = team_user_ids_query.filter(
            User.department == current_user.department
        )

    team_user_ids = [
        row[0]
        for row in team_user_ids_query.all()
    ]

    # -----------------------------------------------------
    # BASE QUERY
    # -----------------------------------------------------

    query = db.query(
        Decision
    ).filter(
        Decision.created_by.in_(team_user_ids)
    )

    total_decisions = query.count()

    draft_decisions = query.filter(
        Decision.status == DecisionStatus.DRAFT
    ).count()

    under_review = query.filter(
        Decision.status == DecisionStatus.UNDER_REVIEW
    ).count()

    approved_decisions = query.filter(
        Decision.status == DecisionStatus.APPROVED
    ).count()

    rejected_decisions = query.filter(
        Decision.status == DecisionStatus.REJECTED
    ).count()

    archived_decisions = query.filter(
        Decision.status == DecisionStatus.ARCHIVED
    ).count()

    return {
        "total_decisions": total_decisions,
        "draft_decisions": draft_decisions,
        "under_review": under_review,
        "approved_decisions": approved_decisions,
        "rejected_decisions": rejected_decisions,
        "archived_decisions": archived_decisions,
        "pending_approvals": 0
    }


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@router.get("/admin")
def admin_dashboard(
    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    """
    Organization-wide administrator dashboard.
    """

    require_admin(current_user)

    # -----------------------------------------------------
    # USERS
    # -----------------------------------------------------

    total_users = db.query(
        func.count(User.id)
    ).scalar() or 0

    # -----------------------------------------------------
    # DECISIONS
    # -----------------------------------------------------

    total_decisions = db.query(
        func.count(Decision.id)
    ).scalar() or 0

    approved_decisions = db.query(
        func.count(Decision.id)
    ).filter(
        Decision.status == DecisionStatus.APPROVED
    ).scalar() or 0

    rejected_decisions = db.query(
        func.count(Decision.id)
    ).filter(
        Decision.status == DecisionStatus.REJECTED
    ).scalar() or 0

    under_review = db.query(
        func.count(Decision.id)
    ).filter(
        Decision.status == DecisionStatus.UNDER_REVIEW
    ).scalar() or 0

    draft_decisions = db.query(
        func.count(Decision.id)
    ).filter(
        Decision.status == DecisionStatus.DRAFT
    ).scalar() or 0

    archived_decisions = db.query(
        func.count(Decision.id)
    ).filter(
        Decision.status == DecisionStatus.ARCHIVED
    ).scalar() or 0

    # -----------------------------------------------------
    # RECENT SYSTEM ACTIVITIES
    # -----------------------------------------------------

    activities = db.query(
        ActivityLog
    ).order_by(
        ActivityLog.created_at.desc()
    ).limit(
        20
    ).all()

    recent_activities = [
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

    return {
        "total_users": total_users,
        "total_decisions": total_decisions,
        "decision_statistics": {
            "draft": draft_decisions,
            "under_review": under_review,
            "approved": approved_decisions,
            "rejected": rejected_decisions,
            "archived": archived_decisions
        },
        "approval_statistics": {
            "total_approvals": 0,
            "pending_approvals": 0,
            "approved_approvals": 0,
            "rejected_approvals": 0,
            "completion_rate": 0
        },
        "recent_system_activities": recent_activities
    }


# =========================================================
# ADMIN ANALYTICS
# =========================================================

@router.get("/admin/analytics")
def admin_analytics(
    start_date: Optional[datetime] = Query(
        None,
        description="Analytics start date"
    ),

    end_date: Optional[datetime] = Query(
        None,
        description="Analytics end date"
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    """
    Organization-level analytics with optional date filtering.
    """

    require_admin(current_user)

    validate_date_range(
        start_date,
        end_date
    )

    # -----------------------------------------------------
    # DECISION QUERY
    # -----------------------------------------------------

    decision_query = db.query(
        Decision
    )

    if start_date:

        decision_query = decision_query.filter(
            Decision.created_at >= start_date
        )

    if end_date:

        decision_query = decision_query.filter(
            Decision.created_at <= end_date
        )

    # -----------------------------------------------------
    # DECISION STATISTICS
    # -----------------------------------------------------

    total_decisions = decision_query.count()

    approved_decisions = decision_query.filter(
        Decision.status == DecisionStatus.APPROVED
    ).count()

    rejected_decisions = decision_query.filter(
        Decision.status == DecisionStatus.REJECTED
    ).count()

    under_review = decision_query.filter(
        Decision.status == DecisionStatus.UNDER_REVIEW
    ).count()

    archived_decisions = decision_query.filter(
        Decision.status == DecisionStatus.ARCHIVED
    ).count()

    draft_decisions = decision_query.filter(
        Decision.status == DecisionStatus.DRAFT
    ).count()

    # -----------------------------------------------------
    # USER STATISTICS
    # -----------------------------------------------------

    total_users = db.query(
        func.count(User.id)
    ).scalar() or 0

    users_by_role = db.query(
        User.role,
        func.count(User.id)
    ).group_by(
        User.role
    ).all()

    role_statistics = {
        str(role.value): count
        for role, count in users_by_role
    }

    # -----------------------------------------------------
    # ACTIVE USERS
    #
    # A user is considered active if they have performed
    # an activity during the selected period.
    # -----------------------------------------------------

    activity_query = db.query(
        ActivityLog
    )

    if start_date:

        activity_query = activity_query.filter(
            ActivityLog.created_at >= start_date
        )

    if end_date:

        activity_query = activity_query.filter(
            ActivityLog.created_at <= end_date
        )

    active_users = activity_query.with_entities(
        func.count(
            func.distinct(ActivityLog.user_id)
        )
    ).scalar() or 0

    # -----------------------------------------------------
    # APPROVAL STATISTICS
    #
    # No Approval table exists currently.
    # -----------------------------------------------------

    approval_statistics = {
        "total_approvals": 0,
        "pending_approvals": 0,
        "approved_approvals": 0,
        "rejected_approvals": 0,
        "completion_rate": 0
    }

    return {
        "date_range": {
            "start_date": start_date,
            "end_date": end_date
        },
        "decision_statistics": {
            "total_decisions": total_decisions,
            "draft_decisions": draft_decisions,
            "under_review": under_review,
            "approved_decisions": approved_decisions,
            "rejected_decisions": rejected_decisions,
            "archived_decisions": archived_decisions
        },
        "user_statistics": {
            "total_users": total_users,
            "active_users": active_users,
            "users_by_role": role_statistics
        },
        "approval_statistics": approval_statistics
    }


# =========================================================
# ADMIN - DECISION ACTIVITY
# =========================================================

@router.get("/admin/decision-activity")
def admin_decision_activity(
    start_date: Optional[datetime] = Query(
        None
    ),

    end_date: Optional[datetime] = Query(
        None
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    """
    Count decisions created per day using PostgreSQL GROUP BY.
    """

    require_admin(current_user)

    validate_date_range(
        start_date,
        end_date
    )

    query = db.query(
        func.date(
            Decision.created_at
        ).label("activity_date"),
        func.count(
            Decision.id
        ).label("decision_count")
    )

    if start_date:

        query = query.filter(
            Decision.created_at >= start_date
        )

    if end_date:

        query = query.filter(
            Decision.created_at <= end_date
        )

    results = query.group_by(
        func.date(Decision.created_at)
    ).order_by(
        func.date(Decision.created_at)
    ).all()

    return {
        "activity": {
            str(row.activity_date): row.decision_count
            for row in results
        }
    }


# =========================================================
# ADMIN - APPROVAL STATISTICS
# =========================================================

@router.get("/admin/approval-statistics")
def admin_approval_statistics(
    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    """
    Approval performance statistics.

    Currently returns zero because the project does not
    contain the Sprint 8 Approval model/table.
    """

    require_admin(current_user)

    return {
        "total_approvals": 0,
        "completed_approvals": 0,
        "pending_approvals": 0,
        "approved_approvals": 0,
        "rejected_approvals": 0,
        "completion_rate": 0,
        "average_approval_time_hours": 0,
        "fastest_approval_time_hours": 0,
        "slowest_approval_time_hours": 0,
        "message": (
            "Approval statistics will be connected to "
            "the Sprint 8 approval workflow when available."
        )
    }


# =========================================================
# ADMIN - USER ACTIVITY
# =========================================================

@router.get("/admin/user-activity")
def admin_user_activity(
    days: int = Query(
        30,
        ge=1,
        le=365
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    """
    Organization-level active user information.
    """

    require_admin(current_user)

    since = datetime.utcnow() - timedelta(
        days=days
    )

    results = db.query(
        ActivityLog.user_id,
        func.count(ActivityLog.id).label(
            "activity_count"
        ),
        func.max(ActivityLog.created_at).label(
            "last_activity"
        )
    ).filter(
        ActivityLog.created_at >= since
    ).group_by(
        ActivityLog.user_id
    ).order_by(
        func.count(ActivityLog.id).desc()
    ).all()

    activity = []

    for row in results:

        user = db.query(
            User
        ).filter(
            User.id == row.user_id
        ).first()

        if user:

            activity.append({
                "user_id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
                "activity_count": row.activity_count,
                "last_activity": row.last_activity
            })

    return {
        "period_days": days,
        "active_users": len(activity),
        "users": activity
    }


# =========================================================
# ACTIVITIES
# =========================================================

@router.get("/activities")
def get_activities(
    user_id: Optional[int] = Query(
        None,
        ge=1
    ),

    action: Optional[str] = Query(
        None,
        min_length=1
    ),

    entity_type: Optional[str] = Query(
        None,
        min_length=1
    ),

    start_date: Optional[datetime] = Query(
        None
    ),

    end_date: Optional[datetime] = Query(
        None
    ),

    page: int = Query(
        1,
        ge=1
    ),

    page_size: int = Query(
        20,
        ge=1,
        le=100
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    """
    Activity log retrieval.

    Administrators can query organization-wide activities.

    Normal users can only retrieve their own activities.
    """

    validate_date_range(
        start_date,
        end_date
    )

    query = db.query(
        ActivityLog
    )

    # -----------------------------------------------------
    # AUTHORIZATION
    # -----------------------------------------------------

    if current_user.role != UserRole.ADMINISTRATOR:

        query = query.filter(
            ActivityLog.user_id == current_user.id
        )

    else:

        if user_id:

            # Verify requested user exists.

            requested_user = db.query(
                User
            ).filter(
                User.id == user_id
            ).first()

            if not requested_user:

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            query = query.filter(
                ActivityLog.user_id == user_id
            )

    # -----------------------------------------------------
    # ACTION FILTER
    # -----------------------------------------------------

    if action:

        query = query.filter(
            ActivityLog.action.ilike(
                f"%{action}%"
            )
        )

    # -----------------------------------------------------
    # ENTITY FILTER
    # -----------------------------------------------------

    if entity_type:

        query = query.filter(
            ActivityLog.entity_type.ilike(
                f"%{entity_type}%"
            )
        )

    # -----------------------------------------------------
    # DATE FILTER
    # -----------------------------------------------------

    if start_date:

        query = query.filter(
            ActivityLog.created_at >= start_date
        )

    if end_date:

        query = query.filter(
            ActivityLog.created_at <= end_date
        )

    # -----------------------------------------------------
    # COUNT
    # -----------------------------------------------------

    total = query.count()

    # -----------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------

    offset = (
        page - 1
    ) * page_size

    activities = query.order_by(
        ActivityLog.created_at.desc()
    ).offset(
        offset
    ).limit(
        page_size
    ).all()

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "count": len(activities),
        "activities": [
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
    }