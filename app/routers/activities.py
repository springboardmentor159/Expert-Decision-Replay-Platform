from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.schemas.activity import ActivityLogResponse, PaginatedActivitiesResponse

router = APIRouter(
    prefix="/activities",
    tags=["Activities"]
)


def _parse_date(date_str: Optional[str], param_name: str) -> Optional[datetime]:
    if not date_str or not date_str.strip():
        return None
    cleaned = date_str.strip()
    try:
        return datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
    except ValueError:
        try:
            return datetime.strptime(cleaned, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid date format for '{param_name}': '{date_str}'. Expected YYYY-MM-DD"
            )


def _format_activity(act: ActivityLog) -> ActivityLogResponse:
    return ActivityLogResponse(
        id=act.id,
        user_id=act.user_id,
        user_name=act.user.full_name if act.user else None,
        action=act.action,
        entity_type=act.entity_type,
        entity_id=act.entity_id,
        description=act.description,
        created_at=act.created_at
    )


@router.get(
    "",
    response_model=PaginatedActivitiesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get paginated list of system activities with optional filtering"
)
def get_activities(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action name"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (decision, alternative, comment, etc.)"),
    start_date: Optional[str] = Query(None, description="Filter from start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter up to end date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    start_dt = _parse_date(start_date, "start_date")
    end_dt = _parse_date(end_date, "end_date")
    if start_dt and end_dt and start_dt > end_dt:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )

    query = db.query(ActivityLog)

    # Role-based scoping: non-admins only see own / team activities unless admin
    if current_user.role == "Employee":
        query = query.filter(ActivityLog.user_id == current_user.id)
    elif current_user.role == "Manager":
        if current_user.department:
            team_users = db.query(User.id).filter(User.department == current_user.department).all()
            team_ids = [u.id for u in team_users]
            query = query.filter(ActivityLog.user_id.in_(team_ids))
        else:
            query = query.filter(ActivityLog.user_id == current_user.id)

    # Applied filters
    if user_id:
        # Check if user exists
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        query = query.filter(ActivityLog.user_id == user_id)

    if action and action.strip():
        query = query.filter(ActivityLog.action == action.strip())

    if entity_type and entity_type.strip():
        query = query.filter(ActivityLog.entity_type == entity_type.strip())

    if start_dt:
        query = query.filter(ActivityLog.created_at >= start_dt)
    if end_dt:
        query = query.filter(ActivityLog.created_at <= end_dt)

    total = query.count()
    items = query.order_by(ActivityLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedActivitiesResponse(
        items=[_format_activity(a) for a in items],
        page=page,
        page_size=page_size,
        total=total
    )
