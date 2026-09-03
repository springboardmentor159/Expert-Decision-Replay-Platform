from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.activity import ActivityLog
from app.models.user import User
from app.schemas.activity import ActivityResponse

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get("", response_model=list[ActivityResponse])
def list_activities(
    user_id: int | None = Query(None, ge=1),
    action: str | None = Query(None, min_length=1),
    entity_type: str | None = Query(None, min_length=1),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if start_date and end_date and end_date < start_date:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="end_date must be on or after start_date")
    is_admin = str(current_user.role).lower() in {"admin", "administrator"}
    query = db.query(ActivityLog)
    if not is_admin:
        query = query.filter(ActivityLog.user_id == current_user.id)
    elif user_id:
        query = query.filter(ActivityLog.user_id == user_id)
    if action:
        query = query.filter(ActivityLog.action == action)
    if entity_type:
        query = query.filter(ActivityLog.entity_type == entity_type)
    if start_date:
        query = query.filter(ActivityLog.created_at >= start_date)
    if end_date:
        query = query.filter(ActivityLog.created_at <= end_date)
    return query.order_by(ActivityLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
