from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User

from app.db.database import get_db

from app.models.decision import Decision
from app.models.approval import Approval
from app.models.activity_log import ActivityLog

from app.core.dependencies import require_role

from app.schemas.dashboard import (
    EmployeeDashboardResponse,
    EmployeeDecisionSummary,
    EmployeePendingReview,
    EmployeeActivitySummary,
    ManagerDashboardResponse,
    ManagerDecisionSummary,
    ManagerPendingApproval,
    ManagerStatisticsResponse,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


# ============================================================
# EMPLOYEE DASHBOARD
# ============================================================

@router.get(
    "/employee",
    response_model=EmployeeDashboardResponse,
)
def get_employee_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_role("Employee")
    ),
):
    user_id = int(current_user["sub"])

    my_decisions = (
        db.query(Decision)
        .filter(Decision.created_by == user_id)
        .count()
    )

    draft_decisions = (
        db.query(Decision)
        .filter(
            Decision.created_by == user_id,
            Decision.status == "Draft",
        )
        .count()
    )

    decisions_under_review = (
        db.query(Decision)
        .filter(
            Decision.created_by == user_id,
            Decision.status == "Under Review",
        )
        .count()
    )

    approved_decisions = (
        db.query(Decision)
        .filter(
            Decision.created_by == user_id,
            Decision.status == "Approved",
        )
        .count()
    )

    rejected_decisions = (
        db.query(Decision)
        .filter(
            Decision.created_by == user_id,
            Decision.status == "Rejected",
        )
        .count()
    )

    pending_reviews = (
        db.query(Approval)
        .join(
            Decision,
            Approval.decision_id == Decision.id
        )
        .filter(
            Decision.created_by == user_id,
            Approval.status == "Pending",
        )
        .count()
    )

    recent_activities = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == user_id)
        .order_by(ActivityLog.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "my_decisions": my_decisions,
        "draft_decisions": draft_decisions,
        "decisions_under_review": decisions_under_review,
        "approved_decisions": approved_decisions,
        "rejected_decisions": rejected_decisions,
        "pending_reviews": pending_reviews,
        "recent_activities": recent_activities,
    }


# ============================================================
# EMPLOYEE DECISION LIST
# ============================================================

@router.get(
    "/employee/decisions",
    response_model=list[EmployeeDecisionSummary],
)
def get_employee_decisions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_role("Employee")
    ),
):
    user_id = int(current_user["sub"])

    decisions = (
        db.query(Decision)
        .filter(Decision.created_by == user_id)
        .order_by(Decision.created_at.desc())
        .all()
    )

    return decisions


# ============================================================
# EMPLOYEE PENDING REVIEWS
# ============================================================

@router.get(
    "/employee/recent-activities",
    response_model=list[EmployeeActivitySummary],
)
def get_employee_recent_activities(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_role("Employee")
    ),
):
    user_id = int(current_user["sub"])

    activities = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == user_id)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
        .all()
    )

    return activities

# ============================================================
# MANAGER DASHBOARD
# ============================================================

@router.get(
    "/manager",
    response_model=ManagerDashboardResponse,
)
def get_manager_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_role("Manager")
    ),
):
    manager_id = int(current_user["sub"])

    # Get manager's department
    manager = (
        db.query(User)
        .filter(User.id == manager_id)
        .first()
    )

    if not manager:
        raise HTTPException(
            status_code=404,
            detail="Manager not found"
        )

    department = manager.department

    # Team decisions = decisions created by users
    # belonging to the manager's department
    team_decisions = (
        db.query(Decision)
        .join(User, Decision.created_by == User.id)
        .filter(User.department == department)
        .count()
    )

    pending_approvals = (
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
            User.department == department,
            Approval.status == "Pending",
        )
        .count()
    )

    approved_decisions = (
        db.query(Decision)
        .join(User, Decision.created_by == User.id)
        .filter(
            User.department == department,
            Decision.status == "Approved",
        )
        .count()
    )

    rejected_decisions = (
        db.query(Decision)
        .join(User, Decision.created_by == User.id)
        .filter(
            User.department == department,
            Decision.status == "Rejected",
        )
        .count()
    )

    under_review = (
        db.query(Decision)
        .join(User, Decision.created_by == User.id)
        .filter(
            User.department == department,
            Decision.status == "Under Review",
        )
        .count()
    )

    recent_team_activities = (
        db.query(ActivityLog)
        .join(
            User,
            ActivityLog.user_id == User.id
        )
        .filter(User.department == department)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "team_decisions": team_decisions,
        "pending_approvals": pending_approvals,
        "approved_decisions": approved_decisions,
        "rejected_decisions": rejected_decisions,
        "under_review": under_review,
        "recent_team_activities": recent_team_activities,
    }


# ============================================================
# MANAGER TEAM DECISIONS
# ============================================================

@router.get(
    "/manager/team-decisions",
    response_model=list[ManagerDecisionSummary],
)
def get_manager_team_decisions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_role("Manager")
    ),
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
            detail="Manager not found"
        )

    decisions = (
        db.query(Decision)
        .join(User, Decision.created_by == User.id)
        .filter(User.department == manager.department)
        .order_by(Decision.created_at.desc())
        .all()
    )

    return decisions


# ============================================================
# MANAGER PENDING APPROVALS
# ============================================================

@router.get(
    "/manager/pending-approvals",
    response_model=list[ManagerPendingApproval],
)
def get_manager_pending_approvals(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_role("Manager")
    ),
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
            detail="Manager not found"
        )

    approvals = (
        db.query(
            Approval,
            Decision.title,
        )
        .join(
            Decision,
            Approval.decision_id == Decision.id
        )
        .join(
            User,
            Decision.created_by == User.id
        )
        .filter(
            User.department == manager.department,
            Approval.status == "Pending",
        )
        .order_by(Approval.created_at.desc())
        .all()
    )

    return [
        {
            "id": approval.id,
            "decision_id": approval.decision_id,
            "decision_title": decision_title,
            "approval_level": approval.approval_level,
            "assigned_to": approval.assigned_to,
            "status": approval.status,
            "created_at": approval.created_at,
        }
        for approval, decision_title in approvals
    ]


# ============================================================
# MANAGER STATISTICS
# ============================================================

@router.get(
    "/manager/statistics",
    response_model=ManagerStatisticsResponse,
)
def get_manager_statistics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_role("Manager")
    ),
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
            detail="Manager not found"
        )

    department = manager.department

    base_query = (
        db.query(Decision)
        .join(User, Decision.created_by == User.id)
        .filter(User.department == department)
    )

    total_decisions = base_query.count()

    draft_decisions = (
        base_query
        .filter(Decision.status == "Draft")
        .count()
    )

    under_review = (
        base_query
        .filter(Decision.status == "Under Review")
        .count()
    )

    approved_decisions = (
        base_query
        .filter(Decision.status == "Approved")
        .count()
    )

    rejected_decisions = (
        base_query
        .filter(Decision.status == "Rejected")
        .count()
    )

    archived_decisions = (
        base_query
        .filter(Decision.status == "Archived")
        .count()
    )

    return {
        "total_decisions": total_decisions,
        "draft_decisions": draft_decisions,
        "under_review": under_review,
        "approved_decisions": approved_decisions,
        "rejected_decisions": rejected_decisions,
        "archived_decisions": archived_decisions,
    }