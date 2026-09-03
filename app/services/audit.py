from sqlalchemy.orm import Session

from app.models.audit import AuditLog, DecisionVersion

AUDIT_ACTIONS = {"CREATE", "UPDATE", "DELETE", "APPROVE", "REJECT", "SUBMIT", "LOGIN", "LOGOUT", "ACCESS"}
ENTITY_TYPES = {"Decision", "Alternative", "Comment", "DiscussionThread", "MeetingNote", "Approval", "User"}


def record_audit(db: Session, user_id: int | None, action: str, entity_type: str, description: str, entity_id: int | None = None, old_value: dict | None = None, new_value: dict | None = None) -> AuditLog:
    if action not in AUDIT_ACTIONS or entity_type not in ENTITY_TYPES:
        raise ValueError("Unsupported audit action or entity type")
    item = AuditLog(user_id=user_id, action=action, entity_type=entity_type, entity_id=entity_id, description=description, old_value=old_value, new_value=new_value)
    db.add(item)
    return item


def record_decision_version(db: Session, decision, user_id: int) -> DecisionVersion:
    latest = db.query(DecisionVersion).filter(DecisionVersion.decision_id == decision.id).order_by(DecisionVersion.version_number.desc()).first()
    version = DecisionVersion(decision_id=decision.id, version_number=(latest.version_number + 1 if latest else 1), title=decision.title, problem_statement=decision.problem_statement, category=decision.category, status=decision.status, rationale=decision.rationale, created_by=user_id)
    db.add(version)
    return version
