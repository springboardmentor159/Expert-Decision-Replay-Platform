from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.approval import Approval
from app.models.alternative import Alternative
from app.models.audit_log import AuditLog
from app.models.decision import Decision
from app.models.tag import Tag
from app.models.user import User


def get_decision_report(
    db: Session,
    category: str | None = None,
    decision_status: str | None = None,
    created_by: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    tag: str | None = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    # -----------------------------------
    # Main decision query
    # -----------------------------------
    query = (
        db.query(Decision)
        .join(User, Decision.created_by == User.id)
    )

    # Filters
    if category is not None:
        query = query.filter(Decision.category == category)

    if decision_status is not None:
        query = query.filter(Decision.status == decision_status)

    if created_by is not None:
        query = query.filter(Decision.created_by == created_by)

    if start_date is not None:
        query = query.filter(Decision.created_at >= start_date)

    if end_date is not None:
        query = query.filter(Decision.created_at <= end_date)

    if tag is not None:
        query = (
            query
            .join(Decision.tags)
            .filter(Tag.name == tag)
        )

    # Total filtered records
    total = query.distinct().count()

    # -----------------------------------
    # Sorting
    # -----------------------------------
    sort_columns = {
        "created_at": Decision.created_at,
        "updated_at": Decision.updated_at,
        "title": Decision.title,
    }

    sort_column = sort_columns[sort_by]

    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # -----------------------------------
    # Pagination
    # -----------------------------------
    offset = (page - 1) * page_size

    decisions = (
        query
        .distinct()
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # -----------------------------------
    # Build report items
    # -----------------------------------
    items = []

    for decision in decisions:
        alternative_count = (
            db.query(func.count(Alternative.id))
            .filter(
                Alternative.decision_id == decision.id
            )
            .scalar()
        )

        approval_count = (
            db.query(func.count(Approval.id))
            .filter(
                Approval.decision_id == decision.id
            )
            .scalar()
        )

        items.append(
            {
                "id": decision.id,
                "title": decision.title,
                "category": decision.category,
                "status": decision.status,
                "creator_id": decision.created_by,
                "creator_name": decision.creator.full_name,
                "created_at": decision.created_at,
                "updated_at": decision.updated_at,
                "alternative_count": alternative_count or 0,
                "approval_count": approval_count or 0,
                "tags": [item.name for item in decision.tags],
            }
        )

    # -----------------------------------
    # Statistics
    # -----------------------------------
    stats_query = db.query(Decision)

    if category is not None:
        stats_query = stats_query.filter(
            Decision.category == category
        )

    if decision_status is not None:
        stats_query = stats_query.filter(
            Decision.status == decision_status
        )

    if created_by is not None:
        stats_query = stats_query.filter(
            Decision.created_by == created_by
        )

    if start_date is not None:
        stats_query = stats_query.filter(
            Decision.created_at >= start_date
        )

    if end_date is not None:
        stats_query = stats_query.filter(
            Decision.created_at <= end_date
        )

    if tag is not None:
        stats_query = (
            stats_query
            .join(Decision.tags)
            .filter(Tag.name == tag)
            .distinct()
        )

    # -----------------------------------
    # Final statistics
    # -----------------------------------
    stats = {
        "total": stats_query.count(),
        "draft": stats_query.filter(
            Decision.status == "Draft"
        ).count(),
        "under_review": stats_query.filter(
            Decision.status == "Under Review"
        ).count(),
        "approved": stats_query.filter(
            Decision.status == "Approved"
        ).count(),
        "rejected": stats_query.filter(
            Decision.status == "Rejected"
        ).count(),
        "archived": stats_query.filter(
            Decision.status == "Archived"
        ).count(),
    }

    # -----------------------------------
    # Return response
    # -----------------------------------
    return {
        "items": items,
        "stats": stats,
        "page": page,
        "page_size": page_size,
        "total": total,
    }
# =========================================================
# APPROVAL REPORT
# =========================================================

def get_approval_report(
    db: Session,
    approval_status: str | None = None,
    reviewer_id: int | None = None,
    decision_id: int | None = None,
    approval_level: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    # -----------------------------------
    # Main approval query
    # -----------------------------------
    query = (
        db.query(Approval)
        .join(Decision, Approval.decision_id == Decision.id)
        .join(User, Approval.assigned_to == User.id)
    )

    # -----------------------------------
    # Filters
    # -----------------------------------
    if approval_status is not None:
        query = query.filter(
            Approval.status == approval_status
        )

    if reviewer_id is not None:
        query = query.filter(
            Approval.assigned_to == reviewer_id
        )

    if decision_id is not None:
        query = query.filter(
            Approval.decision_id == decision_id
        )

    if approval_level is not None:
        query = query.filter(
            Approval.approval_level == approval_level
        )

    if start_date is not None:
        query = query.filter(
            Approval.created_at >= start_date
        )

    if end_date is not None:
        query = query.filter(
            Approval.created_at <= end_date
        )

    # -----------------------------------
    # Total filtered records
    # -----------------------------------
    total = query.count()

    # -----------------------------------
    # Sorting
    # -----------------------------------
    sort_columns = {
        "created_at": Approval.created_at,
        "completed_at": Approval.completed_at,
        "decision_title": Decision.title,
    }

    sort_column = sort_columns[sort_by]

    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # -----------------------------------
    # Pagination
    # -----------------------------------
    offset = (page - 1) * page_size

    approvals = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # -----------------------------------
    # Build report items
    # -----------------------------------
    items = []

    for approval in approvals:
        turnaround_hours = None

        if (
            approval.completed_at is not None
            and approval.created_at is not None
        ):
            turnaround_seconds = (
                approval.completed_at - approval.created_at
            ).total_seconds()

            turnaround_hours = round(
                turnaround_seconds / 3600,
                2,
            )

        items.append(
            {
                "id": approval.id,
                "decision_id": approval.decision_id,
                "decision_title": approval.decision.title,
                "reviewer_id": approval.assigned_to,
                "reviewer_name": approval.reviewer.full_name,
                "approval_level": approval.approval_level,
                "status": approval.status,
                "created_at": approval.created_at,
                "completed_at": approval.completed_at,
                "turnaround_hours": turnaround_hours,
            }
        )

    # -----------------------------------
    # Statistics
    # -----------------------------------
    stats_query = (
        db.query(Approval)
        .join(Decision, Approval.decision_id == Decision.id)
        .join(User, Approval.assigned_to == User.id)
    )

    # Apply the SAME filters to statistics
    if approval_status is not None:
        stats_query = stats_query.filter(
            Approval.status == approval_status
        )

    if reviewer_id is not None:
        stats_query = stats_query.filter(
            Approval.assigned_to == reviewer_id
        )

    if decision_id is not None:
        stats_query = stats_query.filter(
            Approval.decision_id == decision_id
        )

    if approval_level is not None:
        stats_query = stats_query.filter(
            Approval.approval_level == approval_level
        )

    if start_date is not None:
        stats_query = stats_query.filter(
            Approval.created_at >= start_date
        )

    if end_date is not None:
        stats_query = stats_query.filter(
            Approval.created_at <= end_date
        )

    total_stats = stats_query.count()

    pending_count = (
        stats_query
        .filter(Approval.status == "Pending")
        .count()
    )

    approved_count = (
        stats_query
        .filter(Approval.status == "Approved")
        .count()
    )

    rejected_count = (
        stats_query
        .filter(Approval.status == "Rejected")
        .count()
    )

    completed_count = approved_count + rejected_count

    if total_stats > 0:
        completion_rate = round(
            (completed_count / total_stats) * 100,
            2,
        )
    else:
        completion_rate = 0.0

    # -----------------------------------
    # Average turnaround
    # -----------------------------------
    completed_approvals = (
        stats_query
        .filter(
            Approval.completed_at.isnot(None)
        )
        .all()
    )

    turnaround_values = []

    for approval in completed_approvals:
        if approval.created_at and approval.completed_at:
            seconds = (
                approval.completed_at
                - approval.created_at
            ).total_seconds()

            turnaround_values.append(
                seconds / 3600
            )

    if turnaround_values:
        average_turnaround_hours = round(
            sum(turnaround_values)
            / len(turnaround_values),
            2,
        )
    else:
        average_turnaround_hours = None

    stats = {
        "total": total_stats,
        "pending": pending_count,
        "approved": approved_count,
        "rejected": rejected_count,
        "average_turnaround_hours": average_turnaround_hours,
        "completion_rate": completion_rate,
    }

    return {
        "items": items,
        "stats": stats,
        "page": page,
        "page_size": page_size,
        "total": total,
    }
def get_team_report(
    db: Session,
    team: str | None = None,
    decision_status: str | None = None,
    category: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "team_name",
    sort_order: str = "asc",
):
    # Get departments/teams
    team_query = db.query(User.department).distinct()

    if team is not None:
        team_query = team_query.filter(User.department == team)

    teams = [row[0] for row in team_query.all()]

    # Apply sorting
    if sort_order == "desc":
        teams = sorted(teams, reverse=True)
    else:
        teams = sorted(teams)

    total = len(teams)

    # Pagination
    offset = (page - 1) * page_size
    paginated_teams = teams[offset:offset + page_size]

    items = []

    for team_name in paginated_teams:
        # Team members
        member_query = db.query(User).filter(
            User.department == team_name
        )

        member_count = member_query.count()

        member_ids = [
            user.id for user in member_query.all()
        ]

        # Decisions created by team members
        decision_query = db.query(Decision).filter(
            Decision.created_by.in_(member_ids)
        )

        if decision_status is not None:
            decision_query = decision_query.filter(
                Decision.status == decision_status
            )

        if category is not None:
            decision_query = decision_query.filter(
                Decision.category == category
            )

        if start_date is not None:
            decision_query = decision_query.filter(
                Decision.created_at >= start_date
            )

        if end_date is not None:
            decision_query = decision_query.filter(
                Decision.created_at <= end_date
            )

        decisions = decision_query.all()

        total_decisions = len(decisions)

        approved_decisions = sum(
            1 for decision in decisions
            if decision.status == "Approved"
        )

        rejected_decisions = sum(
            1 for decision in decisions
            if decision.status == "Rejected"
        )

        pending_decisions = sum(
            1 for decision in decisions
            if decision.status in ["Pending", "Under Review"]
        )

        decision_ids = [decision.id for decision in decisions]

        # Approvals associated with the team's decisions
        if decision_ids:
            approval_query = db.query(Approval).filter(
                Approval.decision_id.in_(decision_ids)
            )
            approvals = approval_query.all()
        else:
            approvals = []

        total_approvals = len(approvals)

        approved_approvals = sum(
            1 for approval in approvals
            if approval.status == "Approved"
        )

        rejected_approvals = sum(
            1 for approval in approvals
            if approval.status == "Rejected"
        )

        pending_approvals = sum(
            1 for approval in approvals
            if approval.status == "Pending"
        )

        completed_approvals = (
            approved_approvals + rejected_approvals
        )

        approval_completion_rate = round(
            (completed_approvals / total_approvals) * 100,
            2
        ) if total_approvals > 0 else 0.0

        items.append({
            "team_name": team_name,
            "member_count": member_count,
            "total_decisions": total_decisions,
            "approved_decisions": approved_decisions,
            "rejected_decisions": rejected_decisions,
            "pending_decisions": pending_decisions,
            "total_approvals": total_approvals,
            "approved_approvals": approved_approvals,
            "rejected_approvals": rejected_approvals,
            "pending_approvals": pending_approvals,
            "approval_completion_rate": approval_completion_rate,
        })

    # Controlled sorting for numeric report fields
    if sort_by != "team_name":
        items.sort(
            key=lambda item: item.get(sort_by, 0),
            reverse=(sort_order == "desc")
        )

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
    }
def get_audit_report(
    db: Session,
    user_id: int | None = None,
    action: str | None = None,
    entity_type: str | None = None,
    entity_id: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    query = (
        db.query(AuditLog)
        .join(User, AuditLog.user_id == User.id)
    )

    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)

    if action is not None:
        query = query.filter(AuditLog.action == action)

    if entity_type is not None:
        query = query.filter(AuditLog.entity_type == entity_type)

    if entity_id is not None:
        query = query.filter(AuditLog.entity_id == entity_id)

    if start_date is not None:
        query = query.filter(AuditLog.created_at >= start_date)

    if end_date is not None:
        query = query.filter(AuditLog.created_at <= end_date)

    total = query.count()

    sort_columns = {
        "created_at": AuditLog.created_at,
        "action": AuditLog.action,
        "entity_type": AuditLog.entity_type,
    }

    sort_column = sort_columns[sort_by]

    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    offset = (page - 1) * page_size

    logs = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    items = []

    for log in logs:
        items.append({
            "id": log.id,
            "user_id": log.user_id,
            "user_name": log.user.full_name,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "description": log.description,
            "ip_address": log.ip_address,
            "created_at": log.created_at,
        })

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
    }