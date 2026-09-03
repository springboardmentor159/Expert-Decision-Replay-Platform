from datetime import datetime, date, time
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.decision import Decision
from app.models.user import User
from app.models.alternative import Alternative
from app.models.approval import Approval, ApprovalStatus
from app.models.audit_log import AuditLog
from app.models.tag import Tag


# =========================================================
# DATE HELPERS
# =========================================================

def parse_date(
    value: Optional[date],
    end_of_day: bool = False
):
    if value is None:
        return None

    if end_of_day:
        return datetime.combine(value, time.max)

    return datetime.combine(value, time.min)


def validate_date_range(
    start_date: Optional[date],
    end_date: Optional[date]
):
    if start_date and end_date and start_date > end_date:
        raise ValueError(
            "start_date cannot be after end_date"
        )


# =========================================================
# DECISION REPORT
# =========================================================

def get_decision_report(
    db: Session,
    category: Optional[str] = None,
    status: Optional[str] = None,
    created_by: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    tag: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    order: str = "desc",
):

    validate_date_range(start_date, end_date)

    query = (
        db.query(Decision)
        .join(
            User,
            Decision.created_by == User.id
        )
    )

    # -------------------------
    # FILTERS
    # -------------------------

    if category:
        query = query.filter(
            Decision.category == category
        )

    if status:
        query = query.filter(
            Decision.status == status
        )

    if created_by:
        query = query.filter(
            Decision.created_by == created_by
        )

    if start_date:
        query = query.filter(
            Decision.created_at >= parse_date(start_date)
        )

    if end_date:
        query = query.filter(
            Decision.created_at <= parse_date(
                end_date,
                end_of_day=True
            )
        )

    if tag:
        query = (
            query
            .join(Decision.tags)
            .filter(Tag.name == tag)
        )

    # -------------------------
    # SUMMARY
    # -------------------------

    total = query.count()

    draft = query.filter(
        Decision.status == "Draft"
    ).count()

    under_review = query.filter(
        Decision.status == "Under Review"
    ).count()

    approved = query.filter(
        Decision.status == "Approved"
    ).count()

    rejected = query.filter(
        Decision.status == "Rejected"
    ).count()

    archived = query.filter(
        Decision.status == "Archived"
    ).count()

    # -------------------------
    # CONTROLLED SORTING
    # -------------------------

    sort_columns = {
        "id": Decision.id,
        "title": Decision.title,
        "category": Decision.category,
        "status": Decision.status,
        "created_at": Decision.created_at,
        "updated_at": Decision.updated_at,
    }

    sort_column = sort_columns[sort_by]

    if order == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    # -------------------------
    # PAGINATION
    # -------------------------

    offset = (page - 1) * page_size

    decisions = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    data = []

    for decision in decisions:

        alternatives_count = (
            db.query(
                func.count(Alternative.id)
            )
            .filter(
                Alternative.decision_id == decision.id
            )
            .scalar()
            or 0
        )

        approvals_count = (
            db.query(
                func.count(Approval.id)
            )
            .filter(
                Approval.decision_id == decision.id
            )
            .scalar()
            or 0
        )

        tags = [
            item.name
            for item in decision.tags
        ]

        data.append({
            "decision_id": decision.id,
            "title": decision.title,
            "category": decision.category,
            "status": (
                decision.status.value
                if hasattr(
                    decision.status,
                    "value"
                )
                else str(decision.status)
            ),
            "created_by": {
                "id": decision.creator.id,
                "name": decision.creator.full_name,
                "email": decision.creator.email,
            },
            "created_date": decision.created_at,
            "updated_date": decision.updated_at,
            "number_alternatives": alternatives_count,
            "number_approvals": approvals_count,
            "tags": tags,
        })

    return {
        "summary": {
            "total_decisions": total,
            "draft": draft,
            "under_review": under_review,
            "approved": approved,
            "rejected": rejected,
            "archived": archived,
        },
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (
                (total + page_size - 1) // page_size
            ),
        },
        "data": data,
    }


# =========================================================
# APPROVAL REPORT
# =========================================================

