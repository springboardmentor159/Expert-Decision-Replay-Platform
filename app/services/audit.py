from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


AUDIT_ACTIONS = {
    "CREATE",
    "UPDATE",
    "DELETE",
    "APPROVE",
    "REJECT",
    "SUBMIT",
    "LOGIN",
    "LOGOUT",
    "ACCESS",
    "STATUS_CHANGE",
}


AUDIT_ENTITY_TYPES = {
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
    decision_id: int | None = None,
    user_id: int | None = None,
    action: str = "ACCESS",
    description: str = "",
    entity_type: str = "Decision",
    entity_id: int | None = None,
    ip_address: str | None = None,
    old_value: dict[str, Any] | None = None,
    new_value: dict[str, Any] | None = None,
    request_method: str | None = None,
    endpoint: str | None = None,
):
    action = action.upper()
    entity_type = entity_type.strip()

    if action not in AUDIT_ACTIONS:
        raise ValueError(
            f"Invalid audit action: {action}"
        )

    if entity_type not in AUDIT_ENTITY_TYPES:
        raise ValueError(
            f"Invalid audit entity type: {entity_type}"
        )

    if entity_id is None:
        entity_id = decision_id

    if entity_id is None:
        raise ValueError(
            "entity_id is required"
        )

    audit_log = AuditLog(
        decision_id=decision_id,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        ip_address=ip_address,
        old_value=old_value,
        new_value=new_value,
        request_method=request_method,
        endpoint=endpoint,
    )

    db.add(audit_log)

    return audit_log