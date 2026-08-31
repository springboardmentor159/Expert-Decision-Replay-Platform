from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.activity_log import ActivityLog
from app.models.decision import Decision
from app.models.enums import DecisionStatus, UserRole
from app.models.user import User
from app.schemas.dashboard import (
    ActivityItem,
    EmployeeDashboard,
    ManagerStatistics,
    StatusCount,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


def _require_manager_or_admin(user: User) -> None:
    if user.role not in (UserRole.MANAGER, UserRole.ADMINISTRATOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view manager dashboards",
        )


def _status_breakdown(rows) -> dict:
    """Normalize a list of (status, count) tuples into all known statuses."""
    counts = {s.value: 0 for s in DecisionStatus}
    for status_value, count in rows:
        # status_value may be a DecisionStatus enum or a plain string at runtime
        key = status_value.value if isinstance(status_value, DecisionStatus) else str(status_value)
        if key in counts:
            counts[key] = count
    return counts


@router.get(
    "/employee",
    response_model=EmployeeDashboard,
)
def employee_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    status_rows = (
        db.query(Decision.status, func.count(Decision.id))
        .filter(Decision.created_by == current_user.id)
        .group_by(Decision.status)
        .all()
    )
    counts = _status_breakdown(status_rows)
    decisions_by_status = [
        StatusCount(status=s, count=counts[s]) for s in (s.value for s in DecisionStatus)
    ]
    total_decisions = sum(counts.values())

    recent_activity = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == current_user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(20)
        .all()
    )

    return EmployeeDashboard(
        user_id=current_user.id,
        total_decisions=total_decisions,
        decisions_by_status=decisions_by_status,
        recent_activity=recent_activity,
    )


@router.get(
    "/manager/statistics",
    response_model=ManagerStatistics,
)
def manager_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_manager_or_admin(current_user)

    # NOTE: No team / reporting-line concept exists on the User model yet, so
    # these counts are org-wide. This is a known limitation (see task.md).
    status_rows = (
        db.query(Decision.status, func.count(Decision.id))
        .group_by(Decision.status)
        .all()
    )
    counts = _status_breakdown(status_rows)

    return ManagerStatistics(
        scope="org-wide",
        total=sum(counts.values()),
        draft=counts[DecisionStatus.DRAFT.value],
        under_review=counts[DecisionStatus.UNDER_REVIEW.value],
        approved=counts[DecisionStatus.APPROVED.value],
        rejected=counts[DecisionStatus.REJECTED.value],
        archived=counts[DecisionStatus.ARCHIVED.value],
    )


@router.get(
    "/manager/pending-approvals",
)
def manager_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Authorization gate: only Manager / Administrator may attempt this.
    _require_manager_or_admin(current_user)

    # BLOCKED: the approval workflow (Approval model, approval statuses, assigned
    # reviewers) referenced by the spec does NOT exist in this codebase (verified
    # in Sprint 9 / Part A). There is no data source to read from, so this
    # endpoint is intentionally not implemented rather than fabricated.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            "Pending-approvals dashboard is blocked: the approval workflow "
            "(Approval model, approval statuses, assigned reviewers) has not "
            "been implemented yet. This depends on Part C/D of the overall task."
        ),
    )
