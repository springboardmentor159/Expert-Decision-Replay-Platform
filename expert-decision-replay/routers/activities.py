from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/activities",
    tags=["Activities"]
)


# =========================================================
# GET ACTIVITIES
# =========================================================

@router.get("/")
def get_activities(
    user_id: int | None = Query(default=None),
    action: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ActivityLog)

    # -----------------------------------------------------
    # Admin can view organization-wide activities
    # Normal users can view only their own activities
    # -----------------------------------------------------

    role = (
        current_user.role.value
        if hasattr(current_user.role, "value")
        else current_user.role
    )

    if role != "Admin":
        query = query.filter(
            ActivityLog.user_id == current_user.id
        )
    elif user_id is not None:
        query = query.filter(
            ActivityLog.user_id == user_id
        )

    # -----------------------------------------------------
    # Filters
    # -----------------------------------------------------

    if action is not None:
        query = query.filter(
            ActivityLog.action == action
        )

    if entity_type is not None:
        query = query.filter(
            ActivityLog.entity_type == entity_type
        )

    if start_date is not None:
        query = query.filter(
            ActivityLog.created_at >= start_date
        )

    if end_date is not None:
        query = query.filter(
            ActivityLog.created_at <= end_date
        )

    activities = (
        query
        .order_by(ActivityLog.created_at.desc())
        .all()
    )

    return activities