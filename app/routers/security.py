from typing import Optional
from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.security_log import SecurityLog
from app.models.access_log import AccessLog
from app.core.security import get_current_user
from app.core.enums import UserRole


router = APIRouter(
    prefix="/security",
    tags=["Security & Access"]
)


# =========================================================
# ADMIN AUTHORIZATION
# =========================================================

def require_admin(current_user: User):
    if current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required"
        )


# =========================================================
# SECURITY LOGS
# =========================================================

@router.get("/logs")
def get_security_logs(
    user_id: Optional[int] = Query(
        None,
        ge=1
    ),

    event_type: Optional[str] = Query(
        None,
        min_length=1
    ),

    start_date: Optional[datetime] = Query(
        None
    ),

    end_date: Optional[datetime] = Query(
        None
    ),

    page: int = Query(
        1,
        ge=1
    ),

    page_size: int = Query(
        20,
        ge=1,
        le=100
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    """
    Retrieve security logs.

    Security logs are restricted to administrators.
    """

    require_admin(current_user)

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be later than end_date"
        )

    query = db.query(SecurityLog)

    if user_id:
        query = query.filter(
            SecurityLog.user_id == user_id
        )

    if event_type:
        query = query.filter(
            SecurityLog.event_type == event_type
        )

    if start_date:
        query = query.filter(
            SecurityLog.created_at >= start_date
        )

    if end_date:
        query = query.filter(
            SecurityLog.created_at <= end_date
        )

    total = query.count()

    offset = (page - 1) * page_size

    logs = query.order_by(
        SecurityLog.created_at.desc()
    ).offset(
        offset
    ).limit(
        page_size
    ).all()

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "count": len(logs),
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "event_type": log.event_type,
                "description": log.description,
                "ip_address": log.ip_address,
                "created_at": log.created_at
            }
            for log in logs
        ]
    }


# =========================================================
# ACCESS LOGS
# =========================================================

@router.get("/access-logs")
def get_access_logs(
    user_id: Optional[int] = Query(
        None,
        ge=1
    ),

    resource_type: Optional[str] = Query(
        None,
        min_length=1
    ),

    resource_id: Optional[int] = Query(
        None,
        ge=1
    ),

    action: Optional[str] = Query(
        None,
        min_length=1
    ),

    start_date: Optional[datetime] = Query(
        None
    ),

    end_date: Optional[datetime] = Query(
        None
    ),

    page: int = Query(
        1,
        ge=1
    ),

    page_size: int = Query(
        20,
        ge=1,
        le=100
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    """
    Retrieve access logs.

    Access logs are restricted to administrators.
    """

    require_admin(current_user)

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be later than end_date"
        )

    query = db.query(AccessLog)

    if user_id:
        query = query.filter(
            AccessLog.user_id == user_id
        )

    if resource_type:
        query = query.filter(
            AccessLog.resource_type == resource_type
        )

    if resource_id:
        query = query.filter(
            AccessLog.resource_id == resource_id
        )

    if action:
        query = query.filter(
            AccessLog.action == action
        )

    if start_date:
        query = query.filter(
            AccessLog.created_at >= start_date
        )

    if end_date:
        query = query.filter(
            AccessLog.created_at <= end_date
        )

    total = query.count()

    offset = (page - 1) * page_size

    logs = query.order_by(
        AccessLog.created_at.desc()
    ).offset(
        offset
    ).limit(
        page_size
    ).all()

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "count": len(logs),
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "action": log.action,
                "ip_address": log.ip_address,
                "created_at": log.created_at
            }
            for log in logs
        ]
    }
