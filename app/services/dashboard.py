from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog
from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User


def get_dashboard_data(
    db: Session,
    current_user: User,
):
    role = current_user.role

    # ---------------------------------------------------------
    # COMMON RECENT ACTIVITIES
    # ---------------------------------------------------------
    recent_activities = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == current_user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
        .all()
    )

    result = {
        "role": role,
        "my_decisions": [],
        "pending_reviews": [],
        "recent_activities": recent_activities,
        "team_decisions": [],
        "pending_approvals": [],
        "decision_statistics": {},
        "system_analytics": {},
        "user_activity": [],
        "organization_reports": {},
    }

    # ---------------------------------------------------------
    # EMPLOYEE DASHBOARD
    # ---------------------------------------------------------
    if role == "Employee":
        my_decisions = (
            db.query(Decision)
            .filter(Decision.created_by == current_user.id)
            .order_by(Decision.created_at.desc())
            .limit(10)
            .all()
        )

        result["my_decisions"] = [
            {
                "id": decision.id,
                "title": decision.title,
                "category": decision.category,
                "status": decision.status,
                "created_at": decision.created_at,
                "updated_at": decision.updated_at,
            }
            for decision in my_decisions
        ]

        # Pending reviews for an employee are represented by
        # their decisions that are currently Under Review.
        pending_reviews = (
            db.query(Decision)
            .filter(
                Decision.created_by == current_user.id,
                Decision.status == "Under Review",
            )
            .order_by(Decision.updated_at.desc())
            .all()
        )

        result["pending_reviews"] = [
            {
                "id": decision.id,
                "title": decision.title,
                "category": decision.category,
                "status": decision.status,
                "updated_at": decision.updated_at,
            }
            for decision in pending_reviews
        ]

    # ---------------------------------------------------------
    # MANAGER DASHBOARD
    # ---------------------------------------------------------
    elif role == "Manager":
        team_decisions = (
            db.query(Decision)
            .join(User, Decision.created_by == User.id)
            .filter(User.department == current_user.department)
            .order_by(Decision.created_at.desc())
            .limit(20)
            .all()
        )

        result["team_decisions"] = [
            {
                "id": decision.id,
                "title": decision.title,
                "category": decision.category,
                "status": decision.status,
                "created_by": decision.created_by,
                "created_at": decision.created_at,
                "updated_at": decision.updated_at,
            }
            for decision in team_decisions
        ]

        pending_approvals = (
            db.query(Approval)
            .filter(
                Approval.assigned_reviewer_id == current_user.id,
                Approval.status == "Pending",
            )
            .order_by(Approval.created_at.desc())
            .all()
        )

        result["pending_approvals"] = [
            {
                "id": approval.id,
                "decision_id": approval.decision_id,
                "approval_level": approval.approval_level,
                "status": approval.status,
                "created_at": approval.created_at,
            }
            for approval in pending_approvals
        ]

        # Decision statistics for the manager's department
        statistics_query = (
            db.query(
                Decision.status,
                func.count(Decision.id),
            )
            .join(User, Decision.created_by == User.id)
            .filter(User.department == current_user.department)
            .group_by(Decision.status)
            .all()
        )

        statistics = {
            "Draft": 0,
            "Under Review": 0,
            "Approved": 0,
            "Rejected": 0,
            "Archived": 0,
        }

        for status_name, count in statistics_query:
            statistics[status_name] = count

        result["decision_statistics"] = statistics

    # ---------------------------------------------------------
    # ADMINISTRATOR DASHBOARD
    # ---------------------------------------------------------
    elif role in {"Administrator", "Admin"}:
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_decisions = db.query(func.count(Decision.id)).scalar() or 0
        total_approvals = db.query(func.count(Approval.id)).scalar() or 0
        pending_approvals = (
            db.query(func.count(Approval.id))
            .filter(Approval.status == "Pending")
            .scalar()
            or 0
        )

        result["system_analytics"] = {
            "total_users": total_users,
            "total_decisions": total_decisions,
            "total_approvals": total_approvals,
            "pending_approvals": pending_approvals,
        }

        # Recent activity across the organization
        organization_activity = (
            db.query(ActivityLog)
            .order_by(ActivityLog.created_at.desc())
            .limit(20)
            .all()
        )

        result["user_activity"] = [
            {
                "id": activity.id,
                "user_id": activity.user_id,
                "action": activity.action,
                "entity_type": activity.entity_type,
                "entity_id": activity.entity_id,
                "description": activity.description,
                "created_at": activity.created_at,
            }
            for activity in organization_activity
        ]

        # Organization-wide decision statistics
        organization_statistics_query = (
            db.query(
                Decision.status,
                func.count(Decision.id),
            )
            .group_by(Decision.status)
            .all()
        )

        organization_statistics = {
            "Draft": 0,
            "Under Review": 0,
            "Approved": 0,
            "Rejected": 0,
            "Archived": 0,
        }

        for status_name, count in organization_statistics_query:
            organization_statistics[status_name] = count

        result["organization_reports"] = {
            "decision_statistics": organization_statistics,
            "total_users": total_users,
            "total_decisions": total_decisions,
            "total_approvals": total_approvals,
        }

    return result