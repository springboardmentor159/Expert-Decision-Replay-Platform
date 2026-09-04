from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.security_log import SecurityLog


router = APIRouter(
    prefix="/security-logs",
    tags=["Security Logs"],
)


# ============================================================
# GET SECURITY LOGS
# ADMIN ONLY
# ============================================================

@router.get("")
def get_security_logs(
    user_id: int | None = Query(default=None),
    event_type: str | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ========================================================
    # RBAC - ADMIN ONLY
    # ========================================================

    if current_user.role.lower() not in {
        "admin",
        "administrator",
    }:
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    # ========================================================
    # VALIDATE DATE RANGE
    # ========================================================

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be greater than end_date",
        )

    # ========================================================
    # BUILD QUERY
    # ========================================================

    query = db.query(SecurityLog)

    if user_id is not None:
        query = query.filter(
            SecurityLog.user_id == user_id
        )

    if event_type:
        event_type = event_type.upper()

        allowed_events = {
            "LOGIN_SUCCESS",
            "LOGIN_FAILED",
            "LOGOUT",
            "INVALID_JWT",
            "UNAUTHORIZED_ACCESS",
            "FORBIDDEN_ACCESS",
        }

        if event_type not in allowed_events:
            raise HTTPException(
                status_code=422,
                detail="Invalid security event type",
            )

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

    # ========================================================
    # TOTAL
    # ========================================================

    total = query.count()

    # ========================================================
    # PAGINATION
    # ========================================================

    offset = (page - 1) * page_size

    logs = (
        query
        .order_by(SecurityLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "items": logs,
        "page": page,
        "page_size": page_size,
        "total": total,
    }