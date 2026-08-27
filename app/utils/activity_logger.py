from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog


def log_activity(
    db: Session,
    user_id: int,
    action: str,
    entity_type: str,
    entity_id: int,
    description: str,
) -> ActivityLog:
    """
    Writes one activity record. Call this from inside the SAME request/
    transaction as the action it describes, right after db.commit() on the
    main object, then commit again for the log row.

    This is intentionally a plain function (not a route) so it can be
    called from any router without duplicating logic — per the brief,
    activity logs must be created automatically by the backend, never
    typed in manually through Swagger.
    """
    entry = ActivityLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
    )

    db.add(entry)
    db.commit()

    return entry
