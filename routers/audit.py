from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.audit import AccessLog, AuditLog, DecisionVersion, SecurityLog
from app.models.decision import Decision
from app.models.alternative import Alternative
from app.models.comment import Comment
from app.models.discussion_thread import DiscussionThread
from app.models.meeting_note import MeetingNote
from app.models.approval import Approval
from app.models.user import User
from app.schemas.audit import AuditResponse, VersionResponse
from app.services.audit import record_audit

router = APIRouter(tags=["Audit & Compliance"])


def _admin(user: User) -> None:
    if str(user.role).lower() not in {"admin", "administrator"}:
        raise HTTPException(status_code=403, detail="Administrator permission required")


@router.get("/audit-logs")
def audit_logs(user_id: int | None = Query(None, ge=1), action: str | None = Query(None, pattern="^(CREATE|UPDATE|DELETE|APPROVE|REJECT|SUBMIT|LOGIN|LOGOUT|ACCESS)$"), entity_type: str | None = Query(None, pattern="^(Decision|Alternative|Comment|DiscussionThread|MeetingNote|Approval|User)$"), entity_id: int | None = Query(None, ge=1), start_date: datetime | None = None, end_date: datetime | None = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _admin(current_user)
    record_audit(db, current_user.id, "ACCESS", "User", "Audit logs accessed", current_user.id)
    db.commit()
    if start_date and end_date and end_date < start_date:
        raise HTTPException(status_code=422, detail="end_date must be on or after start_date")
    query = db.query(AuditLog)
    if user_id: query = query.filter(AuditLog.user_id == user_id)
    if action: query = query.filter(AuditLog.action == action)
    if entity_type: query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id: query = query.filter(AuditLog.entity_id == entity_id)
    if start_date: query = query.filter(AuditLog.created_at >= start_date)
    if end_date: query = query.filter(AuditLog.created_at <= end_date)
    total = query.count()
    items = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.get("/security-logs", response_model=list[dict])
def security_logs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _admin(current_user)
    return db.query(SecurityLog).order_by(SecurityLog.created_at.desc()).limit(100).all()


@router.get("/access-logs", response_model=list[dict])
def access_logs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _admin(current_user)
    return db.query(AccessLog).order_by(AccessLog.created_at.desc()).limit(100).all()


@router.get("/decisions/{decision_id}/versions", response_model=list[VersionResponse])
def decision_versions(decision_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not db.query(Decision).filter(Decision.id == decision_id).first():
        raise HTTPException(status_code=404, detail="Decision not found")
    return db.query(DecisionVersion).filter(DecisionVersion.decision_id == decision_id).order_by(DecisionVersion.version_number.asc()).all()


@router.get("/decisions/{decision_id}/versions/{version_number}", response_model=VersionResponse)
def decision_version(decision_id: int, version_number: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    version = db.query(DecisionVersion).filter(DecisionVersion.decision_id == decision_id, DecisionVersion.version_number == version_number).first()
    if not version:
        raise HTTPException(status_code=404, detail="Decision version not found")
    return version


@router.get("/decisions/{decision_id}/history")
def decision_history(decision_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not db.query(Decision).filter(Decision.id == decision_id).first():
        raise HTTPException(status_code=404, detail="Decision not found")
    alternative_ids = db.query(Alternative.id).filter(Alternative.decision_id == decision_id)
    comment_ids = db.query(Comment.id).filter(Comment.decision_id == decision_id)
    thread_ids = db.query(DiscussionThread.id).filter(DiscussionThread.decision_id == decision_id)
    note_ids = db.query(MeetingNote.id).filter(MeetingNote.decision_id == decision_id)
    approval_ids = db.query(Approval.id).filter(Approval.decision_id == decision_id)
    condition = or_(
        (AuditLog.entity_type == "Decision") & (AuditLog.entity_id == decision_id),
        (AuditLog.entity_type == "Alternative") & AuditLog.entity_id.in_(alternative_ids),
        (AuditLog.entity_type == "Comment") & AuditLog.entity_id.in_(comment_ids),
        (AuditLog.entity_type == "DiscussionThread") & AuditLog.entity_id.in_(thread_ids),
        (AuditLog.entity_type == "MeetingNote") & AuditLog.entity_id.in_(note_ids),
        (AuditLog.entity_type == "Approval") & AuditLog.entity_id.in_(approval_ids),
    )
    return db.query(AuditLog).filter(condition).order_by(AuditLog.created_at.asc()).all()
