from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.schemas.activity import ActivityResponse, PaginatedActivities
from app.utils.security import get_current_user


router = APIRouter(tags=["Activities"])


@router.get("/activities", response_model=PaginatedActivities)
def get_activities(
    user_id: Optional[int] = Query(default=None),
    action: Optional[str] = Query(default=None),
    entity_type: Optional[str] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date must not be after end_date"
        )

    query = db.query(ActivityLog)

    # Non-admins can only ever see their own activity, regardless of
    # what user_id they pass in — this enforces the authorization rule
    # from the brief rather than trusting the client.
    if current_user.role == "Administrator":
        if user_id is not None:
            target_user = db.query(User).filter(User.id == user_id).first()
            if target_user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            query = query.filter(ActivityLog.user_id == user_id)
    else:
        query = query.filter(ActivityLog.user_id == current_user.id)

    if action is not None:
        query = query.filter(ActivityLog.action == action)

    if entity_type is not None:
        query = query.filter(ActivityLog.entity_type == entity_type)

    if start_date is not None:
        query = query.filter(ActivityLog.created_at >= start_date)

    if end_date is not None:
        query = query.filter(ActivityLog.created_at < (end_date + timedelta(days=1)))

    query = query.order_by(ActivityLog.created_at.desc())

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedActivities(
        items=[ActivityResponse.model_validate(a) for a in items],
        page=page,
        page_size=page_size,
        total=total,
    )
