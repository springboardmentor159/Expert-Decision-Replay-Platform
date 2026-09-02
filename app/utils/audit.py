"""
Sprint 11: Audit & Compliance helpers.

Every function here is a plain Python function (not a route), by design:
audit/version/security/access records must be created automatically by
the backend as a side effect of a real action, never typed in manually
through Swagger. Call these from inside routers, in the same
request/transaction as the action they describe.
"""
from typing import Optional, Any
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import Request

from app.models.audit_log import AuditLog
from app.models.decision_version import DecisionVersion
from app.models.security_log import SecurityLog
from app.models.access_log import AccessLog
from app.models.decision import Decision


def get_client_ip(request: Optional[Request]) -> Optional[str]:
    """
    Best-effort client IP extraction. Works behind simple setups; if the
    app sits behind a proxy/load balancer, prefer the first hop of
    X-Forwarded-For when present.
    """
    if request is None:
        return None

    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client:
        return request.client.host

    return None


# ---------------------------------------------------------------------
# Audit logs (CREATE / UPDATE / DELETE / APPROVE / REJECT / ... )
# ---------------------------------------------------------------------

def log_audit(
    db: Session,
    user_id: int,
    action: str,
    entity_type: str,
    entity_id: int,
    description: str,
    old_value: Optional[dict[str, Any]] = None,
    new_value: Optional[dict[str, Any]] = None,
    request: Optional[Request] = None,
) -> AuditLog:
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        old_value=old_value,
        new_value=new_value,
        request_method=request.method if request is not None else None,
        endpoint=str(request.url.path) if request is not None else None,
        ip_address=get_client_ip(request),
    )

    db.add(entry)
    db.commit()

    return entry


# ---------------------------------------------------------------------
# Decision version tracking
# ---------------------------------------------------------------------

def create_decision_version(
    db: Session,
    decision: Decision,
    created_by: int,
) -> DecisionVersion:
    """
    Snapshots the CURRENT state of `decision` as the next sequential
    version for that decision. The caller is responsible for having
    already applied and committed the change to `decision` itself.

    version_number is computed server-side (max existing + 1) - the
    client can never set it directly.
    """
    next_version = (
        db.query(func.coalesce(func.max(DecisionVersion.version_number), 0))
        .filter(DecisionVersion.decision_id == decision.id)
        .scalar()
    ) + 1

    version = DecisionVersion(
        decision_id=decision.id,
        version_number=next_version,
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status=decision.status,
        rationale=decision.rationale,
        created_by=created_by,
    )

    db.add(version)
    db.commit()
    db.refresh(version)

    return version


# ---------------------------------------------------------------------
# Security logs (authentication / authorization events)
# ---------------------------------------------------------------------

def log_security_event(
    db: Session,
    event_type: str,
    request: Optional[Request] = None,
    user_id: Optional[int] = None,
    identifier: Optional[str] = None,
    description: Optional[str] = None,
) -> SecurityLog:
    """
    NEVER pass a password, token, or other secret into `description` -
    this table exists to record that an auth event happened, not what
    the credentials were.
    """
    entry = SecurityLog(
        user_id=user_id,
        identifier=identifier,
        event_type=event_type,
        description=description,
        ip_address=get_client_ip(request),
    )

    db.add(entry)
    db.commit()

    return entry


# ---------------------------------------------------------------------
# Access logs (read-only resource views)
# ---------------------------------------------------------------------

def log_access(
    db: Session,
    user_id: int,
    resource_type: str,
    resource_id: Optional[int],
    action: str = "VIEW",
    request: Optional[Request] = None,
) -> AccessLog:
    entry = AccessLog(
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        ip_address=get_client_ip(request),
    )

    db.add(entry)
    db.commit()

    return entry
