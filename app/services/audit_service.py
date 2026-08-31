from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.access_log import AccessLog
from app.models.activity_log import ActivityLog
from app.models.audit_log import AuditLog
from app.models.decision import Decision
from app.models.decision_version import DecisionVersion
from app.models.security_log import SecurityLog

# Controlled Action and Entity constants
VALID_AUDIT_ACTIONS = {
    "CREATE",
    "UPDATE",
    "DELETE",
    "APPROVE",
    "REJECT",
    "SUBMIT",
    "LOGIN",
    "LOGOUT",
    "ACCESS",
    "VIEW",
}

VALID_ENTITY_TYPES = {
    "Decision",
    "Alternative",
    "Comment",
    "DiscussionThread",
    "MeetingNote",
    "Approval",
    "User",
    "Tag",
    "AuditLog",
    "SecurityLog",
    "AccessLog",
}


def get_client_ip(request: Optional[Request]) -> Optional[str]:
    """Extracts client IP address from FastAPI Request."""
    if not request:
        return None
    # Check X-Forwarded-For header in case of proxy/reverse proxy
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


def log_audit(
    db: Session,
    user_id: Optional[int],
    action: str,
    entity_type: str,
    entity_id: Optional[int],
    description: str,
    old_value: Optional[Dict[str, Any]] = None,
    new_value: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    request_method: Optional[str] = None,
    endpoint: Optional[str] = None,
) -> AuditLog:
    """
    Utility function to automatically record audit log records.
    Also syncs with ActivityLog for backwards compatibility.
    """
    normalized_action = action.upper().strip()

    audit_entry = AuditLog(
        user_id=user_id,
        action=normalized_action,
        entity_type=entity_type.strip(),
        entity_id=entity_id,
        description=description,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
        request_method=request_method,
        endpoint=endpoint,
        created_at=datetime.utcnow(),
    )
    db.add(audit_entry)

    # Sync with ActivityLog
    activity_entry = ActivityLog(
        user_id=user_id,
        action=action.lower().strip(),
        entity_type=entity_type.strip(),
        entity_id=entity_id,
        description=description,
        created_at=datetime.utcnow(),
    )
    db.add(activity_entry)

    db.commit()
    db.refresh(audit_entry)
    return audit_entry


def create_decision_version(
    db: Session,
    decision: Decision,
    created_by: int,
) -> DecisionVersion:
    """
    Creates a new sequential version for a decision.
    """
    max_ver = (
        db.query(func.max(DecisionVersion.version_number))
        .filter(DecisionVersion.decision_id == decision.id)
        .scalar()
    )
    next_ver = (max_ver or 0) + 1

    version_record = DecisionVersion(
        decision_id=decision.id,
        version_number=next_ver,
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status=decision.status,
        rationale=decision.rationale,
        created_by=created_by,
        created_at=datetime.utcnow(),
    )
    db.add(version_record)
    db.commit()
    db.refresh(version_record)
    return version_record


def log_security_event(
    db: Session,
    event_type: str,
    description: str,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
) -> SecurityLog:
    """
    Records security events (e.g. LOGIN_SUCCESS, LOGIN_FAILED, UNAUTHORIZED_ACCESS).
    Strictly never logs plain passwords or credentials.
    """
    sec_entry = SecurityLog(
        user_id=user_id,
        event_type=event_type.upper().strip(),
        description=description,
        ip_address=ip_address,
        created_at=datetime.utcnow(),
    )
    db.add(sec_entry)
    db.commit()
    db.refresh(sec_entry)
    return sec_entry


def log_access_event(
    db: Session,
    user_id: Optional[int],
    resource_type: str,
    resource_id: Optional[int],
    action: str = "VIEW",
    ip_address: Optional[str] = None,
) -> AccessLog:
    """
    Records resource access/view events.
    """
    acc_entry = AccessLog(
        user_id=user_id,
        resource_type=resource_type.strip(),
        resource_id=resource_id,
        action=action.upper().strip(),
        ip_address=ip_address,
        created_at=datetime.utcnow(),
    )
    db.add(acc_entry)
    db.commit()
    db.refresh(acc_entry)
    return acc_entry
