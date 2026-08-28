from app.models.audit_log import AccessLog, AuditLog, SecurityLog
from app.models.decision_version import DecisionVersion


def log_audit(db, user_id, action, entity_type, entity_id, description, old_value=None, new_value=None, request_method=None, endpoint=None):
    db.add(AuditLog(
        user_id=user_id, action=action, entity_type=entity_type, entity_id=entity_id,
        description=description, old_value=old_value, new_value=new_value,
        request_method=request_method, endpoint=endpoint,
    ))


def log_security(db, user_id, event_type, description, ip_address=None):
    db.add(SecurityLog(user_id=user_id, event_type=event_type, description=description, ip_address=ip_address))


def log_access(db, user_id, resource_type, resource_id, action, ip_address=None):
    db.add(AccessLog(user_id=user_id, resource_type=resource_type, resource_id=resource_id, action=action, ip_address=ip_address))


def snapshot_decision(db, decision, user_id):
    last = db.query(DecisionVersion).filter(DecisionVersion.decision_id == decision.id).order_by(DecisionVersion.version_number.desc()).first()
    db.add(DecisionVersion(
        decision_id=decision.id, version_number=(last.version_number + 1 if last else 1),
        title=decision.title, problem_statement=decision.problem_statement,
        rationale=decision.rationale, category=decision.category, status=decision.status,
        created_by=user_id,
    ))