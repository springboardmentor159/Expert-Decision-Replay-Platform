from datetime import date, datetime, time, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.audit_log import AuditLog
from app.services.access import create_access_log


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"]
)


# ============================================================
# ROLE CHECK
# ============================================================

def require_admin(current_user: User):

    user_role = str(
        current_user.role
    ).strip().lower()

    if user_role not in [
        "admin",
        "administrator"
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access audit logs"
        )


# ============================================================
# GET AUDIT LOGS
#
# GET /audit-logs
#
# Filters:
# user_id
# action
# entity_type
# entity_id
# start_date
# end_date
# page
# page_size
# ============================================================

@router.get("")
def get_audit_logs(

    user_id: Optional[int] = Query(None),

    action: Optional[str] = Query(None),

    entity_type: Optional[str] = Query(None),

    entity_id: Optional[int] = Query(None),

    start_date: Optional[date] = Query(None),

    end_date: Optional[date] = Query(None),

    page: int = Query(1),

    page_size: int = Query(20),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):

    # ========================================================
    # ROLE AUTHORIZATION
    # ========================================================

    require_admin(current_user)

    # ========================================================
    # DATE VALIDATION
    # ========================================================

    if start_date and end_date:

        if start_date > end_date:

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="start_date cannot be after end_date"
            )

    # ========================================================
    # PAGINATION VALIDATION
    # ========================================================

    if page < 1:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="page must be greater than or equal to 1"
        )

    if page_size < 1:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="page_size must be greater than or equal to 1"
        )

    if page_size > 100:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="page_size cannot be greater than 100"
        )

    # ========================================================
    # START QUERY
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

    if action:

        allowed_actions = [
            "CREATE",
            "UPDATE",
            "DELETE",
            "APPROVE",
            "REJECT",
            "SUBMIT",
            "LOGIN",
            "LOGOUT",
            "ACCESS",
            "STATUS_CHANGE"
        ]

        action_value = action.upper()

        if action_value not in allowed_actions:

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid audit action"
            )

        query = query.filter(
            AuditLog.action == action_value
        )

    # ========================================================
    # ENTITY TYPE FILTER
    # ========================================================

    if entity_type:

        allowed_entity_types = [
            "Decision",
            "Alternative",
            "Comment",
            "DiscussionThread",
            "MeetingNote",
            "Approval",
            "User"
        ]

        if entity_type not in allowed_entity_types:

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid entity type"
            )

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

    if start_date:

        start_datetime = datetime.combine(
            start_date,
            time.min
        )

        query = query.filter(
            AuditLog.created_at >= start_datetime
        )

    # ========================================================
    # END DATE FILTER
    # ========================================================

    if end_date:

        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min
        )

        query = query.filter(
            AuditLog.created_at < end_datetime
        )

    # ========================================================
    # TOTAL COUNT
    # ========================================================

    total = query.count()

    # ========================================================
    # PAGINATION
    # ========================================================

    offset = (page - 1) * page_size

    audit_logs = (
        query
        .order_by(
            AuditLog.created_at.desc()
        )
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # ========================================================
    # ACCESS LOG
    #
    # Record that administrator accessed audit logs
    # ========================================================

    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="AuditLog",
        resource_id=None,
        action="VIEW"
    )

    db.commit()

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "items": [
            {
                "id": audit.id,
                "user_id": audit.user_id,
                "action": audit.action,
                "entity_type": audit.entity_type,
                "entity_id": audit.entity_id,
                "description": audit.description,
                "ip_address": audit.ip_address,
                "old_value": audit.old_value,
                "new_value": audit.new_value,
                "request_method": audit.request_method,
                "endpoint": audit.endpoint,
                "created_at": audit.created_at
            }
            for audit in audit_logs
        ],
        "page": page,
        "page_size": page_size,
        "total": total
    }