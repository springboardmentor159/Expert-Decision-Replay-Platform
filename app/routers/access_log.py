from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.access_log import AccessLog
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.access_log import AccessLogResponse
from app.services.audit import log_security

router = APIRouter(
    prefix="/access",
    tags=["Access"],
)


@router.get(
    "/logs",
    response_model=List[AccessLogResponse],
)
def list_access_logs(
    request: Request,
    method: Optional[str] = None,
    path: Optional[str] = None,
    status_code: Optional[int] = None,
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
            description=f"User '{current_user.email}' attempted to access access logs",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view access logs",
        )

    query = db.query(AccessLog)

    if method is not None:
        query = query.filter(AccessLog.method == method.upper())
    if path is not None:
        query = query.filter(AccessLog.path.ilike(f"%{path}%"))
    if status_code is not None:
        query = query.filter(AccessLog.status_code == status_code)
    if user_id is not None:
        query = query.filter(AccessLog.user_id == user_id)

    logs = (
        query.order_by(AccessLog.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return logs


@router.get(
    "/logs/{log_id}",
    response_model=AccessLogResponse,
)
def get_access_log(
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
            description=f"User '{current_user.email}' attempted to access access log {log_id}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view access logs",
        )

    log = db.query(AccessLog).filter(AccessLog.id == log_id).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access log not found",
        )
    return log
