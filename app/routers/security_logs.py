
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.db.database import get_db
from app.models.security_log import SecurityLog
from app.schemas.security_log import SecurityLogListResponse


router = APIRouter(
    prefix="/security-logs",
    tags=["Security Logs"],
)


@router.get("", response_model=SecurityLogListResponse)
def get_security_logs(
    event_type: str | None = Query(default=None),
    user_id: int | None = Query(default=None, ge=1),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("Administrator")),
):
    if (
        start_date is not None
        and end_date is not None
        and end_date < start_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_date must be greater than or equal to start_date",
        )

    query = db.query(SecurityLog)

    if event_type is not None:
        query = query.filter(SecurityLog.event_type == event_type)

    if user_id is not None:
        query = query.filter(SecurityLog.user_id == user_id)

    if start_date is not None:
        query = query.filter(SecurityLog.created_at >= start_date)

    if end_date is not None:
        query = query.filter(SecurityLog.created_at <= end_date)

    total = query.count()

    offset = (page - 1) * page_size

    items = (
        query
        .order_by(SecurityLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {
        "items": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "event_type": log.event_type,
                "description": log.description,
                "ip_address": log.ip_address,
                "created_at": log.created_at,
            }
            for log in items
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }
