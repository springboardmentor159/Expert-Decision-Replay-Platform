from datetime import date, datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.audit import AuditLog
from app.models.user import User, UserRole
from app.services.auth import get_current_user


router = APIRouter(
    prefix="/activities",
    tags=["Activities"]
)


@router.get("")
def get_activities(
    user_id: int | None = None,
    action: str | None = None,
    entity_type: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ========================================================
    # Validate date range
    # ========================================================

    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )

    # ========================================================
    # Base query
    #
    # Join User because AuditLog does not need to contain
    # organization_id directly. The organization is determined
    # from the user who generated the activity.
    # ========================================================

    query = (
        db.query(AuditLog)
        .join(
            User,
            AuditLog.user_id == User.id
        )
    )

    # ========================================================
    # Organization-level authorization
    # ========================================================

    # Every activity returned must belong to the current
    # user's organization.
    query = query.filter(
        User.organization_id == current_user.organization_id
    )

    # ========================================================
    # User-level authorization
    # ========================================================

    if current_user.role == UserRole.ADMINISTRATOR:
        # Administrator can view activities of users
        # within their own organization.

        if user_id is not None:
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

    else:
        # Non-administrators can only view their own activities.
        query = query.filter(
            AuditLog.user_id == current_user.id
        )

        # Prevent another user's activities from being requested.
        if (
            user_id is not None
            and user_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission to view "
                    "this user's activities"
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
    # Filter by start date
    # ========================================================

    if start_date is not None:
        start_datetime = datetime.combine(
            start_date,
            time.min
        )

        query = query.filter(
            AuditLog.created_at >= start_datetime
        )

    # ========================================================
    # Filter by end date
    # ========================================================

    if end_date is not None:
        end_datetime = datetime.combine(
            end_date,
            time.max
        )

        query = query.filter(
            AuditLog.created_at <= end_datetime
        )

    # ========================================================
    # Pagination
    # ========================================================

    offset = (page - 1) * page_size

    activities = (
        query
        .order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return activities