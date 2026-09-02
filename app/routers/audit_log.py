from datetime import datetime
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user

from app.models.audit_log import AuditLog
from app.models.decision import Decision
from app.models.security_log import SecurityLog
from app.models.access_log import AccessLog

from app.schemas.audit_log import AuditLogResponse

from app.services.security import create_access_log


router = APIRouter(
    tags=["Audit Logs"],
)


# =========================================================
# EXISTING DECISION AUDIT ENDPOINT
# =========================================================
@router.get(
    "/decisions/{decision_id}/audit-logs",
    response_model=List[AuditLogResponse],
)
def get_decision_audit_logs(
    decision_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    audit_logs = (
        db.query(AuditLog)
        .filter(AuditLog.decision_id == decision_id)
        .order_by(AuditLog.created_at.desc())
        .all()
    )

    # -----------------------------------------------------
    # Sprint 11: Record resource access
    # -----------------------------------------------------
    client_ip = (
        request.client.host
        if request.client
        else None
    )

    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Decision Audit Logs",
        resource_id=decision_id,
        action="ACCESS",
        ip_address=client_ip,
    )

    db.commit()

    return audit_logs


# =========================================================
# GENERIC AUDIT LOG SEARCH
# =========================================================
@router.get(
    "/audit-logs",
    response_model=List[AuditLogResponse],
)
def get_audit_logs(
    request: Request,
    user_id: int | None = Query(None),
    action: str | None = Query(None),
    entity_type: str | None = Query(None),
    entity_id: int | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # -----------------------------------------------------
    # RBAC
    # -----------------------------------------------------
    if current_user.role not in {
        "Admin",
        "Administrator",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admin can access audit logs",
        )

    # -----------------------------------------------------
    # DATE RANGE VALIDATION
    # -----------------------------------------------------
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be greater than end_date",
        )

    # -----------------------------------------------------
    # VALID AUDIT ACTIONS
    # -----------------------------------------------------
    valid_actions = {
        "CREATE",
        "UPDATE",
        "DELETE",
        "APPROVE",
        "REJECT",
        "SUBMIT",
        "LOGIN",
        "LOGOUT",
        "ACCESS",
        "STATUS_CHANGE",
    }

    # -----------------------------------------------------
    # VALID ENTITY TYPES
    # -----------------------------------------------------
    valid_entity_types = {
        "Decision",
        "Alternative",
        "Comment",
        "DiscussionThread",
        "MeetingNote",
        "Approval",
        "User",
    }

    # -----------------------------------------------------
    # ACTION VALIDATION
    # -----------------------------------------------------
    if action:
        action = action.upper()

        if action not in valid_actions:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid action",
            )

    # -----------------------------------------------------
    # ENTITY TYPE VALIDATION
    # -----------------------------------------------------
    if entity_type and entity_type not in valid_entity_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid entity_type",
        )

    # -----------------------------------------------------
    # BASE QUERY
    # -----------------------------------------------------
    query = db.query(AuditLog)

    if user_id is not None:
        query = query.filter(
            AuditLog.user_id == user_id
        )

    if action:
        query = query.filter(
            AuditLog.action == action
        )

    if entity_type:
        query = query.filter(
            AuditLog.entity_type == entity_type
        )

    if entity_id is not None:
        query = query.filter(
            AuditLog.entity_id == entity_id
        )

    if start_date:
        query = query.filter(
            AuditLog.created_at >= start_date
        )

    if end_date:
        query = query.filter(
            AuditLog.created_at <= end_date
        )

    # -----------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------
    offset = (page - 1) * page_size

    results = (
        query
        .order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # -----------------------------------------------------
    # Record access
    # -----------------------------------------------------
    client_ip = (
        request.client.host
        if request.client
        else None
    )

    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Audit Logs",
        resource_id=None,
        action="ACCESS",
        ip_address=client_ip,
    )

    db.commit()

    return results


