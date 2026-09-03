from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    user_id: int | None,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    description: str | None = None,
    ip_address: str | None = None,
    request_method: str | None = None,
    endpoint: str | None = None,
    old_value: dict | None = None,
    new_value: dict | None = None,
):
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        ip_address=ip_address,
        request_method=request_method,
        endpoint=endpoint,
        old_value=old_value,
        new_value=new_value,
    )

    db.add(audit_log)
    db.flush()

    return audit_log