from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user

from app.models.audit_log import AuditLog
from app.models.audit_action import AuditAction
from app.models.audit_entity import AuditEntityType
from app.models.user import User

from app.schemas.audit_log import AuditLogResponse


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"]
)


@router.get(
    "",
    response_model=dict
)
def get_audit_logs(
    user_id: Optional[int] = Query(None),
    action: Optional[AuditAction] = Query(None),
    entity_type: Optional[AuditEntityType] = Query(None),
    entity_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ==========================================
    # ADMIN ONLY
    # ==========================================
    if current_user.role.value != "Administrator":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can access audit logs"
        )

    query = db.query(AuditLog)

    # ==========================================
    # FILTER BY USER
    # ==========================================
    if user_id is not None:
        query = query.filter(
            AuditLog.user_id == user_id
        )

    # ==========================================
    # FILTER BY ACTION
    # ==========================================
    if action is not None:
        query = query.filter(
            AuditLog.action == action.value
        )

    # ==========================================
    # FILTER BY ENTITY TYPE
    # ==========================================
    if entity_type is not None:
        query = query.filter(
            AuditLog.entity_type == entity_type.value
        )

    # ==========================================
    # FILTER BY ENTITY ID
    # ==========================================
    if entity_id is not None:
        query = query.filter(
            AuditLog.entity_id == entity_id
        )

    # ==========================================
    # FILTER BY START DATE
    # ==========================================
    if start_date is not None:
        query = query.filter(
            AuditLog.created_at >= start_date
        )

    # ==========================================
    # FILTER BY END DATE
    # ==========================================
    if end_date is not None:
        query = query.filter(
            AuditLog.created_at <= end_date
        )

    # ==========================================
    # TOTAL RECORDS
    # ==========================================
    total = query.count()

    # ==========================================
    # PAGINATION
    # ==========================================
    offset = (page - 1) * page_size

    logs = (
        query
        .order_by(
            AuditLog.created_at.desc()
        )
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # ==========================================
    # RESPONSE
    # ==========================================
    return {
        "items": [
            AuditLogResponse.model_validate(log)
            for log in logs
        ],
        "page": page,
        "page_size": page_size,
        "total": total
    }