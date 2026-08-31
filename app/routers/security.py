from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.enums import SecurityEventType, UserRole
from app.models.security_log import SecurityLog
from app.models.user import User
from app.schemas.security_log import SecurityLogResponse
from app.services.audit import log_security

router = APIRouter(
    prefix="/security",
    tags=["Security"],
)


@router.get(
    "/logs",
    response_model=List[SecurityLogResponse],
)
def list_security_logs(
    request: Request,
    event_type: Optional[SecurityEventType] = None,
    user_id: Optional[int] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in (UserRole.ADMINISTRATOR, UserRole.MANAGER):
        log_security(
            db,
            "unauthorized_access",
            user_id=current_user.id,
            description=f"User '{current_user.email}' attempted to access security logs",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view security logs",
        )

    query = db.query(SecurityLog)

    if event_type is not None:
        query = query.filter(SecurityLog.event_type == event_type.value)
    if user_id is not None:
        query = query.filter(SecurityLog.user_id == user_id)

    logs = (
        query.order_by(SecurityLog.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return logs


@router.get(
    "/logs/{log_id}",
    response_model=SecurityLogResponse,
)
def get_security_log(
    log_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in (UserRole.ADMINISTRATOR, UserRole.MANAGER):
        log_security(
            db,
            "unauthorized_access",
            user_id=current_user.id,
            description=f"User '{current_user.email}' attempted to access security log {log_id}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view security logs",
        )

    log = db.query(SecurityLog).filter(SecurityLog.id == log_id).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Security log not found",
        )
    return log
