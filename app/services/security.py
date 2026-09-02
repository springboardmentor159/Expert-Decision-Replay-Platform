from sqlalchemy.orm import Session

from app.models.security_log import SecurityLog
from app.models.access_log import AccessLog


def create_security_log(
    db: Session,
    user_id: int | None,
    event_type: str,
    description: str,
    ip_address: str | None = None,
):
    security_log = SecurityLog(
        user_id=user_id,
        event_type=event_type,
        description=description,
        ip_address=ip_address,
    )

    db.add(security_log)

    return security_log


def create_access_log(
    db: Session,
    user_id: int | None,
    resource_type: str,
    resource_id: int | None,
    action: str,
    ip_address: str | None = None,
):
    access_log = AccessLog(
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        ip_address=ip_address,
    )

    db.add(access_log)

    return access_log