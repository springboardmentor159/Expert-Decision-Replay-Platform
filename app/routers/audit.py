from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.audit_log import AccessLog, AuditLog, SecurityLog
from app.models.activity_log import ActivityLog
from app.models.decision import Decision
from app.models.decision_version import DecisionVersion
from app.routers.dashboard import require_roles
from app.schemas.audit import (
    AccessResponse, AuditAction, AuditEntity, AuditResponse,
    DecisionVersionResponse, PaginatedAuditResponse, SecurityResponse,
)
from app.utils.audit_logger import log_access

router = APIRouter(tags=["Audit & Compliance"])


def _date_filter(query, column, start_date, end_date):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=422, detail="start_date must be before end_date")
    if start_date:
        query = query.filter(column >= start_date)
    if end_date:
        query = query.filter(column < end_date + timedelta(days=1))
    return query


@router.get("/audit-logs", response_model=PaginatedAuditResponse)
def get_audit_logs(
    user_id: int | None = None, action: AuditAction | None = None,
    entity_type: AuditEntity | None = None, entity_id: int | None = None,
    start_date: datetime | None = None, end_date: datetime | None = None,
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db), user=Depends(require_roles("Administrator")),
):
    query = db.query(AuditLog)
    query = _date_filter(query, AuditLog.created_at, start_date, end_date)
    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action.value)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type.value)
    if entity_id is not None:
        query = query.filter(AuditLog.entity_id == entity_id)
    total = query.count()
    items = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    log_access(db, int(user["sub"]), "AuditLog", None, "VIEW")
    db.commit()
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.get("/security-logs", response_model=list[SecurityResponse])
def get_security_logs(db: Session = Depends(get_db), user=Depends(require_roles("Administrator"))):
    return db.query(SecurityLog).order_by(SecurityLog.created_at.desc()).limit(100).all()


@router.get("/access-logs", response_model=list[AccessResponse])
def get_access_logs(db: Session = Depends(get_db), user=Depends(require_roles("Administrator"))):
    return db.query(AccessLog).order_by(AccessLog.created_at.desc()).limit(100).all()


@router.get("/decisions/{decision_id}/versions", response_model=list[DecisionVersionResponse])
def get_versions(decision_id: int, db: Session = Depends(get_db), user=Depends(require_roles("Employee", "Reviewer", "Manager", "Administrator"))):
    if not db.query(Decision).filter(Decision.id == decision_id).first():
        raise HTTPException(status_code=404, detail="Decision not found")
    return db.query(DecisionVersion).filter(DecisionVersion.decision_id == decision_id).order_by(DecisionVersion.version_number.asc()).all()


@router.get("/decisions/{decision_id}/versions/{version_number}", response_model=DecisionVersionResponse)
def get_version(decision_id: int, version_number: int, db: Session = Depends(get_db), user=Depends(require_roles("Employee", "Reviewer", "Manager", "Administrator"))):
    version = db.query(DecisionVersion).filter(DecisionVersion.decision_id == decision_id, DecisionVersion.version_number == version_number).first()
    if not version:
        raise HTTPException(status_code=404, detail="Decision version not found")
    return version


@router.get("/decisions/{decision_id}/history")
def get_decision_history(decision_id: int, db: Session = Depends(get_db), user=Depends(require_roles("Employee", "Reviewer", "Manager", "Administrator"))):
    if not db.query(Decision).filter(Decision.id == decision_id).first():
        raise HTTPException(status_code=404, detail="Decision not found")
    events = db.query(AuditLog).filter(AuditLog.entity_type == "Decision", AuditLog.entity_id == decision_id).order_by(AuditLog.created_at.asc()).all()
    return events