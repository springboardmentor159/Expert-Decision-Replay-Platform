from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"]
)


@router.get(
    "",
    response_model=list[AuditLogResponse]
)
def get_audit_logs(
    action: Optional[str] = Query(default=None),
    entity_type: Optional[str] = Query(default=None),
    entity_id: Optional[int] = Query(default=None),
    user_id: Optional[int] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(AuditLog)

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

    if user_id is not None:
        query = query.filter(
            AuditLog.user_id == user_id
        )

    query = query.order_by(
        AuditLog.created_at.desc()
    )

    offset = (page - 1) * page_size

    return query.offset(offset).limit(page_size).all()