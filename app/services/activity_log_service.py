from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog


def create_activity_log(
    db: Session,
    user_id: int,
    action: str,
    entity_type: str,
    description: str,
    entity_id: int | None = None,
):
    activity_log = ActivityLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
    )

    db.add(activity_log)
    db.commit()
    db.refresh(activity_log)

    return activity_log