from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User


VALID_SORT_FIELDS = {
    "created_date": AuditLog.created_at,
}


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
):
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