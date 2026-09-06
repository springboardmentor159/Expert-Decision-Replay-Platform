from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.core.dependencies import get_current_user, get_user_role


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"]
)


# =========================================================
# ALLOWED VALUES
# =========================================================

ALLOWED_ACTIONS = {
    "CREATE",
    "UPDATE",
    "DELETE",
    "APPROVE",
    "REJECT",
    "SUBMIT",
    "ARCHIVE",
    "LOGIN",
    "LOGOUT",
    "ACCESS",
}
ALLOWED_ENTITY_TYPES = {
    "Decision",
    "Alternative",
    "Comment",
    "DiscussionThread",
    "MeetingNote",
    "Approval",
    "User",
}


# =========================================================
# GET AUDIT LOGS
# =========================================================

@router.get("/")
def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None, ge=1),
    user_id: Optional[int] = Query(None, ge=1),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # -----------------------------------------------------
    # VALIDATE ACTION
    # -----------------------------------------------------

    if action and action not in ALLOWED_ACTIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Invalid audit action",
                "allowed_actions": sorted(ALLOWED_ACTIONS)
            }
        )

    # -----------------------------------------------------
    # VALIDATE ENTITY TYPE
    # -----------------------------------------------------

    if entity_type and entity_type not in ALLOWED_ENTITY_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Invalid entity type",
                "allowed_entity_types": sorted(ALLOWED_ENTITY_TYPES)
            }
        )

    # -----------------------------------------------------
    # VALIDATE DATE RANGE
    # -----------------------------------------------------

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date must be before or equal to end_date"
        )

    query = db.query(AuditLog)

    # -----------------------------------------------------
    # ROLE-BASED ACCESS
    # -----------------------------------------------------

    role = get_user_role(current_user)

    if role != "Administrator":
        query = query.filter(
            AuditLog.user_id == current_user.id
        )

    # -----------------------------------------------------
    # KEYWORD SEARCH
    # -----------------------------------------------------

    if search:
        search_pattern = f"%{search}%"

        query = query.filter(
            or_(
                AuditLog.description.ilike(search_pattern),
                AuditLog.endpoint.ilike(search_pattern)
            )
        )

    # -----------------------------------------------------
    # FILTER BY ACTION
    # -----------------------------------------------------

    if action:
        query = query.filter(
            AuditLog.action == action
        )

    # -----------------------------------------------------
    # FILTER BY ENTITY TYPE
    # -----------------------------------------------------

    if entity_type:
        query = query.filter(
            AuditLog.entity_type == entity_type
        )

    # -----------------------------------------------------
    # FILTER BY ENTITY ID
    # -----------------------------------------------------

    if entity_id:
        query = query.filter(
            AuditLog.entity_id == entity_id
        )

    # -----------------------------------------------------
    # FILTER BY USER
    # -----------------------------------------------------

    if user_id and role == "Administrator":
        query = query.filter(
            AuditLog.user_id == user_id
        )

    # -----------------------------------------------------
    # FILTER BY START DATE
    # -----------------------------------------------------

    if start_date:
        query = query.filter(
            AuditLog.created_at >= start_date
        )

    # -----------------------------------------------------
    # FILTER BY END DATE
    # -----------------------------------------------------

    if end_date:
        query = query.filter(
            AuditLog.created_at <= end_date
        )

    # -----------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------

    total = query.count()

    offset = (page - 1) * page_size

    audit_logs = (
        query
        .order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": audit_logs
    }


# =========================================================
# GET ENTITY AUDIT HISTORY
# =========================================================

@router.get("/entity/{entity_type}/{entity_id}")
def get_entity_history(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # -----------------------------------------------------
    # VALIDATE ENTITY TYPE
    # -----------------------------------------------------

    if entity_type not in ALLOWED_ENTITY_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Invalid entity type",
                "allowed_entity_types": sorted(ALLOWED_ENTITY_TYPES)
            }
        )

    # -----------------------------------------------------
    # BUILD QUERY
    # -----------------------------------------------------

    query = db.query(AuditLog).filter(
        AuditLog.entity_type == entity_type,
        AuditLog.entity_id == entity_id
    )

    # -----------------------------------------------------
    # ROLE-BASED ACCESS
    # -----------------------------------------------------

    role = get_user_role(current_user)

    if role != "Administrator":
        query = query.filter(
            AuditLog.user_id == current_user.id
        )

    # -----------------------------------------------------
    # GET HISTORY
    # -----------------------------------------------------

    history = (
        query
        .order_by(AuditLog.created_at.asc())
        .all()
    )

    return history