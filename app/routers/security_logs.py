from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.security_log import SecurityLog
from app.models.user import User
from app.schemas.security_log import PaginatedSecurityLogResponse
from app.services.audit_service import get_client_ip, log_access_event

router = APIRouter(
    prefix="/security-logs",
    tags=["Audit & Compliance"]
)


@router.get(
    "",
    response_model=PaginatedSecurityLogResponse,
    summary="Get security logs with filtering and pagination"
)
def get_security_logs(
    request: Request,
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type (LOGIN_SUCCESS, LOGIN_FAILED, etc.)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Only administrators can view security logs"
        )

    query = db.query(SecurityLog)

    if user_id is not None:
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        query = query.filter(SecurityLog.user_id == user_id)

    if event_type:
        query = query.filter(SecurityLog.event_type == event_type.upper().strip())

    if start_date:
        try:
            parsed_start = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(SecurityLog.created_at >= parsed_start)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid start_date format. Expected YYYY-MM-DD"
            )

    if end_date:
        try:
            parsed_end = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            query = query.filter(SecurityLog.created_at <= parsed_end)
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
        query.order_by(SecurityLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    client_ip = get_client_ip(request)
    log_access_event(
        db=db,
        user_id=current_user.id,
        resource_type="SecurityLog",
        resource_id=None,
        action="LIST",
        ip_address=client_ip
    )

    return PaginatedSecurityLogResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )
