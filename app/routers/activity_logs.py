from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.schemas.activity_log import ActivityLogResponse


router = APIRouter(
    tags=["Activity Logs"]
)


def validate_date_range(
    start_date: date | None,
    end_date: date | None,
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date",
        )


def apply_date_filter(
    query,
    start_date: date | None,
    end_date: date | None,
):
    if start_date:
        start_datetime = datetime.combine(
            start_date,
            datetime.min.time(),
        )
        query = query.filter(
            ActivityLog.created_at >= start_datetime
        )

    if end_date:
        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            datetime.min.time(),
        )
        query = query.filter(
            ActivityLog.created_at < end_datetime
        )

    return query


# ============================================================
# GET /activities
# ============================================================

@router.get(
    "/activities",
    response_model=list[ActivityLogResponse],
)
def get_activities(
    user_id: int | None = Query(None),
    action: str | None = Query(None),
    entity_type: str | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    validate_date_range(start_date, end_date)

    current_user_id = int(current_user["sub"])
    current_user_role = current_user.get("role")

    # --------------------------------------------------------
    # Permission rules
    # --------------------------------------------------------
    #
    # Employee:
    #   Can see only their own activities.
    #
    # Manager:
    #   Can see activities belonging to users in their
    #   department.
    #
    # Administrator:
    #   Can see organization-wide activities.
    #
    # Client-supplied user_id can NEVER override these rules.
    # --------------------------------------------------------

    query = db.query(ActivityLog)

    if current_user_role == "Employee":
        query = query.filter(
            ActivityLog.user_id == current_user_id
        )

        # Employees cannot request another user's activity.
        if user_id is not None and user_id != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this user's activities",
            )

    elif current_user_role == "Manager":
        manager = (
            db.query(User)
            .filter(User.id == current_user_id)
            .first()
        )

        if not manager:
            raise HTTPException(
                status_code=404,
                detail="Manager not found",
            )

        query = (
            query
            .join(User, ActivityLog.user_id == User.id)
            .filter(User.department == manager.department)
        )

        if user_id is not None:
            requested_user = (
                db.query(User)
                .filter(User.id == user_id)
                .first()
            )

            if not requested_user:
                raise HTTPException(
                    status_code=404,
                    detail="User not found",
                )

            if requested_user.department != manager.department:
                raise HTTPException(
                    status_code=403,
                    detail="You do not have permission to access this user's activities",
                )

            query = query.filter(
                ActivityLog.user_id == user_id
            )

    elif current_user_role == "Administrator":
        if user_id is not None:
            requested_user = (
                db.query(User)
                .filter(User.id == user_id)
                .first()
            )

            if not requested_user:
                raise HTTPException(
                    status_code=404,
                    detail="User not found",
                )

            query = query.filter(
                ActivityLog.user_id == user_id
            )

    else:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access activities",
        )

    # --------------------------------------------------------
    # Optional filters
    # --------------------------------------------------------

    if action:
        query = query.filter(
            ActivityLog.action == action
        )

    if entity_type:
        query = query.filter(
            ActivityLog.entity_type == entity_type
        )

    query = apply_date_filter(
        query,
        start_date,
        end_date,
    )

    # --------------------------------------------------------
    # Pagination
    # --------------------------------------------------------

    offset = (page - 1) * page_size

    return (
        query
        .order_by(ActivityLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )


# ============================================================
# EXISTING ACTIVITY-LOGS ENDPOINT
# ============================================================

@router.get(
    "/activity-logs/",
    response_model=list[ActivityLogResponse],
)
def get_activity_logs(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Backward-compatible activity log endpoint.

    The Sprint 10 permission-sensitive endpoint is /activities.
    """

    current_user_id = int(current_user["sub"])
    current_user_role = current_user.get("role")

    query = db.query(ActivityLog)

    if current_user_role == "Employee":
        query = query.filter(
            ActivityLog.user_id == current_user_id
        )

    elif current_user_role == "Manager":
        manager = (
            db.query(User)
            .filter(User.id == current_user_id)
            .first()
        )

        if not manager:
            raise HTTPException(
                status_code=404,
                detail="Manager not found",
            )

        query = (
            query
            .join(User, ActivityLog.user_id == User.id)
            .filter(User.department == manager.department)
        )

    elif current_user_role != "Administrator":
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access activity logs",
        )

    return (
        query
        .order_by(ActivityLog.created_at.desc())
        .all()
    )