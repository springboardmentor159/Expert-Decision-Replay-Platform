from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard import get_dashboard_data


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "",
    response_model=DashboardResponse,
)
def get_dashboard(
    activity_action: str | None = Query(
        default=None,
        description="Filter activities by action",
    ),
    activity_start_date: date | None = Query(
        default=None,
        description="Filter activities from this date",
    ),
    activity_end_date: date | None = Query(
        default=None,
        description="Filter activities until this date",
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_dashboard_data(
        db=db,
        current_user=current_user,
        activity_action=activity_action,
        activity_start_date=activity_start_date,
        activity_end_date=activity_end_date,
    )