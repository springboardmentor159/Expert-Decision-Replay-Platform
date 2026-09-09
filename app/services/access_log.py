from typing import Optional

from sqlalchemy.orm import Session

from app.models.access_log import AccessLog


def create_access_log(
    db: Session,
    user_id: int,
    resource_type: str,
    resource_id: int,
    action: str,
    ip_address: Optional[str] = None,
):
    access_log = AccessLog(
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        ip_address=ip_address,
    )

    db.add(access_log)
    db.flush()

    return access_log