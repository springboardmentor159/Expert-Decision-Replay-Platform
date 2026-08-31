from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit import AuditAction, AuditEntityType, AuditLogResponse, PaginatedAuditLogsResponse
from app.services.audit_service import log_access_event

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit & Compliance"]
)

VALID_ACTIONS = {a.value for a in AuditAction}
VALID_ENTITY_TYPES = {
    "Decision",
    "Alternative",
    "Comment",
    "DiscussionThread",
    "MeetingNote",
    "Approval",
    "User",
    "Tag",
    "AuditLog",
    "SecurityLog",
    "AccessLog",
}


def _parse_date(date_str: Optional[str], param_name: str) -> Optional[datetime]:
    if not date_str or not date_str.strip():
        return None
    cleaned = date_str.strip()
    try:
        return datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
    except ValueError:
        try:
            return datetime.strptime(cleaned, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid date format for '{param_name}': '{date_str}'. Expected YYYY-MM-DD or ISO 8601"
            )


def _to_audit_response(log: AuditLog) -> AuditLogResponse:
    return AuditLogResponse(
        id=log.id,
        user_id=log.user_id,
        user_name=log.user.full_name if log.user else None,
        action=log.action,
        entity_type=log.entity_type,
        entity_id=log.entity_id,
        description=log.description,
        ip_address=log.ip_address,
        old_value=log.old_value,
        new_value=log.new_value,
        request_method=log.request_method,
        endpoint=log.endpoint,
        created_at=log.created_at,
    )


@router.get(
    "",
    response_model=PaginatedAuditLogsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get paginated system-wide audit logs with filters (Administrator Only)"
)
def get_audit_logs(
    request: Request,
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action (CREATE, UPDATE, DELETE, APPROVE, REJECT, SUBMIT, LOGIN, etc.)"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (Decision, Alternative, Comment, etc.)"),
    entity_id: Optional[int] = Query(None, description="Filter by entity ID"),
    start_date: Optional[str] = Query(None, description="Filter from start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter up to end date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # RBAC: Only Administrators can view audit logs
    if current_user.role != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Only Administrators can view system audit logs"
        )

    # Validate action if supplied
    if action and action.strip():
        act_upper = action.strip().upper()
        if act_upper not in VALID_ACTIONS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid action filter '{action}'. Allowed: {', '.join(sorted(VALID_ACTIONS))}"
            )
        action_filter = act_upper
    else:
        action_filter = None

    # Validate entity_type if supplied
    if entity_type and entity_type.strip():
        clean_entity = entity_type.strip()
        matched = next((e for e in VALID_ENTITY_TYPES if e.lower() == clean_entity.lower()), None)
        if not matched:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid entity_type filter '{entity_type}'. Allowed: {', '.join(sorted(VALID_ENTITY_TYPES))}"
            )
        entity_type_filter = matched
    else:
        entity_type_filter = None

    # Validate date range
    start_dt = _parse_date(start_date, "start_date")
    end_dt = _parse_date(end_date, "end_date")
    if start_dt and end_dt and start_dt > end_dt:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )

    # Validate user exists if user_id filter is passed
    if user_id is not None:
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

    query = db.query(AuditLog)

    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)

    if action_filter:
        query = query.filter(AuditLog.action == action_filter)

    if entity_type_filter:
        query = query.filter(AuditLog.entity_type == entity_type_filter)

    if entity_id is not None:
        query = query.filter(AuditLog.entity_id == entity_id)

    if start_dt:
        query = query.filter(AuditLog.created_at >= start_dt)
    if end_dt:
        query = query.filter(AuditLog.created_at <= end_dt)

    total = query.count()
    items = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # Track Access Log for viewing audit logs
    client_ip = request.client.host if request.client else None
    log_access_event(
        db=db,
        user_id=current_user.id,
        resource_type="AuditLog",
        resource_id=None,
        action="ACCESS",
        ip_address=client_ip
    )

    return PaginatedAuditLogsResponse(
        items=[_to_audit_response(item) for item in items],
        page=page,
        page_size=page_size,
        total=total
    )