# =========================================================
# SECURITY LOGS
# =========================================================
@router.get(
    "/security-logs",
)
def get_security_logs(
    request: Request,
    user_id: int | None = Query(None),
    event_type: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # -----------------------------------------------------
    # Administrator-only access
    # -----------------------------------------------------
    if current_user.role not in {
        "Admin",
        "Administrator",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admin can access security logs",
        )

    # -----------------------------------------------------
    # DATE VALIDATION
    # -----------------------------------------------------
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be greater than end_date",
        )

    query = db.query(SecurityLog)

    # -----------------------------------------------------
    # FILTER BY USER
    # -----------------------------------------------------
    if user_id is not None:
        query = query.filter(
            SecurityLog.user_id == user_id
        )

    # -----------------------------------------------------
    # FILTER BY EVENT TYPE
    # -----------------------------------------------------
    if event_type:
        query = query.filter(
            SecurityLog.event_type == event_type
        )

    # -----------------------------------------------------
    # FILTER BY START DATE
    # -----------------------------------------------------
    if start_date:
        query = query.filter(
            SecurityLog.created_at >= start_date
        )

    # -----------------------------------------------------
    # FILTER BY END DATE
    # -----------------------------------------------------
    if end_date:
        query = query.filter(
            SecurityLog.created_at <= end_date
        )

    # -----------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------
    offset = (page - 1) * page_size

    logs = (
        query
        .order_by(SecurityLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # -----------------------------------------------------
    # Record access to Security Logs
    # -----------------------------------------------------
    client_ip = (
        request.client.host
        if request.client
        else None
    )

    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Security Logs",
        resource_id=None,
        action="ACCESS",
        ip_address=client_ip,
    )

    db.commit()

    # -----------------------------------------------------
    # JSON RESPONSE
    # -----------------------------------------------------
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "event_type": log.event_type,
            "description": log.description,
            "ip_address": log.ip_address,
            "created_at": log.created_at,
        }
        for log in logs
    ]


# =========================================================
# ACCESS LOGS
# =========================================================
@router.get(
    "/access-logs",
)
def get_access_logs(
    request: Request,
    user_id: int | None = Query(None),
    resource_type: str | None = Query(None),
    resource_id: int | None = Query(None),
    action: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # -----------------------------------------------------
    # Administrator-only access
    # -----------------------------------------------------
    if current_user.role not in {
        "Admin",
        "Administrator",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admin can access access logs",
        )

    # -----------------------------------------------------
    # DATE VALIDATION
    # -----------------------------------------------------
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be greater than end_date",
        )

    query = db.query(AccessLog)

    # -----------------------------------------------------
    # FILTER BY USER
    # -----------------------------------------------------
    if user_id is not None:
        query = query.filter(
            AccessLog.user_id == user_id
        )

    # -----------------------------------------------------
    # FILTER BY RESOURCE TYPE
    # -----------------------------------------------------
    if resource_type:
        query = query.filter(
            AccessLog.resource_type == resource_type
        )

    # -----------------------------------------------------
    # FILTER BY RESOURCE ID
    # -----------------------------------------------------
    if resource_id is not None:
        query = query.filter(
            AccessLog.resource_id == resource_id
        )

    # -----------------------------------------------------
    # FILTER BY ACTION
    # -----------------------------------------------------
    if action:
        query = query.filter(
            AccessLog.action == action.upper()
        )

    # -----------------------------------------------------
    # FILTER BY START DATE
    # -----------------------------------------------------
    if start_date:
        query = query.filter(
            AccessLog.created_at >= start_date
        )

    # -----------------------------------------------------
    # FILTER BY END DATE
    # -----------------------------------------------------
    if end_date:
        query = query.filter(
            AccessLog.created_at <= end_date
        )

    # -----------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------
    offset = (page - 1) * page_size

    logs = (
        query
        .order_by(AccessLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # -----------------------------------------------------
    # Record access to Access Logs
    # -----------------------------------------------------
    client_ip = (
        request.client.host
        if request.client
        else None
    )

    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Access Logs",
        resource_id=None,
        action="ACCESS",
        ip_address=client_ip,
    )

    db.commit()

    # -----------------------------------------------------
    # JSON RESPONSE
    # -----------------------------------------------------
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "action": log.action,
            "ip_address": log.ip_address,
            "created_at": log.created_at,
        }
        for log in logs
    ]