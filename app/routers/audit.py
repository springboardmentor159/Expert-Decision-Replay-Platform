from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.audit import AuditLog
from app.models.decision import Decision
from app.models.user import User, UserRole
from app.schemas.audit import AuditLogResponse
from app.services.auth import get_current_user


router = APIRouter(
    tags=["Audit Logs"]
)


# ============================================================
# Decision authorization
# ============================================================

def can_access_decision(
    decision: Decision,
    current_user: User
) -> bool:

    # --------------------------------------------------------
    # Organization isolation
    # --------------------------------------------------------

    if decision.organization_id != current_user.organization_id:
        return False

    # --------------------------------------------------------
    # Decision creator can access their own decision
    # --------------------------------------------------------

    if decision.created_by == current_user.id:
        return True

    # --------------------------------------------------------
    # Managers and Administrators can access decisions
    # within their own organization.
    # --------------------------------------------------------

    if current_user.role in (
        UserRole.MANAGER,
        UserRole.ADMINISTRATOR
    ):
        return True

    return False


# ============================================================
# Get audit history for a decision
# ============================================================

@router.get(
    "/decisions/{decision_id}/audit-logs",
    response_model=list[AuditLogResponse]
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

    # ========================================================
    # Find decision
    # ========================================================

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

    # ========================================================
    # Organization + role authorization
    # ========================================================

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

    # ========================================================
    # Build audit log query
    # ========================================================

    query = (
        db.query(AuditLog)
        .filter(
            AuditLog.decision_id == decision_id
        )
    )

    # ========================================================
    # Filter by action
    # ========================================================

    if action is not None:
        query = query.filter(
            AuditLog.action == action
        )

    # ========================================================
    # Filter by entity type
    # ========================================================

    if entity_type is not None:
        query = query.filter(
            AuditLog.entity_type == entity_type
        )

    # ========================================================
    # Filter by user
    # ========================================================

    if user_id is not None:

        # Make sure the requested user belongs to the
        # same organization as the current user.
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

    # ========================================================
    # Return latest activity first
    # ========================================================

    audit_logs = (
        query
        .order_by(
            AuditLog.created_at.desc()
        )
        .all()
    )

    return audit_logs