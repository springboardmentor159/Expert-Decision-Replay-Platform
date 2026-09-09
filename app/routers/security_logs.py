from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user

from app.models.security_log import SecurityLog
from app.models.user import User

from app.schemas.security_log import SecurityLogResponse


router = APIRouter(
    prefix="/security-logs",
    tags=["Security Logs"]
)


@router.get(
    "",
    response_model=dict
)
def get_security_logs(
    user_id: Optional[int] = Query(None),
    event_type: Optional[str] = Query(None),
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
            detail="Only administrators can access security logs"
        )

    query = db.query(SecurityLog)

    # ==========================================
    # FILTER BY USER
    # ==========================================
    if user_id is not None:
        query = query.filter(
            SecurityLog.user_id == user_id
        )

    # ==========================================
    # FILTER BY EVENT TYPE
    # ==========================================
    if event_type is not None:
        query = query.filter(
            SecurityLog.event_type == event_type
        )

    # ==========================================
    # FILTER BY START DATE
    # ==========================================
    if start_date is not None:
        query = query.filter(
            SecurityLog.created_at >= start_date
        )

    # ==========================================
    # FILTER BY END DATE
    # ==========================================
    if end_date is not None:
        query = query.filter(
            SecurityLog.created_at <= end_date
        )

    # ==========================================
    # TOTAL
    # ==========================================
    total = query.count()

    # ==========================================
    # PAGINATION
    # ==========================================
    offset = (page - 1) * page_size

    logs = (
        query
        .order_by(
            SecurityLog.created_at.desc()
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
            SecurityLogResponse.model_validate(log)
            for log in logs
        ],
        "page": page,
        "page_size": page_size,
        "total": total
    }