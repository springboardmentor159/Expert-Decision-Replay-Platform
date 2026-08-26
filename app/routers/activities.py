from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.schemas.activity_log import PaginatedActivityLogResponse

router = APIRouter(
    prefix="/activities",
    tags=["Activities"]
)


@router.get(
    "",
    response_model=PaginatedActivityLogResponse,
    summary="Get system activity logs with filtering and pagination"
)
def get_activities(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Role-based restriction: Non-administrators only see their own activities
    query = db.query(ActivityLog)
    if current_user.role != "Administrator":
        query = query.filter(ActivityLog.user_id == current_user.id)
    elif user_id is not None:
        # If admin specified a user_id, check if user exists
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        query = query.filter(ActivityLog.user_id == user_id)

    if action:
        query = query.filter(ActivityLog.action.ilike(action.strip()))

    if entity_type:
        query = query.filter(ActivityLog.entity_type.ilike(entity_type.strip()))

    # Date range parsing & validation
    if start_date:
        try:
            parsed_start = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(ActivityLog.created_at >= parsed_start)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid start_date format. Expected YYYY-MM-DD"
            )

    if end_date:
        try:
            parsed_end = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            query = query.filter(ActivityLog.created_at <= parsed_end)
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
        query.order_by(ActivityLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedActivityLogResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )
