from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


def require_admin(current_user: User) -> None:
    if current_user.role != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )


@router.get(
    "",
    response_model=list[AuditLogResponse],
)
def get_audit_logs(
    action: Optional[str] = Query(default=None),
    entity_type: Optional[str] = Query(default=None),
    entity_id: Optional[int] = Query(default=None, ge=1),
    user_id: Optional[int] = Query(default=None, ge=1),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return audit logs for administrators.

    Audit information is intentionally restricted to administrators because
    it may contain sensitive operational and historical information.
    """

    require_admin(current_user)

    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="date_from must be earlier than or equal to date_to",
        )

    query = db.query(AuditLog)

    if action:
        query = query.filter(
            AuditLog.action == action.strip().upper()
        )

    if entity_type:
        query = query.filter(
            AuditLog.entity_type == entity_type.strip()
        )

    if entity_id is not None:
        query = query.filter(
            AuditLog.entity_id == entity_id
        )

    if user_id is not None:
        query = query.filter(
            AuditLog.user_id == user_id
        )

    if date_from:
        query = query.filter(
            AuditLog.created_at >= date_from
        )

    if date_to:
        query = query.filter(
            AuditLog.created_at <= date_to
        )

    query = query.order_by(
        AuditLog.created_at.desc(),
        AuditLog.id.desc(),
    )

    offset = (page - 1) * page_size

    return (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )