from sqlalchemy.orm import Session

from app.models.security_log import SecurityLog


ALLOWED_SECURITY_EVENTS = {
    "LOGIN_SUCCESS",
    "LOGIN_FAILED",
    "LOGOUT",
    "INVALID_JWT",
    "UNAUTHORIZED_ACCESS",
    "FORBIDDEN_ACCESS",
}


def create_security_log(
    db: Session,
    event_type: str,
    description: str | None = None,
    user_id: int | None = None,
    ip_address: str | None = None,
):
    event_type = event_type.upper()

    if event_type not in ALLOWED_SECURITY_EVENTS:
        raise ValueError(
            f"Invalid security event type: {event_type}"
        )

    security_log = SecurityLog(
        user_id=user_id,
        event_type=event_type,
        description=description,
        ip_address=ip_address,
    )

    db.add(security_log)

    return security_log