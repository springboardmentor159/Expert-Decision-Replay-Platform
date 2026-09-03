import json
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditAction, AuditEntityType


def log_audit(
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
    endpoint: Optional[str] = None
) -> AuditLog:
    audit_log = AuditLog(
        user_id=user_id,
        action=action.value,
        entity_type=entity_type.value,
        entity_id=entity_id,
        description=description,
        ip_address=ip_address,
        old_value=(
            json.dumps(old_value)
            if old_value is not None
            else None
        ),
        new_value=(
            json.dumps(new_value)
            if new_value is not None
            else None
        ),
        request_method=request_method,
        endpoint=endpoint
    )

    db.add(audit_log)
    db.flush()

    return audit_log