from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.db.database import get_db
from app.models.access_log import AccessLog
from app.schemas.access_log import AccessLogListResponse

router = APIRouter(
prefix="/access-logs",
tags=["Access Logs"],
)

@router.get("", response_model=AccessLogListResponse)
def get_access_logs(
    user_id: int | None = Query(default=None, ge=1),
    resource_type: str | None = Query(default=None),
    resource_id: int | None = Query(default=None, ge=1),
    action: str | None = Query(default=None),
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

    query = db.query(AccessLog)

    if user_id is not None:
        query = query.filter(AccessLog.user_id == user_id)

    if resource_type is not None:
        query = query.filter(AccessLog.resource_type == resource_type)

    if resource_id is not None:
        query = query.filter(AccessLog.resource_id == resource_id)

    if action is not None:
        query = query.filter(AccessLog.action == action)

    if start_date is not None:
        query = query.filter(AccessLog.created_at >= start_date)

    if end_date is not None:
        query = query.filter(AccessLog.created_at <= end_date)

    total = query.count()

    offset = (page - 1) * page_size

    items = (
        query
        .order_by(AccessLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {
        "items": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "action": log.action,
                "ip_address": log.ip_address,
                "created_at": log.created_at,
            }
            for log in items
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }
