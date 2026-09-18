from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User


VALID_SORT_FIELDS = {
    "created_date": AuditLog.created_at,
}

VALID_SORT_ORDERS = {"asc", "desc"}

ALLOWED_ROLES = {"Administrator"}


def validate_access(
    current_user: Optional[User],
) -> None:
    """Ensure that only authenticated administrators can access audit reports."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    if current_user.role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )


def validate_sorting(
    sort_by: str,
    sort_order: str,
) -> None:
    """Validate audit report sorting parameters."""
    if sort_by not in VALID_SORT_FIELDS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Invalid sort_by '{sort_by}'. "
                f"Allowed values: {', '.join(VALID_SORT_FIELDS.keys())}"
            ),
        )

    if sort_order not in VALID_SORT_ORDERS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Invalid sort_order '{sort_order}'. "
                "Allowed values: asc, desc"
            ),
        )


def validate_date_range(
    date_from: Optional[datetime],
    date_to: Optional[datetime],
) -> None:
    """Validate the requested audit report date range."""
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="date_from cannot be later than date_to",
        )


def validate_pagination(
    page: int,
    page_size: int,
) -> None:
    """Validate pagination parameters."""
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


def get_audit_report(
    db: Session,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_date",
    sort_order: str = "desc",
    current_user: Optional[User] = None,
):
    """
    Generate the administrator audit report.

    Audit reports are system-wide and therefore restricted to
    Administrator users. Filtering, pagination, and sorting are
    applied to the administrator-visible audit dataset.
    """
    validate_access(current_user)
    validate_sorting(sort_by, sort_order)
    validate_date_range(date_from, date_to)
    validate_pagination(page, page_size)

    query = (
        db.query(
            AuditLog,
            User.full_name.label("user_name"),
        )
        .join(
            User,
            AuditLog.user_id == User.id,
        )
    )

    # Filters
    if user_id is not None:
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

    if entity_id is not None:
        query = query.filter(
            AuditLog.entity_id == entity_id
        )

    if date_from:
        query = query.filter(
            AuditLog.created_at >= date_from
        )

    if date_to:
        query = query.filter(
            AuditLog.created_at <= date_to
        )

    total_records = query.count()

    # Controlled sorting
    sort_column = VALID_SORT_FIELDS[sort_by]

    if sort_order == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    offset = (page - 1) * page_size

    rows = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    data = []

    for audit_log, user_name in rows:
        data.append(
            {
                "user": user_name,
                "action": audit_log.action,
                "entity_type": audit_log.entity_type,
                "entity_id": audit_log.entity_id,
                "description": audit_log.description,
                "timestamp": audit_log.created_at,
                "ip_address": audit_log.ip_address,
            }
        )

    return {
        "data": data,
        "page": page,
        "page_size": page_size,
        "total_records": total_records,
    }