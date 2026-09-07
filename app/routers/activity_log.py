from typing import Optional

from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db

from app.models.activity_log import ActivityLog
from app.models.user import User

from app.schemas.activity_log import ActivityLogResponse


router = APIRouter(
    prefix="/activity-logs",
    tags=["Activity Logs"]
)


# ==========================================
# GET ALL ACTIVITY LOGS
# ==========================================
@router.get(
    "",
    response_model=list[ActivityLogResponse]
)
def get_activity_logs(
    user_id: Optional[int] = Query(
        default=None,
        description="Filter activities by user ID"
    ),

    action: Optional[str] = Query(
        default=None,
        description="Filter activities by action"
    ),

    entity_type: Optional[str] = Query(
        default=None,
        description="Filter activities by entity type"
    ),

    entity_id: Optional[int] = Query(
        default=None,
        description="Filter activities by entity ID"
    ),

    start_date: Optional[date] = Query(
        default=None,
        description="Start date for activity filtering"
    ),

    end_date: Optional[date] = Query(
        default=None,
        description="End date for activity filtering"
    ),

    skip: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip"
    ),

    limit: int = Query(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of records to return"
    ),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ==========================================
    # DATE VALIDATION
    # ==========================================

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be later than end_date"
        )

    # ==========================================
    # BUILD QUERY
    # ==========================================

    query = db.query(ActivityLog)

    # ==========================================
    # FILTER BY USER
    # ==========================================

    if user_id is not None:
        query = query.filter(
            ActivityLog.user_id == user_id
        )

    # ==========================================
    # FILTER BY ACTION
    # ==========================================

    if action is not None:
        query = query.filter(
            ActivityLog.action == action
        )

    # ==========================================
    # FILTER BY ENTITY TYPE
    # ==========================================

    if entity_type is not None:
        query = query.filter(
            ActivityLog.entity_type == entity_type
        )

    # ==========================================
    # FILTER BY ENTITY ID
    # ==========================================

    if entity_id is not None:
        query = query.filter(
            ActivityLog.entity_id == entity_id
        )

    # ==========================================
    # DATE RANGE
    # ==========================================

    start_datetime = None
    end_datetime = None

    if start_date:
        start_datetime = datetime.combine(
            start_date,
            time.min
        )

        query = query.filter(
            ActivityLog.created_at >= start_datetime
        )

    if end_date:
        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min
        )

        query = query.filter(
            ActivityLog.created_at < end_datetime
        )

    # ==========================================
    # ORDER + PAGINATION
    # ==========================================

    activities = (
        query
        .order_by(
            ActivityLog.created_at.desc()
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    # ==========================================
    # RETURN RESPONSE
    # ==========================================

    return activities