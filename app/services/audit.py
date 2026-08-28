from app.models.audit import AuditLog


def create_audit_log(
    db,
    decision_id: int,
    user_id: int,
    action: str,
    entity_type: str,
    description: str,
    entity_id: int | None = None
):
    audit_log = AuditLog(
        decision_id=decision_id,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description
    )

    db.add(audit_log)

    return audit_log