def get_approval_report(
    db: Session,
    status: Optional[str] = None,
    reviewer: Optional[int] = None,
    decision: Optional[int] = None,
    approval_level: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "assigned_at",
    order: str = "desc",
):

    validate_date_range(start_date, end_date)

    query = (
        db.query(Approval)
        .join(
            Approval.decision
        )
        .join(
            User,
            Approval.assigned_to == User.id
        )
    )

    # -------------------------
    # FILTERS
    # -------------------------

    if status:
        query = query.filter(
            Approval.status == status
        )

    if reviewer:
        query = query.filter(
            Approval.assigned_to == reviewer
        )

    if decision:
        query = query.filter(
            Approval.decision_id == decision
        )

    if approval_level:
        query = query.filter(
            Approval.assigned_role == approval_level
        )

    if start_date:
        query = query.filter(
            Approval.assigned_at >= parse_date(start_date)
        )

    if end_date:
        query = query.filter(
            Approval.assigned_at <= parse_date(
                end_date,
                end_of_day=True
            )
        )

    # -------------------------
    # SUMMARY
    # -------------------------

    total = query.count()

    pending = query.filter(
        Approval.status == ApprovalStatus.PENDING
    ).count()

    approved = query.filter(
        Approval.status == ApprovalStatus.APPROVED
    ).count()

    rejected = query.filter(
        Approval.status == ApprovalStatus.REJECTED
    ).count()

    completed = approved + rejected

    completion_rate = (
        (completed / total) * 100
        if total
        else 0
    )

    # -------------------------
    # TURNAROUND TIME
    # -------------------------

    completed_approvals = query.filter(
        Approval.reviewed_at.isnot(None)
    ).all()

    turnaround_values = []

    for approval in completed_approvals:

        if (
            approval.reviewed_at
            and approval.assigned_at
        ):
            seconds = (
                approval.reviewed_at
                - approval.assigned_at
            ).total_seconds()

            turnaround_values.append(
                seconds / 3600
            )

    average_turnaround = (
        sum(turnaround_values)
        / len(turnaround_values)
        if turnaround_values
        else 0
    )

    # -------------------------
    # CONTROLLED SORTING
    # -------------------------

    sort_columns = {
        "id": Approval.id,
        "decision_id": Approval.decision_id,
        "assigned_at": Approval.assigned_at,
        "reviewed_at": Approval.reviewed_at,
        "status": Approval.status,
    }

    sort_column = sort_columns[sort_by]

    if order == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    # -------------------------
    # PAGINATION
    # -------------------------

    offset = (page - 1) * page_size

    approvals = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    data = []

    for approval in approvals:

        turnaround_hours = None

        if (
            approval.reviewed_at
            and approval.assigned_at
        ):
            turnaround_hours = (
                approval.reviewed_at
                - approval.assigned_at
            ).total_seconds() / 3600

        data.append({
            "approval_id": approval.id,
            "decision_id": approval.decision_id,
            "decision_title": approval.decision.title,
            "reviewer": {
                "id": approval.assigned_user.id,
                "name": approval.assigned_user.full_name,
                "email": approval.assigned_user.email,
            },
            "approval_level": (
                approval.assigned_role.value
                if hasattr(
                    approval.assigned_role,
                    "value"
                )
                else str(approval.assigned_role)
            ),
            "approval_status": (
                approval.status.value
                if hasattr(
                    approval.status,
                    "value"
                )
                else str(approval.status)
            ),
            "assigned_date": approval.assigned_at,
            "completed_date": approval.reviewed_at,
            "turnaround_time_hours": turnaround_hours,
        })

    return {
        "summary": {
            "total_approvals": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "average_turnaround_hours": round(
                average_turnaround,
                2
            ),
            "completion_rate": round(
                completion_rate,
                2
            ),
        },
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (
                (total + page_size - 1) // page_size
            ),
        },
        "data": data,
    }


# =========================================================
# TEAM REPORT
# =========================================================
# Your current database does not have a Team table.
# Therefore User.department is used as the team.
# =========================================================

