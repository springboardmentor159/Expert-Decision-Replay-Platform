from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.security_log import SecurityLog
from app.models.user import User
from app.schemas.security_log import PaginatedSecurityLogsResponse, SecurityEventType, SecurityLogResponse

router = APIRouter(
    prefix="/security-logs",
    tags=["Audit & Compliance"]
)

VALID_EVENT_TYPES = {e.value for e in SecurityEventType}


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


def _to_security_response(log: SecurityLog) -> SecurityLogResponse:
    return SecurityLogResponse(
        id=log.id,
        user_id=log.user_id,
        user_name=log.user.full_name if log.user else None,
        event_type=log.event_type,
        description=log.description,
        ip_address=log.ip_address,
        created_at=log.created_at,
    )


@router.get(
    "",
    response_model=PaginatedSecurityLogsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get system security logs with filters (Administrator Only)"
)
def get_security_logs(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type (LOGIN_SUCCESS, LOGIN_FAILED, etc.)"),
    start_date: Optional[str] = Query(None, description="Filter from start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter up to end date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # RBAC: Only Administrators can view security logs
    if current_user.role != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Only Administrators can view security logs"
        )

    # Validate event_type if supplied
    if event_type and event_type.strip():
        et_upper = event_type.strip().upper()
        if et_upper not in VALID_EVENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid event_type '{event_type}'. Allowed: {', '.join(sorted(VALID_EVENT_TYPES))}"
            )
        event_type_filter = et_upper
    else:
        event_type_filter = None

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

    query = db.query(SecurityLog)

    if user_id is not None:
        query = query.filter(SecurityLog.user_id == user_id)

    if event_type_filter:
        query = query.filter(SecurityLog.event_type == event_type_filter)

    if start_dt:
        query = query.filter(SecurityLog.created_at >= start_dt)
    if end_dt:
        query = query.filter(SecurityLog.created_at <= end_dt)

    total = query.count()
    items = query.order_by(SecurityLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedSecurityLogsResponse(
        items=[_to_security_response(item) for item in items],
        page=page,
        page_size=page_size,
        total=total
    )
