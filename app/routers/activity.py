from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.activity_log import ActivityLog
from app.schemas.dashboard import PaginatedActivityResponse
from app.routers.users import get_current_user

router = APIRouter(prefix="/activities", tags=["Activities"])

@router.get("", response_model=PaginatedActivityResponse)
def get_activities(user_id: int | None = None, action: str | None = None, entity_type: str | None = None, start_date: datetime | None = None, end_date: datetime | None = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), user=Depends(get_current_user)):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=422, detail="start_date must be before end_date")
    query = db.query(ActivityLog)
    if user.get("role") != "Administrator":
        query = query.filter(ActivityLog.user_id == int(user["sub"]))
    elif user_id:
        query = query.filter(ActivityLog.user_id == user_id)
    if action:
        query = query.filter(ActivityLog.action == action)
    if entity_type:
        query = query.filter(ActivityLog.entity_type == entity_type)
    if start_date:
        query = query.filter(ActivityLog.created_at >= start_date)
    if end_date:
        query = query.filter(ActivityLog.created_at < end_date + timedelta(days=1))
    total = query.count()
    items = query.order_by(ActivityLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "page": page, "page_size": page_size, "total": total}