from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.activity import Activity
from app.models.user import User
from app.schemas.activity import ActivityResponse


router = APIRouter(
    prefix="/activities",
    tags=["Activities"],
)


@router.get(
    "",
    response_model=list[ActivityResponse],
)
def get_activities(
    user_id: Optional[int] = Query(default=None, ge=1),
    action: Optional[str] = Query(default=None),
    entity_type: Optional[str] = Query(default=None),
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return activity records visible to the authenticated user.

    Administrators can view all activity.
    Managers can view activity from users in their department.
    Employees and Reviewers can view only their own activity.
    """

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date must be earlier than or equal to end_date",
        )

    query = db.query(Activity)

    if current_user.role == "Administrator":
        if user_id is not None:
            query = query.filter(
                Activity.user_id == user_id
            )

    elif current_user.role == "Manager":
        query = (
            query
            .join(User, Activity.user_id == User.id)
            .filter(User.department == current_user.department)
        )

        if user_id is not None:
            query = query.filter(
                Activity.user_id == user_id
            )

    else:
        query = query.filter(
            Activity.user_id == current_user.id
        )

    if action:
        query = query.filter(
            Activity.action == action.strip()
        )

    if entity_type:
        query = query.filter(
            Activity.entity_type == entity_type.strip()
        )

    if start_date:
        query = query.filter(
            Activity.created_at >= start_date
        )

    if end_date:
        query = query.filter(
            Activity.created_at <= end_date
        )

    offset = (page - 1) * page_size

    return (
        query
        .order_by(
            Activity.created_at.desc(),
            Activity.id.desc(),
        )
        .offset(offset)
        .limit(page_size)
        .all()
    )