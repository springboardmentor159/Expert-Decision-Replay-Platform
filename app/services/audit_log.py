from typing import Optional, Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.audit_action import AuditAction
from app.models.audit_entity import AuditEntityType


def create_audit_log(
    db: Session,
    user_id: int,
    action: AuditAction,
    entity_type: AuditEntityType,
    entity_id: int,
    description: str,
    ip_address: Optional[str] = None,
    old_value: Optional[Any] = None,
    new_value: Optional[Any] = None,
    request_method: Optional[str] = None,
    endpoint: Optional[str] = None,
):
    audit_log = AuditLog(
        user_id=user_id,
        action=action.value,
        entity_type=entity_type.value,
        entity_id=entity_id,
        description=description,
        ip_address=ip_address,
        old_value=old_value,
        new_value=new_value,
        request_method=request_method,
        endpoint=endpoint,
    )

    db.add(audit_log)
    db.flush()

    return audit_log