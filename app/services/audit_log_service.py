from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


ALLOWED_ACTIONS = {
    "CREATE",
    "UPDATE",
    "DELETE",
    "APPROVE",
    "REJECT",
    "SUBMIT",
    "LOGIN",
    "LOGOUT",
    "ACCESS",
}

ALLOWED_ENTITY_TYPES = {
    "Decision",
    "Alternative",
    "Comment",
    "DiscussionThread",
    "MeetingNote",
    "Approval",
    "User",
}


def create_audit_log(
    db: Session,
    user_id: int,
    action: str,
    entity_type: str,
    description: str,
    entity_id: int | None = None,
    old_value: dict | None = None,
    new_value: dict | None = None,
    ip_address: str | None = None,
    request_method: str | None = None,
    endpoint: str | None = None,
):
    if action not in ALLOWED_ACTIONS:
        raise ValueError(
            f"Invalid audit action: {action}"
        )

    if entity_type not in ALLOWED_ENTITY_TYPES:
        raise ValueError(
            f"Invalid audit entity type: {entity_type}"
        )

    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
        request_method=request_method,
        endpoint=endpoint,
    )

    db.add(audit_log)
    db.flush()

    return audit_log