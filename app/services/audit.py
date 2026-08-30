from typing import Optional

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    user_id: Optional[int],
    action: str,
    entity_type: str,
    entity_id: Optional[int],
    description: str,
    ip_address: Optional[str] = None,
    old_value: Optional[dict] = None,
    new_value: Optional[dict] = None,
    request_method: Optional[str] = None,
    endpoint: Optional[str] = None,
):
    allowed_actions = {
        "CREATE",
        "UPDATE",
        "DELETE",
        "APPROVE",
        "REJECT",
        "SUBMIT",
        "LOGIN",
        "LOGOUT",
        "ACCESS",
        "ASSIGN",
        "STATUS_CHANGE",
    }

    allowed_entities = {
        "Decision",
        "Alternative",
        "Comment",
        "DiscussionThread",
        "MeetingNote",
        "Approval",
        "User",
    }

    if action not in allowed_actions:
        raise ValueError(
            f"Invalid audit action: {action}"
        )

    if entity_type not in allowed_entities:
        raise ValueError(
            f"Invalid entity type: {entity_type}"
        )

    audit = AuditLog(
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

    db.add(audit)

    return audit