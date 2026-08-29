import json
from app.models.audit import AccessLog, AuditLog, DecisionVersion, SecurityLog
from app.models.decision import Decision


def create_audit_log(
    db,
    user_id: int,
    action: str,
    entity_type: str,
    description: str,
    decision_id: int | None = None,
    entity_id: int | None = None,
    old_value: dict | str | None = None,
    new_value: dict | str | None = None,
    ip_address: str | None = None,
    request_method: str | None = None,
    endpoint: str | None = None,
):
    old_val_str = (
        json.dumps(old_value)
        if isinstance(old_value, dict)
        else str(old_value)
        if old_value is not None
        else None
    )
    new_val_str = (
        json.dumps(new_value)
        if isinstance(new_value, dict)
        else str(new_value)
        if new_value is not None
        else None
    )

    action_val = action.value if hasattr(action, "value") else str(action)

    audit_log = AuditLog(
        decision_id=decision_id,
        user_id=user_id,
        action=action_val,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        old_value=old_val_str,
        new_value=new_val_str,
        ip_address=ip_address,
        request_method=request_method,
        endpoint=endpoint,
    )

    db.add(audit_log)
    return audit_log


def create_decision_version(
    db,
    decision: Decision,
    user_id: int,
) -> DecisionVersion:
    # Determine the next sequential version number
    latest_version = (
        db.query(DecisionVersion)
        .filter(DecisionVersion.decision_id == decision.id)
        .order_by(DecisionVersion.version_number.desc())
        .first()
    )

    next_version_num = (
        (latest_version.version_number + 1)
        if latest_version
        else 1
    )

    status_val = (
        decision.status.value
        if hasattr(decision.status, "value")
        else str(decision.status)
    )

    version = DecisionVersion(
        decision_id=decision.id,
        version_number=next_version_num,
        title=decision.title,
        problem_statement=decision.problem_statement,
        rationale=decision.rationale,
        category=decision.category,
        status=status_val,
        created_by=user_id,
    )

    db.add(version)
    return version


def create_security_log(
    db,
    event_type: str,
    description: str,
    user_id: int | None = None,
    email: str | None = None,
    ip_address: str | None = None,
) -> SecurityLog:
    security_log = SecurityLog(
        user_id=user_id,
        email=email,
        event_type=event_type,
        description=description,
        ip_address=ip_address,
    )

    db.add(security_log)
    return security_log


def create_access_log(
    db,
    user_id: int,
    resource_type: str,
    resource_id: int | None,
    action: str = "VIEW",
    ip_address: str | None = None,
) -> AccessLog:
    access_log = AccessLog(
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        ip_address=ip_address,
    )

    db.add(access_log)
    return access_log