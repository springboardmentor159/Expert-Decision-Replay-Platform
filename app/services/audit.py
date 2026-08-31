import json
from typing import Optional

from app.db.database import SessionLocal
from app.models.audit_log import AuditLog
from app.models.security_log import SecurityLog
from app.models.access_log import AccessLog
from app.models.decision_version import DecisionVersion


SENSITIVE_FIELDS = {
    "password", "secret", "token", "password_hash", "secret_key",
    "db_password", "database_url", "credentials", "api_key", "authorization",
}


def _sanitize_dict(d: dict | None) -> str | None:
    if not d:
        return None
    sanitized = {k: "***" if k.lower() in SENSITIVE_FIELDS else v for k, v in d.items()}
    return json.dumps(sanitized, default=str, ensure_ascii=False)


def _get_next_version_number(db, decision_id: int) -> int:
    last = (
        db.query(DecisionVersion)
        .filter(DecisionVersion.decision_id == decision_id)
        .order_by(DecisionVersion.version_number.desc())
        .first()
    )
    return (last.version_number + 1) if last else 1


def log_audit(
    db,
    user_id: int,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    description: str | None = None,
    old_values: dict | None = None,
    new_values: dict | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    """Persist an AuditLog row with controlled action/entity types."""
    own_session = db is None
    if own_session:
        db = SessionLocal()

    try:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            old_values=_sanitize_dict(old_values),
            new_values=_sanitize_dict(new_values),
            ip_address=ip_address,
        )
        db.add(entry)
        db.flush()
        return entry
    finally:
        db.commit()
        if own_session:
            db.close()


def log_security(
    db,
    event_type: str,
    user_id: int | None = None,
    description: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> SecurityLog:
    """Persist a SecurityLog row for security-relevant events."""
    own_session = db is None
    if own_session:
        db = SessionLocal()

    try:
        entry = SecurityLog(
            user_id=user_id,
            event_type=event_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(entry)
        db.flush()
        return entry
    finally:
        db.commit()
        if own_session:
            db.close()


def log_access(
    db,
    method: str,
    path: str,
    status_code: int,
    user_id: int | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    response_time_ms: int | None = None,
) -> AccessLog:
    """Persist an AccessLog row for HTTP request tracking."""
    own_session = db is None
    if own_session:
        db = SessionLocal()

    try:
        entry = AccessLog(
            method=method,
            path=path,
            status_code=status_code,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            response_time_ms=response_time_ms,
        )
        db.add(entry)
        db.flush()
        return entry
    finally:
        db.commit()
        if own_session:
            db.close()


def create_decision_snapshot(
    db,
    decision,
    created_by: int,
) -> DecisionVersion:
    """Create a versioned snapshot of the current decision state."""
    own_session = db is None
    if own_session:
        db = SessionLocal()

    try:
        version_number = _get_next_version_number(db, decision.id)
        snapshot = DecisionVersion(
            decision_id=decision.id,
            version_number=version_number,
            title=decision.title,
            problem_statement=decision.problem_statement,
            category=decision.category,
            status=(
                decision.status.value
                if hasattr(decision.status, "value")
                else decision.status
            ),
            rationale=decision.rationale,
            created_by=created_by,
        )
        db.add(snapshot)
        db.flush()
        return snapshot
    finally:
        db.commit()
        if own_session:
            db.close()
