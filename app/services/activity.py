from app.db.database import SessionLocal
from app.models.activity_log import ActivityLog


def log_activity(
    db,
    user_id: int,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    description: str | None = None,
) -> ActivityLog:
    """Persist an ActivityLog row for an automatically-tracked action.

    The caller is responsible for committing the session; this helper only
    adds the row and flushes so the generated id is available. A standalone
    session is used when ``db`` is not supplied so the helper can also be
    called from non-request contexts (e.g. scripts, background tasks).
    """
    own_session = db is None
    if own_session:
        db = SessionLocal()

    try:
        entry = ActivityLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
        )
        db.add(entry)
        db.flush()
        return entry
    finally:
        # Always persist the audit entry independently of the surrounding
        # transaction so activity is recorded even if the caller's later work
        # fails. The route handler's own commit remains for the primary entity.
        db.commit()
        if own_session:
            db.close()
