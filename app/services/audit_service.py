from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.access_log import AccessLog
from app.models.audit_log import AuditLog
from app.models.decision import Decision
from app.models.decision_version import DecisionVersion
from app.models.security_log import SecurityLog


def log_audit(
    db: Session,
    user_id: Optional[int],
    action: str,
    entity_type: str,
    entity_id: Optional[int],
    description: str,
    ip_address: Optional[str] = None,
    old_value: Optional[Dict[str, Any]] = None,
    new_value: Optional[Dict[str, Any]] = None,
    request_method: Optional[str] = None,
    endpoint: Optional[str] = None,
) -> AuditLog:
    """
    Creates an immutable audit log record for state mutations and actions across the system.
    """
    audit_entry = AuditLog(
        user_id=user_id,
        action=action.strip().upper() if action else "UNKNOWN",
        entity_type=entity_type.strip() if entity_type else "General",
        entity_id=entity_id,
        description=description,
        ip_address=ip_address,
        old_value=old_value,
        new_value=new_value,
        request_method=request_method,
        endpoint=endpoint,
        created_at=datetime.utcnow(),
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    return audit_entry


def log_security_event(
    db: Session,
    user_id: Optional[int],
    event_type: str,
    description: str,
    ip_address: Optional[str] = None,
) -> SecurityLog:
    """
    Records a security-sensitive event (e.g. login success/failure, unauthorized access).
    Sensitive parameters such as passwords are NEVER stored in this log.
    """
    security_entry = SecurityLog(
        user_id=user_id,
        event_type=event_type.strip().upper(),
        description=description,
        ip_address=ip_address,
        created_at=datetime.utcnow(),
    )
    db.add(security_entry)
    db.commit()
    db.refresh(security_entry)
    return security_entry


def log_access_event(
    db: Session,
    user_id: Optional[int],
    resource_type: str,
    resource_id: Optional[int],
    action: str = "VIEW",
    ip_address: Optional[str] = None,
) -> AccessLog:
    """
    Records a resource access event (e.g. viewing decisions, approvals, audit logs).
    """
    access_entry = AccessLog(
        user_id=user_id,
        resource_type=resource_type.strip(),
        resource_id=resource_id,
        action=action.strip().upper(),
        ip_address=ip_address,
        created_at=datetime.utcnow(),
    )
    db.add(access_entry)
    db.commit()
    db.refresh(access_entry)
    return access_entry


def create_decision_version(
    db: Session,
    decision: Decision,
    user_id: int,
    description: Optional[str] = None,
) -> DecisionVersion:
    """
    Generates a new sequential version snapshot of the given Decision.
    Version numbers are monotonically increasing integers (1, 2, 3...).
    """
    current_max = (
        db.query(func.coalesce(func.max(DecisionVersion.version_number), 0))
        .filter(DecisionVersion.decision_id == decision.id)
        .scalar()
    )
    next_version = current_max + 1

    version_record = DecisionVersion(
        decision_id=decision.id,
        version_number=next_version,
        title=decision.title,
        problem_statement=decision.problem_statement,
        description=description if description is not None else (decision.rationale or ""),
        category=decision.category,
        status=decision.status,
        created_by=user_id,
        created_at=datetime.utcnow(),
    )
    db.add(version_record)
    db.commit()
    db.refresh(version_record)
    return version_record
