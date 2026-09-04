from sqlalchemy.orm import Session

from app.models.access_log import AccessLog


def create_access_log(
    db: Session,
    user_id: int | None,
    resource_type: str,
    resource_id: int | None = None,
    action: str = "VIEW",
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