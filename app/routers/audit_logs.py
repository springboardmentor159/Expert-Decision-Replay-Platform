from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.security_log import SecurityLog
from app.models.access_log import AccessLog

router = APIRouter(prefix="/audit-logs", tags=["Audit & Compliance"])

VALID_ACTIONS = [
    "CREATE", "UPDATE", "DELETE", "APPROVE",
    "REJECT", "SUBMIT", "LOGIN", "LOGOUT", "ACCESS"
]
VALID_ENTITY_TYPES = [
    "Decision", "Alternative", "Comment",
    "DiscussionThread", "MeetingNote", "Approval",
    "User", "DecisionVersion"
]


def require_admin(current_user: User):
    if current_user.role != "Administrator":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def parse_date(date_str: str, field_name: str) -> datetime:
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid {field_name} format. Use YYYY-MM-DD."
        )


@router.get("")
def get_audit_logs(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    if action and action not in VALID_ACTIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid action. Valid actions: {VALID_ACTIONS}"
        )

    if entity_type and entity_type not in VALID_ENTITY_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid entity_type. Valid types: {VALID_ENTITY_TYPES}"
        )

    query = db.query(AuditLog)

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if start_date:
        query = query.filter(
            AuditLog.created_at >= parse_date(start_date, "start_date")
        )
    if end_date:
        query = query.filter(
            AuditLog.created_at <= parse_date(end_date, "end_date")
        )

    total = query.count()
    items = (
        query
        .order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": a.id,
                "user_id": a.user_id,
                "action": a.action,
                "entity_type": a.entity_type,
                "entity_id": a.entity_id,
                "description": a.description,
                "old_value": a.old_value,
                "new_value": a.new_value,
                "created_at": a.created_at,
            }
            for a in items
        ]
    }


@router.get("/security")
def get_security_logs(
    user_id: Optional[int] = Query(None),
    event_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    query = db.query(SecurityLog)

    if user_id:
        query = query.filter(SecurityLog.user_id == user_id)
    if event_type:
        query = query.filter(SecurityLog.event_type == event_type)
    if start_date:
        query = query.filter(
            SecurityLog.created_at >= parse_date(start_date, "start_date")
        )
    if end_date:
        query = query.filter(
            SecurityLog.created_at <= parse_date(end_date, "end_date")
        )

    total = query.count()
    items = (
        query
        .order_by(SecurityLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": s.id,
                "user_id": s.user_id,
                "event_type": s.event_type,
                "email": s.email,
                "description": s.description,
                "created_at": s.created_at,
            }
            for s in items
        ]
    }


@router.get("/access")
def get_access_logs(
    user_id: Optional[int] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    query = db.query(AccessLog)

    if user_id:
        query = query.filter(AccessLog.user_id == user_id)
    if resource_type:
        query = query.filter(AccessLog.resource_type == resource_type)
    if start_date:
        query = query.filter(
            AccessLog.created_at >= parse_date(start_date, "start_date")
        )
    if end_date:
        query = query.filter(
            AccessLog.created_at <= parse_date(end_date, "end_date")
        )

    total = query.count()
    items = (
        query
        .order_by(AccessLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": a.id,
                "user_id": a.user_id,
                "resource_type": a.resource_type,
                "resource_id": a.resource_id,
                "action": a.action,
                "created_at": a.created_at,
            }
            for a in items
        ]
    }