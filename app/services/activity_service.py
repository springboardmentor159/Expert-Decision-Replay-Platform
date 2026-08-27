from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog


def log_activity(
    db: Session,
    user_id: int,
    action: str,
    entity_type: str,
    entity_id: int | None,
    description: str
):
    """
    Create an activity log entry.

    This helper is used by application APIs so activity
    records are created automatically.
    """

    activity = ActivityLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description
    )

    db.add(activity)

    return activity