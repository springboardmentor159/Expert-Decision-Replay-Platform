from typing import Optional
from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog


def log_activity(
    db: Session,
    user_id: Optional[int],
    action: str,
    entity_type: str,
    entity_id: Optional[int],
    description: str,
) -> ActivityLog:
    """
    Utility function to automatically record system activities.
    """
    activity = ActivityLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity
