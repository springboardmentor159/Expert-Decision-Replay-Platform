from typing import Optional

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


# =========================================================
# ALLOWED AUDIT ACTIONS
# =========================================================

ALLOWED_AUDIT_ACTIONS = {
    "CREATE",
    "UPDATE",
    "DELETE",
    "APPROVE",
    "REJECT",
    "SUBMIT",
    "ARCHIVE",
    "LOGIN",
    "LOGOUT",
    "ACCESS",
}

# =========================================================
# CREATE AUDIT LOG
# =========================================================

def create_audit_log(
    db: Session,
    user_id: int,
    action: str,
    entity_type: str,
    description: str,
    entity_id: Optional[int] = None,
    old_value: Optional[dict] = None,
    new_value: Optional[dict] = None,
    ip_address: Optional[str] = None,
    request_method: Optional[str] = None,
    endpoint: Optional[str] = None,
):
    # -----------------------------------------------------
    # Validate audit action
    # -----------------------------------------------------

    if action not in ALLOWED_AUDIT_ACTIONS:
        raise ValueError(
            f"Invalid audit action: {action}. "
            f"Allowed actions are: "
            f"{', '.join(sorted(ALLOWED_AUDIT_ACTIONS))}"
        )

    # -----------------------------------------------------
    # Create audit log
    # -----------------------------------------------------

    audit_log = AuditLog(
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

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log