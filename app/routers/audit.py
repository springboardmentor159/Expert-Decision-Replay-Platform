from datetime import datetime
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.core.security import get_current_user
from app.core.enums import UserRole
from app.services.audit import AUDIT_ACTIONS, ENTITY_TYPES


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit & Compliance"]
)


# =========================================================
# ADMIN AUTHORIZATION
# =========================================================

def require_admin(
    current_user: User
):
    """
    Only administrators can access organization-wide
    audit records.
    """

    if current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required"
        )

    return current_user


# =========================================================
# GET AUDIT LOGS
# =========================================================

@router.get("")
def get_audit_logs(

    user_id: Optional[int] = Query(
        None,
        ge=1,
        description="Filter audit logs by user ID"
    ),

    action: Optional[str] = Query(
        None,
        description="Filter by audit action"
    ),

    entity_type: Optional[str] = Query(
        None,
        description="Filter by entity type"
    ),

    entity_id: Optional[int] = Query(
        None,
        ge=1,
        description="Filter by entity ID"
    ),

    start_date: Optional[datetime] = Query(
        None,
        description="Return records from this date/time"
    ),

    end_date: Optional[datetime] = Query(
        None,
        description="Return records up to this date/time"
    ),

    page: int = Query(
        1,
        ge=1,
        description="Page number"
    ),

    page_size: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of records per page"
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    """
    Retrieve audit logs.

    Only administrators can access system-wide audit logs.
    """

    # -----------------------------------------------------
    # ADMIN CHECK
    # -----------------------------------------------------

    require_admin(current_user)

    # -----------------------------------------------------
    # DATE VALIDATION
    # -----------------------------------------------------

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be later than end_date"
        )

    # -----------------------------------------------------
    # ACTION VALIDATION
    # -----------------------------------------------------

    if action:

        action = action.upper()

        if action not in AUDIT_ACTIONS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Invalid audit action '{action}'. "
                    f"Allowed actions: "
                    f"{sorted(AUDIT_ACTIONS)}"
                )
            )

    # -----------------------------------------------------
    # ENTITY TYPE VALIDATION
    # -----------------------------------------------------

    if entity_type:

        if entity_type not in ENTITY_TYPES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Invalid entity type '{entity_type}'. "
                    f"Allowed entity types: "
                    f"{sorted(ENTITY_TYPES)}"
                )
            )

    # -----------------------------------------------------
    # BASE QUERY
    # -----------------------------------------------------

    query = db.query(AuditLog)

    # -----------------------------------------------------
    # USER FILTER
    # -----------------------------------------------------

    if user_id:

        user = db.query(User).filter(
            User.id == user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        query = query.filter(
            AuditLog.user_id == user_id
        )

    # -----------------------------------------------------
    # ACTION FILTER
    # -----------------------------------------------------

    if action:

        query = query.filter(
            AuditLog.action == action
        )

    # -----------------------------------------------------
    # ENTITY TYPE FILTER
    # -----------------------------------------------------

    if entity_type:

        query = query.filter(
            AuditLog.entity_type == entity_type
        )

    # -----------------------------------------------------
    # ENTITY ID FILTER
    # -----------------------------------------------------

    if entity_id:

        query = query.filter(
            AuditLog.entity_id == entity_id
        )

    # -----------------------------------------------------
    # START DATE
    # -----------------------------------------------------

    if start_date:

        query = query.filter(
            AuditLog.created_at >= start_date
        )

    # -----------------------------------------------------
    # END DATE
    # -----------------------------------------------------

    if end_date:

        query = query.filter(
            AuditLog.created_at <= end_date
        )

    # -----------------------------------------------------
    # TOTAL
    # -----------------------------------------------------

    total = query.count()

    # -----------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------

    offset = (
        page - 1
    ) * page_size

    logs = query.order_by(
        AuditLog.created_at.desc()
    ).offset(
        offset
    ).limit(
        page_size
    ).all()

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {
        "items": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "description": log.description,
                "old_value": log.old_value,
                "new_value": log.new_value,
                "ip_address": log.ip_address,
                "request_method": log.request_method,
                "endpoint": log.endpoint,
                "created_at": log.created_at
            }
            for log in logs
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
        "count": len(logs)
    }


# =========================================================
# GET SINGLE AUDIT LOG
# =========================================================

@router.get("/{audit_id}")
def get_audit_log(

    audit_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    """
    Retrieve one audit record.

    Only administrators can access audit records.
    """

    require_admin(current_user)

    audit = db.query(
        AuditLog
    ).filter(
        AuditLog.id == audit_id
    ).first()

    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )

    return {
        "id": audit.id,
        "user_id": audit.user_id,
        "action": audit.action,
        "entity_type": audit.entity_type,
        "entity_id": audit.entity_id,
        "description": audit.description,
        "old_value": audit.old_value,
        "new_value": audit.new_value,
        "ip_address": audit.ip_address,
        "request_method": audit.request_method,
        "endpoint": audit.endpoint,
        "created_at": audit.created_at
    }