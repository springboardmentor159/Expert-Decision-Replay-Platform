from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User


VALID_SORT_FIELDS = {
    "approval_date": Approval.completed_at,
    "created_date": Approval.assigned_at,
}


def get_approval_report(
    db: Session,
    approval_status: Optional[str] = None,
    reviewer_id: Optional[int] = None,
    decision_id: Optional[int] = None,
    approval_level: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "approval_date",
    sort_order: str = "desc",
):
    query = (
        db.query(
            Approval,
            Decision.title.label("decision_title"),
            User.full_name.label("reviewer_name"),
        )
        .join(
            Decision,
            Approval.decision_id == Decision.id
        )
        .join(
            User,
            Approval.reviewer_id == User.id
        )
    )

    # Filters
    if approval_status:
        query = query.filter(
            Approval.status == approval_status
        )

    if reviewer_id is not None:
        query = query.filter(
            Approval.reviewer_id == reviewer_id
        )

    if decision_id is not None:
        query = query.filter(
            Approval.decision_id == decision_id
        )

    if approval_level is not None:
        query = query.filter(
            Approval.approval_level == approval_level
        )

    if date_from:
        query = query.filter(
            Approval.assigned_at >= date_from
        )

    if date_to:
        query = query.filter(
            Approval.assigned_at <= date_to
        )

    total_records = query.count()

    # Controlled sorting only
    sort_column = VALID_SORT_FIELDS[sort_by]

    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    offset = (page - 1) * page_size

    rows = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    data = []

    for approval, decision_title, reviewer_name in rows:

        turnaround = None

        if (
            approval.completed_at is not None
            and approval.assigned_at is not None
        ):
            turnaround_seconds = (
                approval.completed_at - approval.assigned_at
            ).total_seconds()

            turnaround = round(
                turnaround_seconds / 86400,
                2
            )

        data.append(
            {
                "approval_id": approval.id,
                "decision_id": approval.decision_id,
                "decision_title": decision_title,
                "reviewer": reviewer_name,
                "approval_level": approval.approval_level,
                "approval_status": approval.status,
                "assigned_date": approval.assigned_at,
                "completed_date": approval.completed_at,
                "approval_turnaround_time": turnaround,
            }
        )

    # Statistics use the same filters
    stats_query = (
        db.query(Approval)
    )

    if approval_status:
        stats_query = stats_query.filter(
            Approval.status == approval_status
        )

    if reviewer_id is not None:
        stats_query = stats_query.filter(
            Approval.reviewer_id == reviewer_id
        )

    if decision_id is not None:
        stats_query = stats_query.filter(
            Approval.decision_id == decision_id
        )

    if approval_level is not None:
        stats_query = stats_query.filter(
            Approval.approval_level == approval_level
        )

    if date_from:
        stats_query = stats_query.filter(
            Approval.assigned_at >= date_from
        )

    if date_to:
        stats_query = stats_query.filter(
            Approval.assigned_at <= date_to
        )

    stats_rows = stats_query.all()

    total = len(stats_rows)

    pending = sum(
        1
        for approval in stats_rows
        if approval.status.lower() == "pending"
    )

    approved = sum(
        1
        for approval in stats_rows
        if approval.status.lower() == "approved"
    )

    rejected = sum(
        1
        for approval in stats_rows
        if approval.status.lower() == "rejected"
    )

    completed_turnarounds = []

    for approval in stats_rows:
        if (
            approval.completed_at is not None
            and approval.assigned_at is not None
        ):
            turnaround_seconds = (
                approval.completed_at - approval.assigned_at
            ).total_seconds()

            completed_turnarounds.append(
                turnaround_seconds / 86400
            )

    if completed_turnarounds:
        average_turnaround = round(
            sum(completed_turnarounds)
            / len(completed_turnarounds),
            2
        )
    else:
        average_turnaround = None

    completed_count = approved + rejected

    if total > 0:
        completion_rate = round(
            (completed_count / total) * 100,
            2
        )
    else:
        completion_rate = 0.0

    stats = {
        "total": total,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "average_turnaround": average_turnaround,
        "completion_rate": completion_rate,
    }

    return {
        "data": data,
        "stats": stats,
        "page": page,
        "page_size": page_size,
        "total_records": total_records,
    }