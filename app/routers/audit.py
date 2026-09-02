from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.audit_log import AuditLog
from app.models.security_log import SecurityLog
from app.models.access_log import AccessLog
from app.models.user import User
from app.schemas.audit import (
    AuditAction,
    EntityType,
    AuditLogResponse,
    PaginatedAuditLogs,
    SecurityLogResponse,
    PaginatedSecurityLogs,
    AccessLogResponse,
    PaginatedAccessLogs,
)
from app.utils.security import require_role
from app.utils.audit import log_access


router = APIRouter(tags=["Audit & Compliance"])


def _validate_date_range(start_date: Optional[date], end_date: Optional[date]) -> None:
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date must not be after end_date"
        )


# GET /audit-logs - Administrator only
@router.get(
    "/audit-logs",
    response_model=PaginatedAuditLogs
)
def get_audit_logs(
    request: Request,
    user_id: Optional[int] = Query(default=None),
    action: Optional[AuditAction] = Query(default=None),
    entity_type: Optional[EntityType] = Query(default=None),
    entity_id: Optional[int] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Administrator")),
):
    _validate_date_range(start_date, end_date)

    query = db.query(AuditLog)

    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)

    if action is not None:
        query = query.filter(AuditLog.action == action.value)

    if entity_type is not None:
        query = query.filter(AuditLog.entity_type == entity_type.value)

    if entity_id is not None:
        query = query.filter(AuditLog.entity_id == entity_id)

    if start_date is not None:
        query = query.filter(AuditLog.created_at >= start_date)

    if end_date is not None:
        query = query.filter(AuditLog.created_at < (end_date + timedelta(days=1)))

    query = query.order_by(AuditLog.created_at.desc())

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    # Administrators reading the audit trail is itself worth recording.
    log_access(
        db=db,
        user_id=current_user.id,
        resource_type="AuditLog",
        resource_id=None,
        action="LIST",
        request=request,
    )

    return PaginatedAuditLogs(
        items=[AuditLogResponse.model_validate(a) for a in items],
        page=page,
        page_size=page_size,
        total=total,
    )


# GET /security-logs - Administrator only
@router.get(
    "/security-logs",
    response_model=PaginatedSecurityLogs
)
def get_security_logs(
    event_type: Optional[str] = Query(default=None),
    user_id: Optional[int] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Administrator")),
):
    _validate_date_range(start_date, end_date)

    query = db.query(SecurityLog)

    if event_type is not None:
        query = query.filter(SecurityLog.event_type == event_type)

    if user_id is not None:
        query = query.filter(SecurityLog.user_id == user_id)

    if start_date is not None:
        query = query.filter(SecurityLog.created_at >= start_date)

    if end_date is not None:
        query = query.filter(SecurityLog.created_at < (end_date + timedelta(days=1)))

    query = query.order_by(SecurityLog.created_at.desc())

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedSecurityLogs(
        items=[SecurityLogResponse.model_validate(s) for s in items],
        page=page,
        page_size=page_size,
        total=total,
    )


# GET /access-logs - Administrator only
@router.get(
    "/access-logs",
    response_model=PaginatedAccessLogs
)
def get_access_logs(
    resource_type: Optional[str] = Query(default=None),
    user_id: Optional[int] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Administrator")),
):
    _validate_date_range(start_date, end_date)

    query = db.query(AccessLog)

    if resource_type is not None:
        query = query.filter(AccessLog.resource_type == resource_type)

    if user_id is not None:
        query = query.filter(AccessLog.user_id == user_id)

    if start_date is not None:
        query = query.filter(AccessLog.created_at >= start_date)

    if end_date is not None:
        query = query.filter(AccessLog.created_at < (end_date + timedelta(days=1)))

    query = query.order_by(AccessLog.created_at.desc())

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedAccessLogs(
        items=[AccessLogResponse.model_validate(a) for a in items],
        page=page,
        page_size=page_size,
        total=total,
    )
