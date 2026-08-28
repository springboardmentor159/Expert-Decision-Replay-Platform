from app.models.activity_log import ActivityLog


def log_activity(db, user_id, action, entity_type, entity_id, description):
    db.add(ActivityLog(
        user_id=user_id, action=action, entity_type=entity_type,
        entity_id=entity_id, description=description,
    ))