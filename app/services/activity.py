from sqlalchemy.orm import Session

from app.models.activity import ActivityLog


def record_activity(
    db: Session,
    user_id: int,
    action: str,
    entity_type: str,
    description: str,
    entity_id: int | None = None,
) -> ActivityLog:
    activity = ActivityLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
    )
    db.add(activity)
    return activity
