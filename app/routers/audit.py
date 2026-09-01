from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.audit_log import AuditLog
from app.services.audit import ALLOWED_ACTIONS, ALLOWED_ENTITY_TYPES


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


# ============================================================
# ADMIN AUTHORIZATION
# ============================================================

def require_admin(
    current_user: User = Depends(get_current_user),
):
    if current_user.role.lower() not in {
        "admin",
        "administrator",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )

    return current_user


# ============================================================
# GET AUDIT LOGS
# ============================================================

@router.get("")
def get_audit_logs(
    user_id: Optional[int] = Query(
        default=None,
        ge=1,
    ),

    action: Optional[str] = Query(
        default=None,
    ),

    entity_type: Optional[str] = Query(
        default=None,
    ),

    entity_id: Optional[int] = Query(
        default=None,
        ge=1,
    ),

    start_date: Optional[datetime] = None,

    end_date: Optional[datetime] = None,

    page: int = Query(
        default=1,
        ge=1,
    ),

    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(require_admin),
):
    # ========================================================
    # VALIDATE ACTION
    # ========================================================

    if action is not None:
        action = action.upper()

        if action not in ALLOWED_ACTIONS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid audit action: {action}",
            )

    # ========================================================
    # VALIDATE ENTITY TYPE
    # ========================================================

    if entity_type is not None:
        if entity_type not in ALLOWED_ENTITY_TYPES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Invalid entity type: "
                    f"{entity_type}"
                ),
            )

    # ========================================================
    # VALIDATE DATE RANGE
    # ========================================================

    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date",
        )

    # ========================================================
    # BASE QUERY
    # ========================================================

    query = db.query(AuditLog)

    # ========================================================
    # USER FILTER
    # ========================================================

    if user_id is not None:
        query = query.filter(
            AuditLog.user_id == user_id
        )

    # ========================================================
    # ACTION FILTER
    # ========================================================

    if action is not None:
        query = query.filter(
            AuditLog.action == action
        )

    # ========================================================
    # ENTITY TYPE FILTER
    # ========================================================

    if entity_type is not None:
        query = query.filter(
            AuditLog.entity_type == entity_type
        )

    # ========================================================
    # ENTITY ID FILTER
    # ========================================================

    if entity_id is not None:
        query = query.filter(
            AuditLog.entity_id == entity_id
        )

    # ========================================================
    # START DATE FILTER
    # ========================================================

    if start_date is not None:
        query = query.filter(
            AuditLog.created_at >= start_date
        )

    # ========================================================
    # END DATE FILTER
    # ========================================================

    if end_date is not None:
        query = query.filter(
            AuditLog.created_at <= end_date
        )

    # ========================================================
    # TOTAL COUNT
    # ========================================================

    total = query.count()

    # ========================================================
    # PAGINATION
    # ========================================================

    offset = (page - 1) * page_size

    items = (
        query
        .order_by(
            AuditLog.created_at.desc()
        )
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
    }