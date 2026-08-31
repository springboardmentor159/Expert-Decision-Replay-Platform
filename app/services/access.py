from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.access_log import AccessLog


ACCESS_ACTIONS = {
    "VIEW",
    "CREATE",
    "UPDATE",
    "DELETE",
    "ACCESS",
}


def log_access(
    db: Session,
    user_id: Optional[int],
    resource_type: str,
    resource_id: Optional[int] = None,
    action: str = "VIEW",
    ip_address: Optional[str] = None,
):
    """
    Create an access log entry.

    This function does not commit the transaction.
    """

    if action not in ACCESS_ACTIONS:
        raise ValueError(
            f"Invalid access action: {action}"
        )

    access_log = AccessLog(
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        ip_address=ip_address,
        created_at=datetime.utcnow(),
    )

    db.add(access_log)

    return access_log
