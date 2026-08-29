from datetime import date, datetime, time
from math import ceil

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.audit import AccessLog, AuditLog, SecurityLog
from app.models.decision import Decision
from app.models.user import User, UserRole
from app.schemas.audit import (
    AccessLogListResponse,
    AuditLogListResponse,
    AuditLogResponse,
    SecurityLogListResponse,
)
from app.services.auth import get_current_user
from app.services.authorization import require_roles


router = APIRouter(
    tags=["Audit & Compliance"]
)


# ============================================================
# Decision authorization helper
# ============================================================

def can_access_decision(
    decision: Decision,
    current_user: User
) -> bool:
    if decision.organization_id != current_user.organization_id:
        return False

    if decision.created_by == current_user.id:
        return True

    if current_user.role in (
        UserRole.MANAGER,
        UserRole.ADMINISTRATOR
    ):
        return True

    return False


# ============================================================
# SYSTEM-WIDE AUDIT LOGS
# Administrator only
# ============================================================

@router.get(
    "/audit-logs",
    response_model=AuditLogListResponse,
)
def get_audit_logs(
    user_id: int | None = Query(default=None, description="Filter by user ID"),
    action: str | None = Query(default=None, description="Filter by action type"),
    entity_type: str | None = Query(default=None, description="Filter by entity type"),
    entity_id: int | None = Query(default=None, description="Filter by entity ID"),
    start_date: date | None = Query(default=None, description="Start date filter"),
    end_date: date | None = Query(default=None, description="End date filter"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR)),
):
    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date",
        )

    query = (
        db.query(AuditLog)
        .join(User, AuditLog.user_id == User.id)
        .filter(User.organization_id == current_user.organization_id)
    )

    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)

    if action is not None:
        query = query.filter(AuditLog.action == action)

    if entity_type is not None:
        query = query.filter(AuditLog.entity_type == entity_type)

    if entity_id is not None:
        query = query.filter(AuditLog.entity_id == entity_id)

    if start_date is not None:
        query = query.filter(
            AuditLog.created_at >= datetime.combine(start_date, time.min)
        )

    if end_date is not None:
        query = query.filter(
            AuditLog.created_at <= datetime.combine(end_date, time.max)
        )

    total = query.count()
    offset = (page - 1) * page_size
    items = (
        query
        .order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    total_pages = ceil(total / page_size) if total > 0 else 0

    return AuditLogListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# ============================================================
# SECURITY LOGS
# Administrator only
# ============================================================

@router.get(
    "/security-logs",
    response_model=SecurityLogListResponse,
)
def get_security_logs(
    user_id: int | None = Query(default=None, description="Filter by user ID"),
    event_type: str | None = Query(default=None, description="Filter by event type"),
    start_date: date | None = Query(default=None, description="Start date filter"),
    end_date: date | None = Query(default=None, description="End date filter"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR)),
):
    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date",
        )

    query = db.query(SecurityLog)

    if user_id is not None:
        query = query.filter(SecurityLog.user_id == user_id)

    if event_type is not None:
        query = query.filter(SecurityLog.event_type == event_type)

    if start_date is not None:
        query = query.filter(
            SecurityLog.created_at >= datetime.combine(start_date, time.min)
        )

    if end_date is not None:
        query = query.filter(
            SecurityLog.created_at <= datetime.combine(end_date, time.max)
        )

    total = query.count()
    offset = (page - 1) * page_size
    items = (
        query
        .order_by(SecurityLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    total_pages = ceil(total / page_size) if total > 0 else 0

    return SecurityLogListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# ============================================================
# ACCESS LOGS
# Administrator only
# ============================================================

@router.get(
    "/access-logs",
    response_model=AccessLogListResponse,
)
def get_access_logs(
    user_id: int | None = Query(default=None, description="Filter by user ID"),
    resource_type: str | None = Query(default=None, description="Filter by resource type"),
    resource_id: int | None = Query(default=None, description="Filter by resource ID"),
    start_date: date | None = Query(default=None, description="Start date filter"),
    end_date: date | None = Query(default=None, description="End date filter"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR)),
):
    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date",
        )

    query = (
        db.query(AccessLog)
        .join(User, AccessLog.user_id == User.id)
        .filter(User.organization_id == current_user.organization_id)
    )

    if user_id is not None:
        query = query.filter(AccessLog.user_id == user_id)

    if resource_type is not None:
        query = query.filter(AccessLog.resource_type == resource_type)

    if resource_id is not None:
        query = query.filter(AccessLog.resource_id == resource_id)

    if start_date is not None:
        query = query.filter(
            AccessLog.created_at >= datetime.combine(start_date, time.min)
        )

    if end_date is not None:
        query = query.filter(
            AccessLog.created_at <= datetime.combine(end_date, time.max)
        )

    total = query.count()
    offset = (page - 1) * page_size
    items = (
        query
        .order_by(AccessLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    total_pages = ceil(total / page_size) if total > 0 else 0

    return AccessLogListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# ============================================================
# Get audit history for a specific decision
# ============================================================

@router.get(
    "/decisions/{decision_id}/audit-logs",
    response_model=list[AuditLogResponse],
)
def get_decision_audit_logs(
    decision_id: int,
    action: str | None = Query(
        default=None,
        description="Filter by audit action"
    ),
    entity_type: str | None = Query(
        default=None,
        description="Filter by entity type"
    ),
    user_id: int | None = Query(
        default=None,
        description="Filter by user ID"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = (
        db.query(Decision)
        .filter(
            Decision.id == decision_id
        )
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    if not can_access_decision(
        decision,
        current_user
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission to view "
                "audit logs for this decision"
            )
        )

    query = (
        db.query(AuditLog)
        .filter(
            AuditLog.decision_id == decision_id
        )
    )

    if action is not None:
        query = query.filter(
            AuditLog.action == action
        )

    if entity_type is not None:
        query = query.filter(
            AuditLog.entity_type == entity_type
        )

    if user_id is not None:
        requested_user = (
            db.query(User)
            .filter(
                User.id == user_id,
                User.organization_id == current_user.organization_id
            )
            .first()
        )

        if requested_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in your organization"
            )

        query = query.filter(
            AuditLog.user_id == user_id
        )

    audit_logs = (
        query
        .order_by(
            AuditLog.created_at.desc()
        )
        .all()
    )

    return audit_logs