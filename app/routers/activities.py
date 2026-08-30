from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.activity_log import ActivityLog

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get("")
def get_activities(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ActivityLog)

    # Non-admins only see their own activities
    if current_user.role != "admin":
        query = query.filter(ActivityLog.user_id == current_user.id)
    elif user_id:
        query = query.filter(ActivityLog.user_id == user_id)

    if action:
        query = query.filter(ActivityLog.action == action)

    if entity_type:
        query = query.filter(ActivityLog.entity_type == entity_type)

    if start_date:
        try:
            query = query.filter(
                ActivityLog.created_at >= datetime.fromisoformat(start_date)
            )
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="Invalid start_date format. Use YYYY-MM-DD."
            )

    if end_date:
        try:
            query = query.filter(
                ActivityLog.created_at <= datetime.fromisoformat(end_date)
            )
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="Invalid end_date format. Use YYYY-MM-DD."
            )

    total = query.count()
    items = (
        query
        .order_by(ActivityLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": a.id,
                "user_id": a.user_id,
                "action": a.action,
                "entity_type": a.entity_type,
                "entity_id": a.entity_id,
                "description": a.description,
                "created_at": a.created_at,
            }
            for a in items
        ]
    }