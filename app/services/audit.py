from datetime import datetime
from typing import Optional, Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


# =========================================================
# CONTROLLED AUDIT ACTIONS
# =========================================================

AUDIT_ACTIONS = {
    "CREATE",
    "UPDATE",
    "DELETE",
    "APPROVE",
    "REJECT",
    "SUBMIT",
    "LOGIN",
    "LOGOUT",
    "ACCESS",
}


# =========================================================
# CONTROLLED ENTITY TYPES
# =========================================================

ENTITY_TYPES = {
    "Decision",
    "Alternative",
    "Comment",
    "DiscussionThread",
    "MeetingNote",
    "Approval",
    "User",
}


# =========================================================
# AUDIT LOG SERVICE
# =========================================================

def log_audit(
    db: Session,
    user_id: Optional[int],
    action: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    description: Optional[str] = None,
    old_value: Optional[Any] = None,
    new_value: Optional[Any] = None,
    ip_address: Optional[str] = None,
    request_method: Optional[str] = None,
    endpoint: Optional[str] = None,
):
    """
    Create an audit record.

    This function is intended to be called automatically
    by application services and routers.

    It does NOT commit the transaction.
    The caller controls the transaction so that the audit
    record and the application change are committed together.
    """

    # -----------------------------------------------------
    # VALIDATE ACTION
    # -----------------------------------------------------

    if action not in AUDIT_ACTIONS:
        raise ValueError(
            f"Invalid audit action: {action}"
        )

    # -----------------------------------------------------
    # VALIDATE ENTITY TYPE
    # -----------------------------------------------------

    if entity_type not in ENTITY_TYPES:
        raise ValueError(
            f"Invalid audit entity type: {entity_type}"
        )

    # -----------------------------------------------------
    # CREATE AUDIT RECORD
    # -----------------------------------------------------

    audit = AuditLog(
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
        created_at=datetime.utcnow(),
    )

    db.add(audit)

    return audit