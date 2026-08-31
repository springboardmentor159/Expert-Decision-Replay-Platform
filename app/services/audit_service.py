from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.models.security_log import SecurityLog
from app.models.access_log import AccessLog


def log_audit(
    db: Session,
    user_id: int,
    action: str,
    entity_type: str = None,
    entity_id: int = None,
    description: str = None,
    old_value: dict = None,
    new_value: dict = None,
    ip_address: str = None,
    request_method: str = None,
    endpoint: str = None,
):
    entry = AuditLog(
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
    db.add(entry)


def log_security(
    db: Session,
    event_type: str,
    user_id: int = None,
    email: str = None,
    description: str = None,
    ip_address: str = None,
):
    entry = SecurityLog(
        user_id=user_id,
        event_type=event_type,
        email=email,
        description=description,
        ip_address=ip_address,
    )
    db.add(entry)


def log_access(
    db: Session,
    user_id: int,
    resource_type: str = None,
    resource_id: int = None,
    action: str = "VIEW",
    ip_address: str = None,
):
    entry = AccessLog(
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        ip_address=ip_address,
    )
    db.add(entry)