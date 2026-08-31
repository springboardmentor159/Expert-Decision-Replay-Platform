import math
from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.audit_log import AuditLog
from app.models.enums import AuditAction, AuditEntityType, UserRole
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse, PaginatedAuditLogResponse
from app.services.audit import log_security

router = APIRouter(
    prefix="/audit",
    tags=["Audit"],
)

audit_logs_router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit"],
)


def _parse_date(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        d = date.fromisoformat(value)
        return datetime(d.year, d.month, d.day)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid date format: '{value}'. Expected YYYY-MM-DD.",
        )


@router.get(
    "/logs",
    response_model=List[AuditLogResponse],
)
def list_audit_logs(
    action: Optional[AuditAction] = None,
    entity_type: Optional[AuditEntityType] = None,
    user_id: Optional[int] = None,
    entity_id: Optional[int] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(AuditLog)

    if current_user.role not in (UserRole.ADMINISTRATOR, UserRole.MANAGER):
        query = query.filter(AuditLog.user_id == current_user.id)

    if action is not None:
        query = query.filter(AuditLog.action == action.value)
    if entity_type is not None:
        query = query.filter(AuditLog.entity_type == entity_type.value)
    if user_id is not None and current_user.role in (
        UserRole.ADMINISTRATOR,
        UserRole.MANAGER,
    ):
        query = query.filter(AuditLog.user_id == user_id)
    if entity_id is not None:
        query = query.filter(AuditLog.entity_id == entity_id)

    logs = (
        query.order_by(AuditLog.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return logs


@router.get(
    "/logs/{log_id}",
    response_model=AuditLogResponse,
)
def get_audit_log(
    log_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found",
        )
    if (
        current_user.role not in (UserRole.ADMINISTRATOR, UserRole.MANAGER)
        and log.user_id != current_user.id
    ):
        log_security(
            db,
            "unauthorized_access",
            user_id=current_user.id,
            description=f"User '{current_user.email}' attempted to access audit log {log_id}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this audit log",
        )
    return log


@audit_logs_router.get(
    "",
    response_model=PaginatedAuditLogResponse,
)
def list_audit_logs_paginated(
    request: Request,
    user: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[AuditAction] = Query(None, description="Filter by audit action"),
    entity_type: Optional[AuditEntityType] = Query(None, description="Filter by entity type"),
    entity_id: Optional[int] = Query(None, description="Filter by entity ID"),
    start_date: Optional[str] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sd = _parse_date(start_date)
    ed = _parse_date(end_date)

    if sd and ed and sd > ed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date must not be after end_date.",
        )

    query = db.query(AuditLog)

    if current_user.role not in (UserRole.ADMINISTRATOR, UserRole.MANAGER):
        query = query.filter(AuditLog.user_id == current_user.id)
    elif user is not None:
        query = query.filter(AuditLog.user_id == user)

    if action is not None:
        query = query.filter(AuditLog.action == action.value)
    if entity_type is not None:
        query = query.filter(AuditLog.entity_type == entity_type.value)
    if entity_id is not None:
        query = query.filter(AuditLog.entity_id == entity_id)
    if sd:
        query = query.filter(AuditLog.created_at >= sd)
    if ed:
        query = query.filter(AuditLog.created_at < ed + timedelta(days=1))

    total = query.count()
    pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size

    items = (
        query.order_by(AuditLog.id.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return PaginatedAuditLogResponse(
        items=[AuditLogResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@audit_logs_router.get(
    "/{log_id}",
    response_model=AuditLogResponse,
)
def get_audit_log_by_id(
    log_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found",
        )
    if (
        current_user.role not in (UserRole.ADMINISTRATOR, UserRole.MANAGER)
        and log.user_id != current_user.id
    ):
        log_security(
            db,
            "unauthorized_access",
            user_id=current_user.id,
            description=f"User '{current_user.email}' attempted to access audit log {log_id}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this audit log",
        )
    return log
