from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.activity import Activity
from app.models.user import User
from app.schemas.activity import ActivityResponse
from datetime import datetime
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Query
)

router = APIRouter(
    prefix="/activities",
    tags=["Activities"]
)


@router.get(
    "",
    response_model=list[ActivityResponse]
)
def get_activities(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
            Activity.action == action
        )

    if entity_type:
        query = query.filter(
            Activity.entity_type == entity_type
        )

    if start_date:
        query = query.filter(
            Activity.created_at >= start_date
        )

    if end_date:
        query = query.filter(
            Activity.created_at <= end_date
        )

    return (
        query
        .order_by(Activity.created_at.desc())
        .all()
    )