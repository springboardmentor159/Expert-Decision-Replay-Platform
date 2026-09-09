from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user

from app.models.access_log import AccessLog
from app.models.user import User

from app.schemas.access_log import AccessLogResponse


router = APIRouter(
    prefix="/access-logs",
    tags=["Access Logs"]
)


@router.get(
    "",
    response_model=dict
)
def get_access_logs(
    user_id: Optional[int] = Query(None),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ==========================================
    # ADMIN ONLY
    # ==========================================
    if current_user.role.value != "Administrator":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can access access logs"
        )

    query = db.query(AccessLog)

    # ==========================================
    # FILTER BY USER
    # ==========================================
    if user_id is not None:
        query = query.filter(
            AccessLog.user_id == user_id
        )

    # ==========================================
    # FILTER BY RESOURCE TYPE
    # ==========================================
    if resource_type is not None:
        query = query.filter(
            AccessLog.resource_type == resource_type
        )

    # ==========================================
    # FILTER BY RESOURCE ID
    # ==========================================
    if resource_id is not None:
        query = query.filter(
            AccessLog.resource_id == resource_id
        )

    # ==========================================
    # FILTER BY ACTION
    # ==========================================
    if action is not None:
        query = query.filter(
            AccessLog.action == action
        )

    # ==========================================
    # FILTER BY START DATE
    # ==========================================
    if start_date is not None:
        query = query.filter(
            AccessLog.created_at >= start_date
        )

    # ==========================================
    # FILTER BY END DATE
    # ==========================================
    if end_date is not None:
        query = query.filter(
            AccessLog.created_at <= end_date
        )

    # ==========================================
    # TOTAL RECORDS
    # ==========================================
    total = query.count()

    # ==========================================
    # PAGINATION
    # ==========================================
    offset = (page - 1) * page_size

    logs = (
        query
        .order_by(
            AccessLog.created_at.desc()
        )
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # ==========================================
    # RESPONSE
    # ==========================================
    return {
        "items": [
            AccessLogResponse.model_validate(log)
            for log in logs
        ],
        "page": page,
        "page_size": page_size,
        "total": total
    }