from typing import Optional

from sqlalchemy.orm import Session

from app.models.access_log import AccessLog


def create_access_log(
    db: Session,
    user_id: Optional[int],
    resource_type: str,
    resource_id: Optional[int],
    action: str = "VIEW",
    ip_address: Optional[str] = None
):
    """
    Create an access log entry.

    This function is reusable across the application
    whenever a user accesses a resource.
    """

    access_log = AccessLog(
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        ip_address=ip_address
    )

    db.add(access_log)

    return access_log