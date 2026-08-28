from datetime import datetime, date, time
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Query,
    HTTPException,
    status
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.activity import Activity
from app.models.user import User


router = APIRouter(
    prefix="/activities",
    tags=["Activities"]
)


# ============================================================
# GET ALL ACTIVITIES
# GET /activities
# ============================================================

@router.get("")
def get_activities(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # --------------------------------------------------------
    # VALIDATE DATE RANGE
    # --------------------------------------------------------

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )

    # --------------------------------------------------------
    # START QUERY
    # --------------------------------------------------------

    query = db.query(Activity)

    # --------------------------------------------------------
    # CHECK USER ROLE
    # --------------------------------------------------------

    user_role = str(
        current_user.role
    ).strip().lower()

    # --------------------------------------------------------
    # ADMIN
    # Admin can see all activities
    # --------------------------------------------------------

    if user_role in [
        "admin",
        "administrator"
    ]:

        if user_id is not None:
            query = query.filter(
                Activity.user_id == user_id
            )

    # --------------------------------------------------------
    # EMPLOYEE / MANAGER
    # They can see only their own activities
    # --------------------------------------------------------

    else:

        query = query.filter(
            Activity.user_id == current_user.id
        )

    # --------------------------------------------------------
    # FILTER BY ACTION
    # --------------------------------------------------------

    if action:

        query = query.filter(
            Activity.action == action
        )

    # --------------------------------------------------------
    # FILTER BY ENTITY TYPE
    # --------------------------------------------------------

    if entity_type:

        query = query.filter(
            Activity.entity_type == entity_type
        )

    # --------------------------------------------------------
    # FILTER FROM START DATE
    # --------------------------------------------------------

    if start_date:

        start_datetime = datetime.combine(
            start_date,
            time.min
        )

        query = query.filter(
            Activity.created_at >= start_datetime
        )

    # --------------------------------------------------------
    # FILTER UNTIL END DATE
    # --------------------------------------------------------

    if end_date:

        end_datetime = datetime.combine(
            end_date,
            time.max
        )

        query = query.filter(
            Activity.created_at <= end_datetime
        )

    # --------------------------------------------------------
    # GET ACTIVITIES
    # MOST RECENT FIRST
    # --------------------------------------------------------

    activities = (
        query
        .order_by(
            Activity.created_at.desc()
        )
        .limit(100)
        .all()
    )

    # --------------------------------------------------------
    # RETURN RESPONSE
    # --------------------------------------------------------

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