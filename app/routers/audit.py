from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user

from app.models.audit_log import AuditLog
from app.models.decision_version import DecisionVersion
from app.models.security_log import SecurityLog
from app.models.access_log import AccessLog


router = APIRouter(
    tags=["Audit & Compliance"]
)


# =========================================================
# HELPER - ADMIN CHECK
# =========================================================

def require_admin(current_user):

    if current_user["role"] != "Administrator":
        raise HTTPException(
            status_code=403,
            detail="Administrator access required"
        )


# =========================================================
# 1. GET AUDIT LOGS
# =========================================================

@router.get("/audit-logs")
def get_audit_logs(
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    require_admin(current_user)

    # Pagination validation
    if page < 1:
        raise HTTPException(
            status_code=422,
            detail="Page must be greater than or equal to 1"
        )

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=422,
            detail="Page size must be between 1 and 100"
        )

    # Date validation
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be greater than end_date"
        )

    query = db.query(AuditLog)

    if action:
        query = query.filter(
            AuditLog.action == action
        )

    if entity_type:
        query = query.filter(
            AuditLog.entity_type == entity_type
        )

    if user_id:
        query = query.filter(
            AuditLog.user_id == user_id
        )

    if start_date:
        query = query.filter(
            AuditLog.created_at >= start_date
        )

    if end_date:
        query = query.filter(
            AuditLog.created_at <= end_date
        )

    total = query.count()

    logs = (
        query
        .order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": logs,
        "page": page,
        "page_size": page_size,
        "total": total
    }


# =========================================================
# 2. DECISION HISTORY
# =========================================================

@router.get("/decisions/{decision_id}/history")
def get_decision_history(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    versions = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision_id
        )
        .order_by(
            DecisionVersion.version_number.asc()
        )
        .all()
    )

    return {
        "decision_id": decision_id,
        "history": versions
    }


# =========================================================
# 3. GET ALL DECISION VERSIONS
# =========================================================

@router.get("/decisions/{decision_id}/versions")
def get_decision_versions(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    versions = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision_id
        )
        .order_by(
            DecisionVersion.version_number.asc()
        )
        .all()
    )

    return {
        "decision_id": decision_id,
        "versions": versions
    }


# =========================================================
# 4. GET SPECIFIC DECISION VERSION
# =========================================================

@router.get(
    "/decisions/{decision_id}/versions/{version_number}"
)
def get_specific_version(
    decision_id: int,
    version_number: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision_id,
            DecisionVersion.version_number == version_number
        )
        .first()
    )

    if version is None:
        raise HTTPException(
            status_code=404,
            detail="Version not found"
        )

    return version


# =========================================================
# 5. GET ACCESS LOGS
# =========================================================

@router.get("/access-logs")
def get_access_logs(
    user_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    require_admin(current_user)

    # Pagination validation
    if page < 1:
        raise HTTPException(
            status_code=422,
            detail="Page must be greater than or equal to 1"
        )

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=422,
            detail="Page size must be between 1 and 100"
        )

    # Date validation
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be greater than end_date"
        )

    query = db.query(AccessLog)

    if user_id:
        query = query.filter(
            AccessLog.user_id == user_id
        )

    if resource_type:
        query = query.filter(
            AccessLog.resource_type == resource_type
        )

    if resource_id:
        query = query.filter(
            AccessLog.resource_id == resource_id
        )

    if action:
        query = query.filter(
            AccessLog.action == action
        )

    if start_date:
        query = query.filter(
            AccessLog.created_at >= start_date
        )

    if end_date:
        query = query.filter(
            AccessLog.created_at <= end_date
        )

    total = query.count()

    logs = (
        query
        .order_by(AccessLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": logs,
        "page": page,
        "page_size": page_size,
        "total": total
    }


# =========================================================
# 6. GET SECURITY LOGS
# =========================================================

@router.get("/security-logs")
def get_security_logs(
    user_id: Optional[int] = None,
    event_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    require_admin(current_user)

    # Pagination validation
    if page < 1:
        raise HTTPException(
            status_code=422,
            detail="Page must be greater than or equal to 1"
        )

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=422,
            detail="Page size must be between 1 and 100"
        )

    # Date validation
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be greater than end_date"
        )

    query = db.query(SecurityLog)

    if user_id:
        query = query.filter(
            SecurityLog.user_id == user_id
        )

    if event_type:
        query = query.filter(
            SecurityLog.event_type == event_type
        )

    if start_date:
        query = query.filter(
            SecurityLog.created_at >= start_date
        )

    if end_date:
        query = query.filter(
            SecurityLog.created_at <= end_date
        )

    total = query.count()

    logs = (
        query
        .order_by(SecurityLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": logs,
        "page": page,
        "page_size": page_size,
        "total": total
    }