def get_team_report(
    db: Session,
    team: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    decision_status: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "team",
    order: str = "asc",
):

    validate_date_range(start_date, end_date)

    departments_query = (
        db.query(User.department)
        .filter(
            User.department.isnot(None)
        )
        .distinct()
    )

    if team:
        departments_query = departments_query.filter(
            User.department == team
        )

    departments = [
        row[0]
        for row in departments_query.all()
    ]

    data = []

    for department in departments:

        members = (
            db.query(User)
            .filter(
                User.department == department
            )
            .all()
        )

        member_ids = [
            member.id
            for member in members
        ]

        if not member_ids:
            continue

        decision_query = (
            db.query(Decision)
            .filter(
                Decision.created_by.in_(member_ids)
            )
        )

        if start_date:
            decision_query = decision_query.filter(
                Decision.created_at >= parse_date(
                    start_date
                )
            )

        if end_date:
            decision_query = decision_query.filter(
                Decision.created_at <= parse_date(
                    end_date,
                    end_of_day=True
                )
            )

        if decision_status:
            decision_query = decision_query.filter(
                Decision.status == decision_status
            )

        if category:
            decision_query = decision_query.filter(
                Decision.category == category
            )

        decisions = decision_query.all()

        total_decisions = len(decisions)

        approved = sum(
            1
            for item in decisions
            if (
                item.status.value
                if hasattr(item.status, "value")
                else str(item.status)
            ) == "Approved"
        )

        rejected = sum(
            1
            for item in decisions
            if (
                item.status.value
                if hasattr(item.status, "value")
                else str(item.status)
            ) == "Rejected"
        )

        pending = sum(
            1
            for item in decisions
            if (
                item.status.value
                if hasattr(item.status, "value")
                else str(item.status)
            ) in ["Draft", "Under Review"]
        )

        # -------------------------
        # APPROVAL STATISTICS
        # -------------------------

        approval_query = (
            db.query(Approval)
            .filter(
                Approval.assigned_to.in_(member_ids)
            )
        )

        if start_date:
            approval_query = approval_query.filter(
                Approval.assigned_at >= parse_date(
                    start_date
                )
            )

        if end_date:
            approval_query = approval_query.filter(
                Approval.assigned_at <= parse_date(
                    end_date,
                    end_of_day=True
                )
            )

        approvals = approval_query.all()

        approval_total = len(approvals)

        approval_approved = sum(
            1
            for item in approvals
            if (
                item.status.value
                if hasattr(item.status, "value")
                else str(item.status)
            ) == "Approved"
        )

        approval_rejected = sum(
            1
            for item in approvals
            if (
                item.status.value
                if hasattr(item.status, "value")
                else str(item.status)
            ) == "Rejected"
        )

        approval_pending = sum(
            1
            for item in approvals
            if (
                item.status.value
                if hasattr(item.status, "value")
                else str(item.status)
            ) == "Pending"
        )

        completion_rate = (
            (
                (
                    approval_approved
                    + approval_rejected
                )
                / approval_total
            ) * 100
            if approval_total
            else 0
        )

        data.append({
            "team": department,
            "member_count": len(members),
            "total_decisions": total_decisions,
            "approved": approved,
            "rejected": rejected,
            "pending": pending,
            "approval_statistics": {
                "total": approval_total,
                "approved": approval_approved,
                "rejected": approval_rejected,
                "pending": approval_pending,
                "completion_rate": round(
                    completion_rate,
                    2
                ),
            },
        })

    # -------------------------
    # SORTING
    # -------------------------

    reverse = order == "desc"

    sort_functions = {
        "team": lambda x: x["team"].lower(),
        "member_count": lambda x: x["member_count"],
        "total_decisions": lambda x: x["total_decisions"],
        "approved": lambda x: x["approved"],
        "rejected": lambda x: x["rejected"],
    }

    data.sort(
        key=sort_functions[sort_by],
        reverse=reverse
    )

    total = len(data)

    offset = (page - 1) * page_size

    paginated_data = data[
        offset:offset + page_size
    ]

    return {
        "summary": {
            "total_teams": total,
            "total_members": sum(
                item["member_count"]
                for item in data
            ),
            "total_decisions": sum(
                item["total_decisions"]
                for item in data
            ),
            "approved": sum(
                item["approved"]
                for item in data
            ),
            "rejected": sum(
                item["rejected"]
                for item in data
            ),
            "pending": sum(
                item["pending"]
                for item in data
            ),
        },
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (
                (total + page_size - 1) // page_size
            ),
        },
        "data": paginated_data,
    }


# =========================================================
# AUDIT REPORT
# =========================================================

def get_audit_report(
    db: Session,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    order: str = "desc",
):

    validate_date_range(start_date, end_date)

    query = (
        db.query(AuditLog)
        .outerjoin(
            User,
            AuditLog.user_id == User.id
        )
    )

    # -------------------------
    # FILTERS
    # -------------------------

    if user_id:
        query = query.filter(
            AuditLog.user_id == user_id
        )

    if action:
        query = query.filter(
            AuditLog.action == action
        )

    if entity_type:
        query = query.filter(
            AuditLog.entity_type == entity_type
        )

    if entity_id:
        query = query.filter(
            AuditLog.entity_id == entity_id
        )

    if start_date:
        query = query.filter(
            AuditLog.created_at >= parse_date(
                start_date
            )
        )

    if end_date:
        query = query.filter(
            AuditLog.created_at <= parse_date(
                end_date,
                end_of_day=True
            )
        )

    total = query.count()

    # -------------------------
    # CONTROLLED SORTING
    # -------------------------

    sort_columns = {
        "id": AuditLog.id,
        "action": AuditLog.action,
        "entity_type": AuditLog.entity_type,
        "entity_id": AuditLog.entity_id,
        "created_at": AuditLog.created_at,
    }

    sort_column = sort_columns[sort_by]

    if order == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    # -------------------------
    # PAGINATION
    # -------------------------

    offset = (page - 1) * page_size

    logs = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    data = []

    for log in logs:

        data.append({
            "audit_id": log.id,
            "user": {
                "id": (
                    log.user.id
                    if log.user
                    else None
                ),
                "name": (
                    log.user.full_name
                    if log.user
                    else None
                ),
                "email": (
                    log.user.email
                    if log.user
                    else None
                ),
            },
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "description": log.description,
            "timestamp": log.created_at,
            "ip_address": log.ip_address,
            "request_method": log.request_method,
            "endpoint": log.endpoint,
        })

    return {
        "summary": {
            "total_audit_records": total,
        },
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (
                (total + page_size - 1) // page_size
            ),
        },
        "data": data,
    }