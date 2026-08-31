from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import PaginatedAuditLogResponse
from app.services.audit_service import (
    VALID_AUDIT_ACTIONS,
    VALID_ENTITY_TYPES,
    get_client_ip,
    log_access_event,
)

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit & Compliance"]
)


@router.get(
    "",
    response_model=PaginatedAuditLogResponse,
    summary="Get system audit logs with filtering and pagination"
)
def get_audit_logs(
    request: Request,
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action type (CREATE, UPDATE, DELETE, etc.)"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (Decision, Alternative, etc.)"),
    entity_id: Optional[int] = Query(None, description="Filter by entity ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Only Administrators are allowed to view audit logs
    if current_user.role != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Only administrators can view audit logs"
        )

    query = db.query(AuditLog)

    if user_id is not None:
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        query = query.filter(AuditLog.user_id == user_id)

    if action:
        normalized_action = action.upper().strip()
        if normalized_action not in VALID_AUDIT_ACTIONS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid action '{action}'. Allowed actions: {sorted(list(VALID_AUDIT_ACTIONS))}"
            )
        query = query.filter(AuditLog.action == normalized_action)

    if entity_type:
        normalized_entity = entity_type.strip()
        # Case insensitive match for valid entity types
        matched = [e for e in VALID_ENTITY_TYPES if e.lower() == normalized_entity.lower()]
        if not matched:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid entity_type '{entity_type}'. Allowed types: {sorted(list(VALID_ENTITY_TYPES))}"
            )
        query = query.filter(AuditLog.entity_type.ilike(matched[0]))

    if entity_id is not None:
        query = query.filter(AuditLog.entity_id == entity_id)

    # Date range parsing and validation
    if start_date:
        try:
            parsed_start = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(AuditLog.created_at >= parsed_start)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid start_date format. Expected YYYY-MM-DD"
            )

    if end_date:
        try:
            parsed_end = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            query = query.filter(AuditLog.created_at <= parsed_end)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid end_date format. Expected YYYY-MM-DD"
            )

    if start_date and end_date:
        if parsed_start > parsed_end:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="start_date cannot be after end_date"
            )

    total = query.count()
    items = (
        query.order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # Log access event
    client_ip = get_client_ip(request)
    log_access_event(
        db=db,
        user_id=current_user.id,
        resource_type="AuditLog",
        resource_id=None,
        action="LIST",
        ip_address=client_ip
    )

    return PaginatedAuditLogResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )
