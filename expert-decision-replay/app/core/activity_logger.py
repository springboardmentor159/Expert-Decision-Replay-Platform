from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog
from app.models.user import User


def create_activity_log(
    db: Session,
    user: User,
    action: str,
    entity_type: str,
    description: str,
    entity_id: int | None = None,
):
    activity = ActivityLog(
        user_id=user.id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
    )

    db.add(activity)

    return activity