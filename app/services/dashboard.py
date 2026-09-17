from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog
from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User


def get_dashboard_data(
    db: Session,
    current_user: User,
    activity_action: str | None = None,
    activity_start_date: date | None = None,
    activity_end_date: date | None = None,
):
    role = current_user.role

    # ---------------------------------------------------------
    # ACTIVITY FILTERS
    # ---------------------------------------------------------
    activity_query = db.query(ActivityLog).filter(
        ActivityLog.user_id == current_user.id
    )

    if activity_action:
        activity_query = activity_query.filter(
            ActivityLog.action == activity_action
        )

    if activity_start_date:
        start_datetime = datetime.combine(
            activity_start_date,
            datetime.min.time(),
            tzinfo=timezone.utc,
        )
        activity_query = activity_query.filter(
            ActivityLog.created_at >= start_datetime
        )

    if activity_end_date:
        end_datetime = datetime.combine(
            activity_end_date,
            datetime.max.time(),
            tzinfo=timezone.utc,
        )
        activity_query = activity_query.filter(
            ActivityLog.created_at <= end_datetime
        )

    recent_activities = (
        activity_query
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
    # REVIEWER DASHBOARD
    # ---------------------------------------------------------
    elif role == "Reviewer":
        pending_reviews = (
            db.query(Approval)
            .filter(
                Approval.assigned_reviewer_id == current_user.id,
                Approval.approval_level == 1,
                Approval.status == "Pending",
            )
            .order_by(Approval.created_at.desc())
            .all()
        )

        result["pending_reviews"] = [
            {
                "id": approval.id,
                "decision_id": approval.decision_id,
                "approval_level": approval.approval_level,
                "status": approval.status,
                "created_at": approval.created_at,
            }
            for approval in pending_reviews
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
        # -----------------------------------------------------
        # ORGANIZATION TOTALS
        # -----------------------------------------------------
        total_users = (
            db.query(func.count(User.id)).scalar() or 0
        )

        total_decisions = (
            db.query(func.count(Decision.id)).scalar() or 0
        )

        total_approvals = (
            db.query(func.count(Approval.id)).scalar() or 0
        )

        pending_approvals = (
            db.query(func.count(Approval.id))
            .filter(Approval.status == "Pending")
            .scalar()
            or 0
        )

        # -----------------------------------------------------
        # ACTIVE USERS
        # -----------------------------------------------------
        active_users_since = (
            datetime.now(timezone.utc)
            - timedelta(days=30)
        )

        active_users = (
            db.query(
                func.count(
                    func.distinct(ActivityLog.user_id)
                )
            )
            .filter(
                ActivityLog.created_at >= active_users_since
            )
            .scalar()
            or 0
        )

        # -----------------------------------------------------
        # USERS BY ROLE
        # -----------------------------------------------------
        users_by_role_query = (
            db.query(
                User.role,
                func.count(User.id),
            )
            .group_by(User.role)
            .all()
        )

        users_by_role = {}

        for role_name, count in users_by_role_query:
            users_by_role[str(role_name)] = count

        # -----------------------------------------------------
        # APPROVAL ANALYTICS
        # -----------------------------------------------------
        completed_approvals = (
            db.query(func.count(Approval.id))
            .filter(
                Approval.completed_at.isnot(None)
            )
            .scalar()
            or 0
        )

        if total_approvals:
            completion_rate = round(
                (completed_approvals / total_approvals) * 100,
                2,
            )
        else:
            completion_rate = 0.0

        completed_approval_rows = (
            db.query(Approval.created_at, Approval.completed_at)
            .filter(
                Approval.completed_at.isnot(None),
                Approval.created_at.isnot(None),
            )
            .all()
        )

        turnaround_hours = []

        for created_at, completed_at in completed_approval_rows:
            if created_at and completed_at:
                duration = (
                    completed_at - created_at
                ).total_seconds() / 3600

                turnaround_hours.append(duration)

        if turnaround_hours:
            average_turnaround_hours = round(
                sum(turnaround_hours)
                / len(turnaround_hours),
                2,
            )
        else:
            average_turnaround_hours = 0.0

        # -----------------------------------------------------
        # DECISION CREATION STATISTICS
        # -----------------------------------------------------
        now = datetime.now(timezone.utc)

        daily_start = now - timedelta(days=7)
        weekly_start = now - timedelta(weeks=12)
        monthly_start = now - timedelta(days=365)

        daily_query = (
            db.query(
                func.date(Decision.created_at),
                func.count(Decision.id),
            )
            .filter(
                Decision.created_at >= daily_start
            )
            .group_by(func.date(Decision.created_at))
            .order_by(func.date(Decision.created_at))
            .all()
        )

        weekly_query = (
            db.query(
                func.date_trunc(
                    "week",
                    Decision.created_at,
                ),
                func.count(Decision.id),
            )
            .filter(
                Decision.created_at >= weekly_start
            )
            .group_by(
                func.date_trunc(
                    "week",
                    Decision.created_at,
                )
            )
            .order_by(
                func.date_trunc(
                    "week",
                    Decision.created_at,
                )
            )
            .all()
        )

        monthly_query = (
            db.query(
                func.date_trunc(
                    "month",
                    Decision.created_at,
                ),
                func.count(Decision.id),
            )
            .filter(
                Decision.created_at >= monthly_start
            )
            .group_by(
                func.date_trunc(
                    "month",
                    Decision.created_at,
                )
            )
            .order_by(
                func.date_trunc(
                    "month",
                    Decision.created_at,
                )
            )
            .all()
        )

        decision_creation_statistics = {
            "daily": [
                {
                    "date": str(period),
                    "count": count,
                }
                for period, count in daily_query
            ],
            "weekly": [
                {
                    "week": str(period),
                    "count": count,
                }
                for period, count in weekly_query
            ],
            "monthly": [
                {
                    "month": str(period),
                    "count": count,
                }
                for period, count in monthly_query
            ],
        }

        result["system_analytics"] = {
            "total_users": total_users,
            "active_users": active_users,
            "total_decisions": total_decisions,
            "total_approvals": total_approvals,
            "pending_approvals": pending_approvals,
            "completed_approvals": completed_approvals,
            "approval_completion_rate": completion_rate,
            "average_approval_turnaround_hours": average_turnaround_hours,
            "users_by_role": users_by_role,
            "decision_creation_statistics": decision_creation_statistics,
        }

        # -----------------------------------------------------
        # ORGANIZATION ACTIVITY WITH FILTERS
        # -----------------------------------------------------
        organization_activity_query = db.query(ActivityLog)

        if activity_action:
            organization_activity_query = (
                organization_activity_query.filter(
                    ActivityLog.action == activity_action
                )
            )

        if activity_start_date:
            start_datetime = datetime.combine(
                activity_start_date,
                datetime.min.time(),
                tzinfo=timezone.utc,
            )

            organization_activity_query = (
                organization_activity_query.filter(
                    ActivityLog.created_at >= start_datetime
                )
            )

        if activity_end_date:
            end_datetime = datetime.combine(
                activity_end_date,
                datetime.max.time(),
                tzinfo=timezone.utc,
            )

            organization_activity_query = (
                organization_activity_query.filter(
                    ActivityLog.created_at <= end_datetime
                )
            )

        organization_activity = (
            organization_activity_query
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

        # -----------------------------------------------------
        # ORGANIZATION-WIDE DECISION STATISTICS
        # -----------------------------------------------------
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
            "users_by_role": users_by_role,
            "approval_completion_rate": completion_rate,
            "average_approval_turnaround_hours": average_turnaround_hours,
            "decision_creation_statistics": decision_creation_statistics,
        }

    return result