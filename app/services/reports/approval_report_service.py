from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User


VALID_SORT_FIELDS = {
    "approval_date": Approval.assigned_at,
}

VALID_SORT_ORDERS = {
    "asc",
    "desc",
}

VALID_STATUSES = {
    "Pending",
    "Under Review",
    "Approved",
    "Rejected",
}


def _validate_pagination(
    page: int,
    page_size: int,
) -> None:
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="page must be greater than or equal to 1",
        )

    if page_size < 1 or page_size > 10000:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="page_size must be between 1 and 10000",
        )


def _validate_sorting(
    sort_by: str,
    sort_order: str,
) -> None:
    if sort_by not in VALID_SORT_FIELDS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid approval report sort_by. "
                "Allowed value: approval_date"
            ),
        )

    if sort_order not in VALID_SORT_ORDERS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "sort_order must be either "
                "'asc' or 'desc'"
            ),
        )


def _apply_authorization_scope(
    query,
    current_user: User,
):
    role = (current_user.role or "").strip()

    if role == "Employee":
        return (
            query
            .join(
                Decision,
                Approval.decision_id == Decision.id,
            )
            .filter(
                Decision.created_by == current_user.id
            )
        )

    if role == "Reviewer":
        return query.filter(
            Approval.reviewer_id == current_user.id
        )

    if role == "Manager":
        return (
            query
            .join(
                Decision,
                Approval.decision_id == Decision.id,
            )
            .join(
                User,
                Decision.created_by == User.id,
            )
            .filter(
                User.department == current_user.department
            )
        )

    if role == "Administrator":
        return query

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions",
    )


def _apply_filters(
    query,
    approval_status: Optional[str],
    reviewer_id: Optional[int],
    decision_id: Optional[int],
    approval_level: Optional[int],
    date_from: Optional[datetime],
    date_to: Optional[datetime],
):
    if approval_status:
        normalized_status = approval_status.strip()

        if normalized_status not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Invalid approval status. Allowed values: "
                    "Pending, Under Review, Approved, Rejected"
                ),
            )

        query = query.filter(
            Approval.status == normalized_status
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

    return query


def _turnaround_seconds(
    assigned_at: Optional[datetime],
    completed_at: Optional[datetime],
) -> Optional[float]:
    if not assigned_at or not completed_at:
        return None

    assigned = assigned_at
    completed = completed_at

    if assigned.tzinfo is None:
        assigned = assigned.replace(
            tzinfo=timezone.utc
        )

    if completed.tzinfo is None:
        completed = completed.replace(
            tzinfo=timezone.utc
        )

    seconds = (
        completed - assigned
    ).total_seconds()

    return max(seconds, 0.0)


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
    current_user: Optional[User] = None,
):
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    _validate_pagination(
        page=page,
        page_size=page_size,
    )

    _validate_sorting(
        sort_by=sort_by,
        sort_order=sort_order,
    )

    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "date_from must be earlier than "
                "or equal to date_to"
            ),
        )

    query = (
        db.query(
            Approval,
            Decision.title.label("decision_title"),
            User.full_name.label("reviewer_name"),
        )
        .join(
            Decision,
            Approval.decision_id == Decision.id,
        )
        .join(
            User,
            Approval.reviewer_id == User.id,
        )
    )

    query = _apply_authorization_scope(
        query,
        current_user,
    )

    query = _apply_filters(
        query,
        approval_status=approval_status,
        reviewer_id=reviewer_id,
        decision_id=decision_id,
        approval_level=approval_level,
        date_from=date_from,
        date_to=date_to,
    )

    total_records = query.count()

    sort_column = VALID_SORT_FIELDS[sort_by]

    if sort_order == "asc":
        query = query.order_by(
            sort_column.asc(),
            Approval.id.asc(),
        )
    else:
        query = query.order_by(
            sort_column.desc(),
            Approval.id.desc(),
        )

    offset = (page - 1) * page_size

    rows = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    data = []

    turnaround_values = []

    for (
        approval,
        decision_title,
        reviewer_name,
    ) in rows:
        turnaround = _turnaround_seconds(
            approval.assigned_at,
            approval.completed_at,
        )

        if turnaround is not None:
            turnaround_values.append(
                turnaround
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

    # Build statistics from the complete authorized and
    # filtered dataset, not only the current page.
    stats_query = db.query(Approval)

    stats_query = _apply_authorization_scope(
        stats_query,
        current_user,
    )

    stats_query = _apply_filters(
        stats_query,
        approval_status=approval_status,
        reviewer_id=reviewer_id,
        decision_id=decision_id,
        approval_level=approval_level,
        date_from=date_from,
        date_to=date_to,
    )

    stats_rows = stats_query.all()

    total = len(stats_rows)

    pending = sum(
        1
        for approval in stats_rows
        if approval.status == "Pending"
    )

    approved = sum(
        1
        for approval in stats_rows
        if approval.status == "Approved"
    )

    rejected = sum(
        1
        for approval in stats_rows
        if approval.status == "Rejected"
    )

    completed_turnarounds = []

    for approval in stats_rows:
        turnaround = _turnaround_seconds(
            approval.assigned_at,
            approval.completed_at,
        )

        if turnaround is not None:
            completed_turnarounds.append(
                turnaround
            )

    average_turnaround = None

    if completed_turnarounds:
        average_turnaround = (
            sum(completed_turnarounds)
            / len(completed_turnarounds)
        )

    completion_rate = 0.0

    if total > 0:
        completed_count = approved + rejected

        completion_rate = (
            completed_count / total
        ) * 100.0

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