from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.activity_log import ActivityLog
from app.schemas.activity_log import ActivityLogResponse


router = APIRouter(
    prefix="/activity-logs",
    tags=["Activity Logs"]
)


@router.get("/", response_model=list[ActivityLogResponse])
def get_activity_logs(
    db: Session = Depends(get_db),
):
    logs = (
        db.query(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .all()
    )

    return logs