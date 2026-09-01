from typing import Optional

from fastapi import APIRouter, Depends, Query
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
    user_id: Optional[int] = Query(default=None),
    entity_type: Optional[str] = Query(default=None),
    entity_id: Optional[int] = Query(default=None),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ActivityLog)

    # Filter by user
    if user_id is not None:
        query = query.filter(
            ActivityLog.user_id == user_id
        )

    # Filter by entity type
    if entity_type is not None:
        query = query.filter(
            ActivityLog.entity_type == entity_type
        )

    # Filter by entity ID
    if entity_id is not None:
        query = query.filter(
            ActivityLog.entity_id == entity_id
        )

    activities = (
        query
        .order_by(ActivityLog.created_at.desc())
        .all()
    )

    return activities