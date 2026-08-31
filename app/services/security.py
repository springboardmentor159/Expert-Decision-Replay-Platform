from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.security_log import SecurityLog


SECURITY_EVENTS = {
    "LOGIN_SUCCESS",
    "LOGIN_FAILED",
    "LOGOUT",
    "INVALID_JWT",
    "UNAUTHORIZED_ACCESS",
    "FORBIDDEN_ACCESS",
}


def log_security_event(
    db: Session,
    event_type: str,
    user_id: Optional[int] = None,
    description: Optional[str] = None,
    ip_address: Optional[str] = None,
):
    """
    Create a security log entry.

    This function does not commit the transaction.
    """

    if event_type not in SECURITY_EVENTS:
        raise ValueError(
            f"Invalid security event type: {event_type}"
        )

    security_log = SecurityLog(
        user_id=user_id,
        event_type=event_type,
        description=description,
        ip_address=ip_address,
        created_at=datetime.utcnow(),
    )

    db.add(security_log)

    return security_log
