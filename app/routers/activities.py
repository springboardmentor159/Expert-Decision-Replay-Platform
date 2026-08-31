from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.activity_log import ActivityLog
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.dashboard import ActivityItem, PaginatedActivityResponse

router = APIRouter(
    tags=["Activities"],
)


def _parse_date(value: str | None) -> datetime | None:
    """Parse YYYY-MM-DD to datetime at midnight."""
    if value is None:
        return None
    try:
        d = date.fromisoformat(value)
        return datetime(d.year, d.month, d.day)
    except ValueError:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid date format: '{value}'. Expected YYYY-MM-DD.",
        )


@router.get(
    "/activities",
    response_model=PaginatedActivityResponse,
)
def list_activities(
    user: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action type (e.g. create, update, status_change)"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (e.g. decision, alternative, comment)"),
    start_date: Optional[str] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of items to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Activity feed endpoint.

    Authorization rule:
    - Administrator: sees organization-wide activity (all users).
    - Manager: sees organization-wide activity (all users).
    - Employee / Reviewer: sees only their own activity.

    Filters compose with AND. Results are ordered by created_at descending
    (most recent first). Pagination uses offset/limit with a maximum of 200
    items per page. The response includes total count and has_more flag.
    """
    sd = _parse_date(start_date)
    ed = _parse_date(end_date)

    if sd and ed and sd > ed:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date must not be after end_date.",
        )

    query = db.query(ActivityLog)

    # Scope: non-admin/manager users can only see their own activity
    if current_user.role not in (UserRole.ADMINISTRATOR, UserRole.MANAGER):
        query = query.filter(ActivityLog.user_id == current_user.id)
    elif user is not None:
        # Admin/Manager can optionally filter by a specific user
        query = query.filter(ActivityLog.user_id == user)

    if action is not None:
        query = query.filter(ActivityLog.action == action)
    if entity_type is not None:
        query = query.filter(ActivityLog.entity_type == entity_type)
    if sd:
        query = query.filter(ActivityLog.created_at >= sd)
    if ed:
        query = query.filter(ActivityLog.created_at < ed + timedelta(days=1))

    # Total count (before pagination)
    total = query.count()

    # Apply pagination
    items = (
        query
        .order_by(ActivityLog.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    has_more = (offset + limit) < total

    return PaginatedActivityResponse(
        items=[
            ActivityItem(
                id=a.id,
                user_id=a.user_id,
                action=a.action,
                entity_type=a.entity_type,
                entity_id=a.entity_id,
                description=a.description,
                created_at=a.created_at,
            )
            for a in items
        ],
        total=total,
        offset=offset,
        limit=limit,
        has_more=has_more,
    )
