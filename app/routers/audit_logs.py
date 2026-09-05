
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.db.database import get_db
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogListResponse


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


AuditAction = Literal[
    "CREATE",
    "UPDATE",
    "DELETE",
    "APPROVE",
    "REJECT",
    "SUBMIT",
    "LOGIN",
    "LOGOUT",
    "ACCESS",
]

AuditEntityType = Literal[
    "Decision",
    "Alternative",
    "Comment",
    "DiscussionThread",
    "MeetingNote",
    "Approval",
    "User",
]


@router.get(
    "",
    response_model=AuditLogListResponse,
)
def get_audit_logs(
    user_id: int | None = Query(default=None, ge=1),
    action: AuditAction | None = Query(default=None),
    entity_type: AuditEntityType | None = Query(default=None),
    entity_id: int | None = Query(default=None, ge=1),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_role("Administrator")
    ),
):
    if (
        start_date is not None
        and end_date is not None
        and end_date < start_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_date must be greater than or equal to start_date",
        )

    query = db.query(AuditLog)

    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)

    if action is not None:
        query = query.filter(AuditLog.action == action)

    if entity_type is not None:
        query = query.filter(
            AuditLog.entity_type == entity_type
        )

    if entity_id is not None:
        query = query.filter(
            AuditLog.entity_id == entity_id
        )

    if start_date is not None:
        query = query.filter(
            AuditLog.created_at >= start_date
        )

    if end_date is not None:
        query = query.filter(
            AuditLog.created_at <= end_date
        )

    total = query.count()

    offset = (page - 1) * page_size

    items = (
        query
        .order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
    }
