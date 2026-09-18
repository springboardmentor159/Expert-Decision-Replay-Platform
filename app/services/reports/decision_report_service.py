from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status as http_status
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.alternative import Alternative
from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User


VALID_SORT_FIELDS = {
    "created_date": Decision.created_at,
    "updated_date": Decision.updated_at,
    "title": Decision.title,
}

VALID_SORT_ORDERS = {
    "asc",
    "desc",
}


def _validate_pagination(
    page: int,
    page_size: int,
) -> None:
    if page < 1:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="page must be greater than or equal to 1",
        )

    if page_size < 1 or page_size > 10000:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="page_size must be between 1 and 10000",
        )


def _validate_sorting(
    sort_by: str,
    sort_order: str,
) -> None:
    if sort_by not in VALID_SORT_FIELDS:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid decision report sort_by. "
                "Allowed values: created_date, updated_date, title"
            ),
        )

    if sort_order not in VALID_SORT_ORDERS:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="sort_order must be either 'asc' or 'desc'",
        )


def _apply_authorization_scope(
    query,
    current_user: User,
):
    role = (current_user.role or "").strip()

    if role == "Employee":
        return query.filter(
            Decision.created_by == current_user.id
        )

    if role == "Reviewer":
        return query.filter(
            Approval.reviewer_id == current_user.id
        )

    if role == "Manager":
        return query.filter(
            User.department == current_user.department
        )

    if role == "Administrator":
        return query

    raise HTTPException(
        status_code=http_status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions",
    )


def _apply_decision_filters(
    query,
    category: Optional[str],
    decision_status: Optional[str],
    created_by: Optional[int],
    date_from: Optional[datetime],
    date_to: Optional[datetime],
    tags: Optional[str],
):
    if category:
        query = query.filter(
            Decision.category == category
        )

    if decision_status:
        query = query.filter(
            Decision.status == decision_status
        )

    if created_by is not None:
        query = query.filter(
            Decision.created_by == created_by
        )

    if date_from:
        query = query.filter(
            Decision.created_at >= date_from
        )

    if date_to:
        query = query.filter(
            Decision.created_at <= date_to
        )

    if tags:
        query = query.filter(
            Decision.tags.ilike(f"%{tags}%")
        )

    return query


def _build_summary(
    db: Session,
    current_user: User,
    category: Optional[str],
    decision_status: Optional[str],
    created_by: Optional[int],
    date_from: Optional[datetime],
    date_to: Optional[datetime],
    tags: Optional[str],
):
    summary_query = (
        db.query(Decision.id)
        .join(
            User,
            Decision.created_by == User.id,
        )
        .outerjoin(
            Approval,
            Approval.decision_id == Decision.id,
        )
    )

    summary_query = _apply_authorization_scope(
        summary_query,
        current_user,
    )

    summary_query = _apply_decision_filters(
        summary_query,
        category=category,
        decision_status=decision_status,
        created_by=created_by,
        date_from=date_from,
        date_to=date_to,
        tags=tags,
    )

    # Use a distinct decision subquery so multiple approvals
    # cannot duplicate summary counts.
    decision_ids = (
        summary_query
        .distinct()
        .subquery()
    )

    summary_counts = (
        db.query(
            func.count(Decision.id).label("total"),

            func.sum(
                case(
                    (func.lower(Decision.status) == "draft", 1),
                    else_=0,
                )
            ).label("draft"),

            func.sum(
                case(
                    (func.lower(Decision.status) == "under review", 1),
                    else_=0,
                )
            ).label("under_review"),

            func.sum(
                case(
                    (func.lower(Decision.status) == "approved", 1),
                    else_=0,
                )
            ).label("approved"),

            func.sum(
                case(
                    (func.lower(Decision.status) == "rejected", 1),
                    else_=0,
                )
            ).label("rejected"),

            func.sum(
                case(
                    (func.lower(Decision.status) == "archived", 1),
                    else_=0,
                )
            ).label("archived"),
        )
        .join(
            decision_ids,
            Decision.id == decision_ids.c.id,
        )
        .first()
    )

    def safe_count(value) -> int:
        return int(value or 0)

    return {
        "total": safe_count(summary_counts.total),
        "draft": safe_count(summary_counts.draft),
        "under_review": safe_count(summary_counts.under_review),
        "approved": safe_count(summary_counts.approved),
        "rejected": safe_count(summary_counts.rejected),
        "archived": safe_count(summary_counts.archived),
    }


def get_decision_report(
    db: Session,
    current_user: User,
    category: Optional[str] = None,
    status: Optional[str] = None,
    created_by: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    tags: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_date",
    sort_order: str = "desc",
):
    if current_user is None:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
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
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "date_from must be earlier than "
                "or equal to date_to"
            ),
        )

    query = (
        db.query(
            Decision,
            User.full_name.label("creator_name"),
            func.count(
                func.distinct(Alternative.id)
            ).label("alternative_count"),
            func.count(
                func.distinct(Approval.id)
            ).label("approval_count"),
        )
        .join(
            User,
            Decision.created_by == User.id,
        )
        .outerjoin(
            Alternative,
            Alternative.decision_id == Decision.id,
        )
        .outerjoin(
            Approval,
            Approval.decision_id == Decision.id,
        )
        .group_by(
            Decision.id,
            User.full_name,
        )
    )

    # ------------------------------------------------------------
    # Authorization scope
    # ------------------------------------------------------------
    #
    # Employee:
    #     only decisions created by the current employee.
    #
    # Reviewer:
    #     only decisions having an approval assigned to the
    #     current reviewer.
    #
    # Manager:
    #     only decisions created by users in the manager's
    #     department.
    #
    # Administrator:
    #     system-wide access.
    #
    query = _apply_authorization_scope(
        query,
        current_user,
    )

    # ------------------------------------------------------------
    # Report filters
    # ------------------------------------------------------------

    query = _apply_decision_filters(
        query,
        category=category,
        decision_status=status,
        created_by=created_by,
        date_from=date_from,
        date_to=date_to,
        tags=tags,
    )

    total_records = query.count()

    sort_column = VALID_SORT_FIELDS[sort_by]

    if sort_order == "asc":
        query = query.order_by(
            sort_column.asc(),
            Decision.id.asc(),
        )
    else:
        query = query.order_by(
            sort_column.desc(),
            Decision.id.desc(),
        )

    offset = (page - 1) * page_size

    rows = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    data = []

    for (
        decision,
        creator_name,
        alternative_count,
        approval_count,
    ) in rows:
        data.append(
            {
                "decision_id": decision.id,
                "title": decision.title,
                "category": decision.category,
                "status": decision.status,
                "created_by": creator_name,
                "created_date": decision.created_at,
                "updated_date": decision.updated_at,
                "number_of_alternatives": int(
                    alternative_count or 0
                ),
                "number_of_approvals": int(
                    approval_count or 0
                ),
                "tags": decision.tags,
            }
        )

    summary = _build_summary(
        db=db,
        current_user=current_user,
        category=category,
        decision_status=status,
        created_by=created_by,
        date_from=date_from,
        date_to=date_to,
        tags=tags,
    )

    return {
        "data": data,
        "summary": summary,
        "page": page,
        "page_size": page_size,
        "total_records": total_records,
    }