from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.activity_log import ActivityLog


router = APIRouter(
    prefix="/activities",
    tags=["Activities"]
)


@router.get("")
def get_activities(
    user_id: int | None = None,
    action: str | None = None,
    entity_type: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    current_user_id = int(current_user["sub"])
    role = str(current_user.get("role", "")).lower()

    query = db.query(ActivityLog)

    # Only administrators can view organization-wide activities
    if role not in ["administrator", "admin"]:
        query = query.filter(
            ActivityLog.user_id == current_user_id
        )

    if user_id:
        if role not in ["administrator", "admin"]:
            if user_id != current_user_id:
                raise HTTPException(
                    status_code=403,
                    detail="You cannot view another user's activities"
                )

        query = query.filter(
            ActivityLog.user_id == user_id
        )

    if action:
        query = query.filter(
            ActivityLog.action == action
        )

    if entity_type:
        query = query.filter(
            ActivityLog.entity_type == entity_type
        )

    if start_date:
        query = query.filter(
            ActivityLog.created_at >= start_date
        )

    if end_date:
        query = query.filter(
            ActivityLog.created_at <= end_date
        )

    activities = (
        query
        .order_by(ActivityLog.created_at.desc())
        .limit(100)
        .all()
    )

    return [
        {
            "id": activity.id,
            "user_id": activity.user_id,
            "action": activity.action,
            "entity_type": activity.entity_type,
            "entity_id": activity.entity_id,
            "description": activity.description,
            "created_at": activity.created_at
        }
        for activity in activities
    ]