from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db

from app.schemas.reports import (
    DecisionReportResponse,
    ApprovalReportResponse,
    TeamReportResponse,
)

from app.services.report_service import (
    get_decision_report,
    get_approval_report,
    get_team_report,
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


# =========================================================
# DECISION REPORT
# =========================================================

@router.get(
    "/decisions",
    response_model=DecisionReportResponse,
)
def decision_report(
    category: str | None = Query(default=None),
    decision_status: str | None = Query(default=None),
    created_by: int | None = Query(default=None, ge=1),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    tag: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: Literal[
        "created_at",
        "updated_at",
        "title",
    ] = Query(default="created_at"),
    sort_order: Literal[
        "asc",
        "desc",
    ] = Query(default="desc"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if (
        start_date is not None
        and end_date is not None
        and end_date < start_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="end_date must be greater than or equal to start_date",
        )

    return get_decision_report(
        db=db,
        category=category,
        decision_status=decision_status,
        created_by=created_by,
        start_date=start_date,
        end_date=end_date,
        tag=tag,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# =========================================================
# APPROVAL REPORT
# =========================================================

@router.get(
    "/approvals",
    response_model=ApprovalReportResponse,
)
def approval_report(
    approval_status: str | None = Query(default=None),
    reviewer_id: int | None = Query(default=None, ge=1),
    decision_id: int | None = Query(default=None, ge=1),
    approval_level: str | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: Literal[
        "created_at",
        "completed_at",
        "decision_title",
    ] = Query(default="created_at"),
    sort_order: Literal[
        "asc",
        "desc",
    ] = Query(default="desc"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if (
        start_date is not None
        and end_date is not None
        and end_date < start_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="end_date must be greater than or equal to start_date",
        )

    return get_approval_report(
        db=db,
        approval_status=approval_status,
        reviewer_id=reviewer_id,
        decision_id=decision_id,
        approval_level=approval_level,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# =========================================================
# TEAM REPORT
# =========================================================

@router.get("/teams", response_model=TeamReportResponse)
def team_report(
    team: str | None = Query(default=None),
    decision_status: str | None = Query(default=None),
    category: str | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: Literal[
        "team_name",
        "member_count",
        "total_decisions",
        "approved_decisions",
        "rejected_decisions",
        "pending_decisions",
        "total_approvals",
        "approved_approvals",
        "rejected_approvals",
        "pending_approvals",
        "approval_completion_rate",
    ] = Query(default="team_name"),
    sort_order: Literal["asc", "desc"] = Query(default="asc"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if start_date is not None and end_date is not None and end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="end_date must be greater than or equal to start_date",
        )

    return get_team_report(
        db=db,
        team=team,
        decision_status=decision_status,
        category=category,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
