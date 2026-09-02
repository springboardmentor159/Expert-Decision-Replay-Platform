from datetime import date, datetime, time, timedelta
from typing import Optional
from app.models.audit_log import AuditLog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from io import BytesIO

from fastapi.responses import StreamingResponse

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from app.db.database import get_db
from app.core.security import get_current_user

from app.models.decision import Decision
from app.models.user import User
from app.models.approval import Approval
from app.models.team import Team


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


# ============================================================
# DECISION REPORT
# GET /reports/decisions
# ============================================================

@router.get("/decisions")
def get_decision_report(
    category: Optional[str] = Query(
        None,
        description="Filter decisions by category"
    ),
    decision_status: Optional[str] = Query(
        None,
        alias="status",
        description="Filter decisions by status"
    ),
    created_by: Optional[int] = Query(
        None,
        description="Filter decisions by creator user ID"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Filter decisions created from this date"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Filter decisions created up to this date"
    ),
    tag: Optional[str] = Query(
        None,
        description="Filter decisions by tag name"
    ),
    page: int = Query(
        1,
        ge=1,
        description="Page number"
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of records per page"
    ),
    sort_by: str = Query(
        "created_at",
        description="Sort field: created_at, updated_at, title"
    ),
    sort_order: str = Query(
        "desc",
        description="Sort order: asc or desc"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )

    allowed_statuses = {
        "Draft",
        "Under Review",
        "Approved",
        "Rejected",
        "Archived"
    }

    if decision_status:
        matched_status = None

        for allowed_status in allowed_statuses:
            if allowed_status.lower() == decision_status.lower():
                matched_status = allowed_status
                break

        if matched_status is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Invalid status. Allowed values are: "
                    "Draft, Under Review, Approved, Rejected, Archived"
                )
            )

        decision_status = matched_status

    allowed_sort_fields = {
        "created_at": Decision.created_at,
        "updated_at": Decision.updated_at,
        "title": Decision.title
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid sort field. Allowed values are: "
                "created_at, updated_at, title"
            )
        )

    if sort_order.lower() not in {"asc", "desc"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="sort_order must be either 'asc' or 'desc'"
        )

    query = (
        db.query(Decision)
        .options(
            joinedload(Decision.user),
            joinedload(Decision.alternatives),
            joinedload(Decision.approvals),
            joinedload(Decision.tags)
        )
    )

    if category:
        query = query.filter(
            Decision.category == category
        )

    if decision_status:
        query = query.filter(
            Decision.status == decision_status
        )

    if created_by is not None:
        query = query.filter(
            Decision.created_by == created_by
        )

    if start_date:
        start_datetime = datetime.combine(
            start_date,
            time.min
        )

        query = query.filter(
            Decision.created_at >= start_datetime
        )

    if end_date:
        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min
        )

        query = query.filter(
            Decision.created_at < end_datetime
        )

    if tag:
        query = query.filter(
            Decision.tags.any(name=tag)
        )

    total_decisions = query.count()

    draft_count = query.filter(
        Decision.status == "Draft"
    ).count()

    under_review_count = query.filter(
        Decision.status == "Under Review"
    ).count()

    approved_count = query.filter(
        Decision.status == "Approved"
    ).count()

    rejected_count = query.filter(
        Decision.status == "Rejected"
    ).count()

    archived_count = query.filter(
        Decision.status == "Archived"
    ).count()

    sort_column = allowed_sort_fields[sort_by]

    if sort_order.lower() == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    offset = (page - 1) * page_size

    decisions = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    items = []

    for decision in decisions:
        tags = [
            current_tag.name
            for current_tag in decision.tags
        ]

        items.append(
            {
                "decision_id": decision.id,
                "title": decision.title,
                "category": decision.category,
                "status": decision.status,
                "created_by": {
                    "user_id": (
                        decision.user.id
                        if decision.user
                        else decision.created_by
                    ),
                    "name": (
                        decision.user.full_name
                        if decision.user
                        else None
                    )
                },
                "created_date": decision.created_at,
                "updated_date": decision.updated_at,
                "number_of_alternatives": len(
                    decision.alternatives
                ),
                "number_of_approvals": len(
                    decision.approvals
                ),
                "tags": tags
            }
        )

    return {
        "report": "Decision Report",
        "generated_at": datetime.utcnow(),

        "filters": {
            "category": category,
            "status": decision_status,
            "created_by": created_by,
            "start_date": start_date,
            "end_date": end_date,
            "tag": tag
        },

        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total_decisions,
            "total_pages": (
                (total_decisions + page_size - 1)
                // page_size
                if total_decisions > 0
                else 0
            )
        },

        "summary": {
            "total_decisions": total_decisions,
            "draft_decisions": draft_count,
            "decisions_under_review": under_review_count,
            "approved_decisions": approved_count,
            "rejected_decisions": rejected_count,
            "archived_decisions": archived_count
        },

        "sorting": {
            "sort_by": sort_by,
            "sort_order": sort_order.lower()
        },

        "items": items
    }


# ============================================================
# APPROVAL REPORT
# GET /reports/approvals
# ============================================================

@router.get("/approvals")
def get_approval_report(
    approval_status: Optional[str] = Query(
        None,
        alias="status",
        description="Filter approvals by status"
    ),
    reviewer: Optional[int] = Query(
        None,
        description="Filter approvals by reviewer user ID"
    ),
    decision: Optional[int] = Query(
        None,
        description="Filter approvals by decision ID"
    ),
    approval_level: Optional[int] = Query(
        None,
        description="Filter approvals by approval level"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Filter approvals assigned from this date"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Filter approvals assigned up to this date"
    ),
    page: int = Query(
        1,
        ge=1,
        description="Page number"
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of records per page"
    ),
    sort_by: str = Query(
        "assigned_date",
        description=(
            "Sort field: assigned_date, completed_date, "
            "approval_level"
        )
    ),
    sort_order: str = Query(
        "desc",
        description="Sort order: asc or desc"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )

    allowed_statuses = {
        "Pending",
        "Approved",
        "Rejected"
    }

    if approval_status:
        matched_status = None

        for allowed_status in allowed_statuses:
            if allowed_status.lower() == approval_status.lower():
                matched_status = allowed_status
                break

        if matched_status is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Invalid approval status. Allowed values are: "
                    "Pending, Approved, Rejected"
                )
            )

        approval_status = matched_status

    allowed_sort_fields = {
        "assigned_date": Approval.created_at,
        "completed_date": Approval.completed_at,
        "approval_level": Approval.approval_level
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid sort field. Allowed values are: "
                "assigned_date, completed_date, approval_level"
            )
        )

    if sort_order.lower() not in {"asc", "desc"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="sort_order must be either 'asc' or 'desc'"
        )

    query = (
        db.query(Approval)
        .join(
            Decision,
            Approval.decision_id == Decision.id
        )
        .options(
            joinedload(Approval.decision),
            joinedload(Approval.reviewer)
        )
    )

    if approval_status:
        query = query.filter(
            Approval.status == approval_status
        )

    if reviewer is not None:
        query = query.filter(
            Approval.reviewer_id == reviewer
        )

    if decision is not None:
        query = query.filter(
            Approval.decision_id == decision
        )

    if approval_level is not None:
        if approval_level < 1:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "approval_level must be greater than or equal to 1"
                )
            )

        query = query.filter(
            Approval.approval_level == approval_level
        )

    if start_date:
        start_datetime = datetime.combine(
            start_date,
            time.min
        )

        query = query.filter(
            Approval.created_at >= start_datetime
        )

    if end_date:
        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min
        )

        query = query.filter(
            Approval.created_at < end_datetime
        )

    total_approvals = query.count()

    pending_approvals = query.filter(
        Approval.status == "Pending"
    ).count()

    approved_approvals = query.filter(
        Approval.status == "Approved"
    ).count()

    rejected_approvals = query.filter(
        Approval.status == "Rejected"
    ).count()

    completed_approvals = (
        query
        .filter(
            Approval.completed_at.isnot(None)
        )
        .all()
    )

    turnaround_times = []

    for approval in completed_approvals:
        if approval.created_at and approval.completed_at:
            duration = (
                approval.completed_at -
                approval.created_at
            )

            turnaround_times.append(
                duration.total_seconds()
            )

    if turnaround_times:
        average_turnaround_seconds = (
            sum(turnaround_times)
            / len(turnaround_times)
        )

        average_turnaround_hours = (
            average_turnaround_seconds / 3600
        )
    else:
        average_turnaround_hours = 0

    if total_approvals > 0:
        completed_count = (
            approved_approvals +
            rejected_approvals
        )

        completion_rate = (
            completed_count /
            total_approvals
        ) * 100
    else:
        completion_rate = 0

    sort_column = allowed_sort_fields[sort_by]

    if sort_order.lower() == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    offset = (page - 1) * page_size

    approvals = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    items = []

    for approval in approvals:

        turnaround_hours = None

        if (
            approval.created_at
            and approval.completed_at
        ):
            duration = (
                approval.completed_at -
                approval.created_at
            )

            turnaround_hours = (
                duration.total_seconds() / 3600
            )

        reviewer_name = None

        if approval.reviewer:
            reviewer_name = (
                getattr(
                    approval.reviewer,
                    "full_name",
                    None
                )
                or getattr(
                    approval.reviewer,
                    "name",
                    None
                )
                or approval.reviewer.email
            )

        items.append(
            {
                "approval_id": approval.id,
                "decision_id": approval.decision_id,

                "decision_title": (
                    approval.decision.title
                    if approval.decision
                    else None
                ),

                "reviewer": {
                    "user_id": approval.reviewer_id,
                    "name": reviewer_name
                },

                "approval_level": approval.approval_level,
                "approval_status": approval.status,
                "assigned_date": approval.created_at,
                "completed_date": approval.completed_at,

                "approval_turnaround_time_hours":
                    turnaround_hours
            }
        )

    return {
        "report": "Approval Report",
        "generated_at": datetime.utcnow(),

        "filters": {
            "status": approval_status,
            "reviewer": reviewer,
            "decision": decision,
            "approval_level": approval_level,
            "start_date": start_date,
            "end_date": end_date
        },

        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total_approvals,
            "total_pages": (
                (
                    total_approvals +
                    page_size -
                    1
                )
                // page_size
                if total_approvals > 0
                else 0
            )
        },

        "summary": {
            "total_approvals": total_approvals,
            "pending_approvals": pending_approvals,
            "approved_approvals": approved_approvals,
            "rejected_approvals": rejected_approvals,

            "average_approval_turnaround_time_hours":
                round(
                    average_turnaround_hours,
                    2
                ),

            "approval_completion_rate_percent":
                round(
                    completion_rate,
                    2
                )
        },

        "sorting": {
            "sort_by": sort_by,
            "sort_order": sort_order.lower()
        },

        "items": items
    }


# ============================================================
# TEAM REPORT
# GET /reports/teams
# ============================================================

@router.get("/teams")
def get_team_report(
    team_id: Optional[int] = Query(
        None,
        description="Filter report by team ID"
    ),
    team: Optional[str] = Query(
        None,
        description="Filter report by team name"
    ),
    decision_status: Optional[str] = Query(
        None,
        alias="status",
        description="Filter decisions by status"
    ),
    category: Optional[str] = Query(
        None,
        description="Filter decisions by category"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Filter decisions created from this date"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Filter decisions created up to this date"
    ),
    page: int = Query(
        1,
        ge=1,
        description="Page number"
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of teams per page"
    ),
    sort_by: str = Query(
        "team_name",
        description=(
            "Sort field: team_name, member_count, "
            "total_decisions, approved_decisions, "
            "rejected_decisions, pending_decisions"
        )
    ),
    sort_order: str = Query(
        "asc",
        description="Sort order: asc or desc"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ========================================================
    # DATE VALIDATION
    # ========================================================

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )

    # ========================================================
    # TEAM ID VALIDATION
    # ========================================================

    if team_id is not None and team_id < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="team_id must be greater than or equal to 1"
        )

    # ========================================================
    # DECISION STATUS VALIDATION
    # ========================================================

    allowed_statuses = {
        "Draft",
        "Under Review",
        "Approved",
        "Rejected",
        "Archived"
    }

    if decision_status:
        matched_status = None

        for allowed_status in allowed_statuses:
            if allowed_status.lower() == decision_status.lower():
                matched_status = allowed_status
                break

        if matched_status is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Invalid status. Allowed values are: "
                    "Draft, Under Review, Approved, Rejected, Archived"
                )
            )

        decision_status = matched_status

    # ========================================================
    # SORTING VALIDATION
    # ========================================================

    allowed_sort_fields = {
        "team_name": Team.name,
        "member_count": None,
        "total_decisions": None,
        "approved_decisions": None,
        "rejected_decisions": None,
        "pending_decisions": None
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid sort field. Allowed values are: "
                "team_name, member_count, total_decisions, "
                "approved_decisions, rejected_decisions, "
                "pending_decisions"
            )
        )

    if sort_order.lower() not in {"asc", "desc"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="sort_order must be either 'asc' or 'desc'"
        )

    # ========================================================
    # TEAM QUERY
    # ========================================================

    team_query = db.query(Team)

    if team_id is not None:
        team_query = team_query.filter(
            Team.id == team_id
        )

    if team:
        team_query = team_query.filter(
            Team.name.ilike(f"%{team}%")
        )

    teams = team_query.all()

    report_items = []

    # ========================================================
    # BUILD TEAM REPORT
    # ========================================================

    for current_team in teams:

        # ----------------------------------------------------
        # MEMBER COUNT
        # ----------------------------------------------------

        member_count = (
            db.query(User)
            .filter(
                User.team_id == current_team.id
            )
            .count()
        )

        # ----------------------------------------------------
        # DECISION QUERY FOR THIS TEAM
        # ----------------------------------------------------

        decision_query = (
            db.query(Decision)
            .join(
                User,
                Decision.created_by == User.id
            )
            .filter(
                User.team_id == current_team.id
            )
        )

        # ----------------------------------------------------
        # CATEGORY FILTER
        # ----------------------------------------------------

        if category:
            decision_query = decision_query.filter(
                Decision.category == category
            )

        # ----------------------------------------------------
        # STATUS FILTER
        # ----------------------------------------------------

        if decision_status:
            decision_query = decision_query.filter(
                Decision.status == decision_status
            )

        # ----------------------------------------------------
        # START DATE FILTER
        # ----------------------------------------------------

        if start_date:
            start_datetime = datetime.combine(
                start_date,
                time.min
            )

            decision_query = decision_query.filter(
                Decision.created_at >= start_datetime
            )

        # ----------------------------------------------------
        # END DATE FILTER
        # ----------------------------------------------------

        if end_date:
            end_datetime = datetime.combine(
                end_date + timedelta(days=1),
                time.min
            )

            decision_query = decision_query.filter(
                Decision.created_at < end_datetime
            )

        # ----------------------------------------------------
        # DECISION COUNTS
        # ----------------------------------------------------

        total_decisions = decision_query.count()

        approved_decisions = (
            decision_query
            .filter(Decision.status == "Approved")
            .count()
        )

        rejected_decisions = (
            decision_query
            .filter(Decision.status == "Rejected")
            .count()
        )

        pending_decisions = (
            decision_query
            .filter(
                Decision.status.in_(
                    ["Draft", "Under Review"]
                )
            )
            .count()
        )

        # ----------------------------------------------------
        # APPROVAL STATISTICS
        # ----------------------------------------------------

        approval_query = (
            db.query(Approval)
            .join(
                Decision,
                Approval.decision_id == Decision.id
            )
            .join(
                User,
                Decision.created_by == User.id
            )
            .filter(
                User.team_id == current_team.id
            )
        )

        if category:
            approval_query = approval_query.filter(
                Decision.category == category
            )

        if decision_status:
            approval_query = approval_query.filter(
                Decision.status == decision_status
            )

        if start_date:
            start_datetime = datetime.combine(
                start_date,
                time.min
            )

            approval_query = approval_query.filter(
                Decision.created_at >= start_datetime
            )

        if end_date:
            end_datetime = datetime.combine(
                end_date + timedelta(days=1),
                time.min
            )

            approval_query = approval_query.filter(
                Decision.created_at < end_datetime
            )

        total_approvals = approval_query.count()

        pending_approvals = (
            approval_query
            .filter(Approval.status == "Pending")
            .count()
        )

        approved_approvals = (
            approval_query
            .filter(Approval.status == "Approved")
            .count()
        )

        rejected_approvals = (
            approval_query
            .filter(Approval.status == "Rejected")
            .count()
        )

        completed_approvals = (
            approved_approvals +
            rejected_approvals
        )

        if total_approvals > 0:
            approval_completion_rate = (
                completed_approvals /
                total_approvals
            ) * 100
        else:
            approval_completion_rate = 0

        # ----------------------------------------------------
        # ADD TEAM ITEM
        # ----------------------------------------------------

        report_items.append(
            {
                "team_id": current_team.id,
                "team_name": current_team.name,

                "member_count": member_count,

                "decisions": {
                    "total": total_decisions,
                    "approved": approved_decisions,
                    "rejected": rejected_decisions,
                    "pending": pending_decisions
                },

                "approval_statistics": {
                    "total_approvals": total_approvals,
                    "pending_approvals": pending_approvals,
                    "approved_approvals": approved_approvals,
                    "rejected_approvals": rejected_approvals,
                    "completion_rate_percent": round(
                        approval_completion_rate,
                        2
                    )
                }
            }
        )

    # ========================================================
    # CONTROLLED SORTING
    # ========================================================

    reverse_sort = sort_order.lower() == "desc"

    if sort_by == "team_name":
        report_items.sort(
            key=lambda item: item["team_name"].lower(),
            reverse=reverse_sort
        )

    elif sort_by == "member_count":
        report_items.sort(
            key=lambda item: item["member_count"],
            reverse=reverse_sort
        )

    elif sort_by == "total_decisions":
        report_items.sort(
            key=lambda item: item["decisions"]["total"],
            reverse=reverse_sort
        )

    elif sort_by == "approved_decisions":
        report_items.sort(
            key=lambda item: item["decisions"]["approved"],
            reverse=reverse_sort
        )

    elif sort_by == "rejected_decisions":
        report_items.sort(
            key=lambda item: item["decisions"]["rejected"],
            reverse=reverse_sort
        )

    elif sort_by == "pending_decisions":
        report_items.sort(
            key=lambda item: item["decisions"]["pending"],
            reverse=reverse_sort
        )

    # ========================================================
    # PAGINATION
    # ========================================================

    total_teams = len(report_items)

    offset = (page - 1) * page_size

    paginated_items = report_items[
        offset:offset + page_size
    ]

    # ========================================================
    # RETURN TEAM REPORT
    # ========================================================

    return {
        "report": "Team Report",

        "generated_at": datetime.utcnow(),

        "filters": {
            "team_id": team_id,
            "team": team,
            "status": decision_status,
            "category": category,
            "start_date": start_date,
            "end_date": end_date
        },

        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total_teams,
            "total_pages": (
                (total_teams + page_size - 1)
                // page_size
                if total_teams > 0
                else 0
            )
        },

        "sorting": {
            "sort_by": sort_by,
            "sort_order": sort_order.lower()
        },

        "summary": {
            "total_teams": total_teams,
            "teams_with_decisions": sum(
                1
                for item in report_items
                if item["decisions"]["total"] > 0
            )
        },

        "items": paginated_items
    }
# ============================================================
# AUDIT REPORT
# GET /reports/audit
# ============================================================

@router.get("/audit")
def get_audit_report(
    user_id: Optional[int] = Query(
        None,
        description="Filter audit logs by user ID"
    ),
    action: Optional[str] = Query(
        None,
        description="Filter audit logs by action"
    ),
    entity_type: Optional[str] = Query(
        None,
        description="Filter audit logs by entity type"
    ),
    entity_id: Optional[int] = Query(
        None,
        description="Filter audit logs by entity ID"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Filter audit logs from this date"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Filter audit logs up to this date"
    ),
    page: int = Query(
        1,
        ge=1,
        description="Page number"
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of audit records per page"
    ),
    sort_by: str = Query(
        "created_at",
        description=(
            "Sort field: created_at, action, entity_type, entity_id"
        )
    ),
    sort_order: str = Query(
        "desc",
        description="Sort order: asc or desc"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ========================================================
    # ADMIN AUTHORIZATION
    # ========================================================

    if current_user.role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # ========================================================
    # DATE RANGE VALIDATION
    # ========================================================

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )

    # ========================================================
    # ID VALIDATION
    # ========================================================

    if user_id is not None and user_id < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="user_id must be greater than or equal to 1"
        )

    if entity_id is not None and entity_id < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="entity_id must be greater than or equal to 1"
        )

    # ========================================================
    # SORTING VALIDATION
    # ========================================================

    allowed_sort_fields = {
        "created_at": AuditLog.created_at,
        "action": AuditLog.action,
        "entity_type": AuditLog.entity_type,
        "entity_id": AuditLog.entity_id
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid sort field. Allowed values are: "
                "created_at, action, entity_type, entity_id"
            )
        )

    if sort_order.lower() not in {"asc", "desc"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="sort_order must be either 'asc' or 'desc'"
        )

    # ========================================================
    # BASE QUERY
    # ========================================================

    query = (
        db.query(AuditLog)
        .outerjoin(
            User,
            AuditLog.user_id == User.id
        )
    )

    # ========================================================
    # FILTER: USER
    # ========================================================

    if user_id is not None:
        query = query.filter(
            AuditLog.user_id == user_id
        )

    # ========================================================
    # FILTER: ACTION
    # ========================================================

    if action:
        query = query.filter(
            AuditLog.action.ilike(action)
        )

    # ========================================================
    # FILTER: ENTITY TYPE
    # ========================================================

    if entity_type:
        query = query.filter(
            AuditLog.entity_type.ilike(entity_type)
        )

    # ========================================================
    # FILTER: ENTITY ID
    # ========================================================

    if entity_id is not None:
        query = query.filter(
            AuditLog.entity_id == entity_id
        )

    # ========================================================
    # FILTER: START DATE
    # ========================================================

    if start_date:
        start_datetime = datetime.combine(
            start_date,
            time.min
        )

        query = query.filter(
            AuditLog.created_at >= start_datetime
        )

    # ========================================================
    # FILTER: END DATE
    # ========================================================

    if end_date:
        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min
        )

        query = query.filter(
            AuditLog.created_at < end_datetime
        )

    # ========================================================
    # TOTAL AUDIT RECORDS
    # ========================================================

    total_audit_logs = query.count()

    # ========================================================
    # SUMMARY
    # ========================================================

    unique_users = (
        query
        .filter(AuditLog.user_id.isnot(None))
        .with_entities(AuditLog.user_id)
        .distinct()
        .count()
    )

    unique_actions = (
        query
        .with_entities(AuditLog.action)
        .distinct()
        .count()
    )

    unique_entities = (
        query
        .with_entities(
            AuditLog.entity_type,
            AuditLog.entity_id
        )
        .distinct()
        .count()
    )

    # ========================================================
    # SORTING
    # ========================================================

    sort_column = allowed_sort_fields[sort_by]

    if sort_order.lower() == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    # ========================================================
    # PAGINATION
    # ========================================================

    offset = (page - 1) * page_size

    audit_logs = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # ========================================================
    # BUILD REPORT ITEMS
    # ========================================================

    items = []

    for audit_log in audit_logs:

        user_name = None
        user_email = None

        if audit_log.user_id is not None:
            user = (
                db.query(User)
                .filter(
                    User.id == audit_log.user_id
                )
                .first()
            )

            if user:
                user_name = user.full_name
                user_email = user.email

        items.append(
            {
                "audit_log_id": audit_log.id,

                "user": {
                    "user_id": audit_log.user_id,
                    "name": user_name,
                    "email": user_email
                },

                "action": audit_log.action,

                "entity_type": audit_log.entity_type,

                "entity_id": audit_log.entity_id,

                "description": audit_log.description,

                "ip_address": audit_log.ip_address,

                "old_value": audit_log.old_value,

                "new_value": audit_log.new_value,

                "request_method": audit_log.request_method,

                "endpoint": audit_log.endpoint,

                "created_at": audit_log.created_at
            }
        )

    # ========================================================
    # RETURN REPORT
    # ========================================================

    return {
        "report": "Audit Report",

        "generated_at": datetime.utcnow(),

        "filters": {
            "user_id": user_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "start_date": start_date,
            "end_date": end_date
        },

        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total_audit_logs,
            "total_pages": (
                (
                    total_audit_logs +
                    page_size -
                    1
                )
                // page_size
                if total_audit_logs > 0
                else 0
            )
        },

        "summary": {
            "total_audit_logs": total_audit_logs,
            "unique_users": unique_users,
            "unique_actions": unique_actions,
            "unique_entities": unique_entities
        },

        "sorting": {
            "sort_by": sort_by,
            "sort_order": sort_order.lower()
        },

        "items": items
    }
# ============================================================
# DECISION REPORT PDF EXPORT
# GET /reports/decisions/pdf
# ============================================================

@router.get("/decisions/pdf")
def export_decision_report_pdf(
    category: Optional[str] = Query(
        None,
        description="Filter decisions by category"
    ),
    decision_status: Optional[str] = Query(
        None,
        alias="status",
        description="Filter decisions by status"
    ),
    created_by: Optional[int] = Query(
        None,
        description="Filter decisions by creator user ID"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Filter decisions created from this date"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Filter decisions created up to this date"
    ),
    tag: Optional[str] = Query(
        None,
        description="Filter decisions by tag name"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ========================================================
    # DATE VALIDATION
    # ========================================================

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )

    # ========================================================
    # STATUS VALIDATION
    # ========================================================

    allowed_statuses = {
        "Draft",
        "Under Review",
        "Approved",
        "Rejected",
        "Archived"
    }

    if decision_status:
        matched_status = None

        for allowed_status in allowed_statuses:
            if allowed_status.lower() == decision_status.lower():
                matched_status = allowed_status
                break

        if matched_status is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Invalid status. Allowed values are: "
                    "Draft, Under Review, Approved, Rejected, Archived"
                )
            )

        decision_status = matched_status

    # ========================================================
    # QUERY
    # ========================================================

    query = (
        db.query(Decision)
        .options(
            joinedload(Decision.user),
            joinedload(Decision.alternatives),
            joinedload(Decision.approvals),
            joinedload(Decision.tags)
        )
    )

    if category:
        query = query.filter(
            Decision.category == category
        )

    if decision_status:
        query = query.filter(
            Decision.status == decision_status
        )

    if created_by is not None:
        query = query.filter(
            Decision.created_by == created_by
        )

    if start_date:
        start_datetime = datetime.combine(
            start_date,
            time.min
        )

        query = query.filter(
            Decision.created_at >= start_datetime
        )

    if end_date:
        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min
        )

        query = query.filter(
            Decision.created_at < end_datetime
        )

    if tag:
        query = query.filter(
            Decision.tags.any(name=tag)
        )

    decisions = (
        query
        .order_by(Decision.created_at.desc())
        .all()
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    total_decisions = len(decisions)

    draft_count = sum(
        1 for d in decisions
        if d.status == "Draft"
    )

    under_review_count = sum(
        1 for d in decisions
        if d.status == "Under Review"
    )

    approved_count = sum(
        1 for d in decisions
        if d.status == "Approved"
    )

    rejected_count = sum(
        1 for d in decisions
        if d.status == "Rejected"
    )

    archived_count = sum(
        1 for d in decisions
        if d.status == "Archived"
    )

    # ========================================================
    # CREATE PDF
    # ========================================================

    pdf_buffer = BytesIO()

    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=landscape(A4),
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "Decision Report",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            f"Generated at: {datetime.utcnow()}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 12))

    # ========================================================
    # SUMMARY TABLE
    # ========================================================

    summary_data = [
        [
            "Total",
            "Draft",
            "Under Review",
            "Approved",
            "Rejected",
            "Archived"
        ],
        [
            str(total_decisions),
            str(draft_count),
            str(under_review_count),
            str(approved_count),
            str(rejected_count),
            str(archived_count)
        ]
    ]

    summary_table = Table(
        summary_data,
        repeatRows=1
    )

    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8)
            ]
        )
    )

    elements.append(summary_table)

    elements.append(Spacer(1, 15))

    # ========================================================
    # DECISION DATA TABLE
    # ========================================================

    table_data = [
        [
            "ID",
            "Title",
            "Category",
            "Status",
            "Created By",
            "Created Date",
            "Updated Date",
            "Alternatives",
            "Approvals",
            "Tags"
        ]
    ]

    for decision in decisions:

        creator_name = (
            decision.user.full_name
            if decision.user
            else "Unknown"
        )

        tags = ", ".join(
            current_tag.name
            for current_tag in decision.tags
        )

        table_data.append(
            [
                str(decision.id),
                decision.title,
                decision.category,
                decision.status,
                creator_name,
                str(decision.created_at),
                str(decision.updated_at),
                str(len(decision.alternatives)),
                str(len(decision.approvals)),
                tags
            ]
        )

    decision_table = Table(
        table_data,
        repeatRows=1,
        colWidths=[
            35,
            120,
            75,
            75,
            80,
            100,
            100,
            55,
            50,
            100
        ]
    )

    decision_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.black
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (0, -1),
                    "CENTER"
                )
            ]
        )
    )

    elements.append(decision_table)

    # ========================================================
    # BUILD PDF
    # ========================================================

    document.build(elements)

    pdf_buffer.seek(0)

    # ========================================================
    # RETURN PDF
    # ========================================================

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=decision_report.pdf"
        }
    )
# ============================================================
# APPROVAL REPORT PDF EXPORT
# GET /reports/approvals/pdf
# ============================================================

@router.get("/approvals/pdf")
def export_approval_report_pdf(
    approval_status: Optional[str] = Query(
        None,
        alias="status",
        description="Filter approvals by status"
    ),
    reviewer: Optional[int] = Query(
        None,
        description="Filter approvals by reviewer user ID"
    ),
    decision: Optional[int] = Query(
        None,
        description="Filter approvals by decision ID"
    ),
    approval_level: Optional[int] = Query(
        None,
        description="Filter approvals by approval level"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Filter approvals assigned from this date"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Filter approvals assigned up to this date"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ========================================================
    # DATE VALIDATION
    # ========================================================

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )

    # ========================================================
    # STATUS VALIDATION
    # ========================================================

    allowed_statuses = {
        "Pending",
        "Approved",
        "Rejected"
    }

    if approval_status:
        matched_status = None

        for allowed_status in allowed_statuses:
            if allowed_status.lower() == approval_status.lower():
                matched_status = allowed_status
                break

        if matched_status is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Invalid approval status. Allowed values are: "
                    "Pending, Approved, Rejected"
                )
            )

        approval_status = matched_status

    # ========================================================
    # APPROVAL LEVEL VALIDATION
    # ========================================================

    if approval_level is not None and approval_level < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="approval_level must be greater than or equal to 1"
        )

    # ========================================================
    # QUERY
    # ========================================================

    query = (
        db.query(Approval)
        .join(
            Decision,
            Approval.decision_id == Decision.id
        )
        .options(
            joinedload(Approval.decision),
            joinedload(Approval.reviewer)
        )
    )

    if approval_status:
        query = query.filter(
            Approval.status == approval_status
        )

    if reviewer is not None:
        query = query.filter(
            Approval.reviewer_id == reviewer
        )

    if decision is not None:
        query = query.filter(
            Approval.decision_id == decision
        )

    if approval_level is not None:
        query = query.filter(
            Approval.approval_level == approval_level
        )

    if start_date:
        start_datetime = datetime.combine(
            start_date,
            time.min
        )

        query = query.filter(
            Approval.created_at >= start_datetime
        )

    if end_date:
        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min
        )

        query = query.filter(
            Approval.created_at < end_datetime
        )

    approvals = (
        query
        .order_by(Approval.created_at.desc())
        .all()
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    total_approvals = len(approvals)

    pending_count = sum(
        1
        for approval in approvals
        if approval.status == "Pending"
    )

    approved_count = sum(
        1
        for approval in approvals
        if approval.status == "Approved"
    )

    rejected_count = sum(
        1
        for approval in approvals
        if approval.status == "Rejected"
    )

    completed_count = (
        approved_count +
        rejected_count
    )

    if total_approvals > 0:
        completion_rate = (
            completed_count /
            total_approvals
        ) * 100
    else:
        completion_rate = 0

    # ========================================================
    # AVERAGE TURNAROUND
    # ========================================================

    turnaround_values = []

    for approval in approvals:

        if (
            approval.created_at
            and approval.completed_at
        ):
            duration = (
                approval.completed_at -
                approval.created_at
            )

            turnaround_values.append(
                duration.total_seconds() / 3600
            )

    if turnaround_values:
        average_turnaround = (
            sum(turnaround_values)
            / len(turnaround_values)
        )
    else:
        average_turnaround = 0

    # ========================================================
    # CREATE PDF
    # ========================================================

    pdf_buffer = BytesIO()

    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=landscape(A4),
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "Approval Report",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            f"Generated at: {datetime.utcnow()}",
            styles["Normal"]
        )
    )

    elements.append(
        Spacer(1, 12)
    )

    # ========================================================
    # SUMMARY TABLE
    # ========================================================

    summary_data = [
        [
            "Total",
            "Pending",
            "Approved",
            "Rejected",
            "Completion Rate",
            "Avg Turnaround (Hours)"
        ],
        [
            str(total_approvals),
            str(pending_count),
            str(approved_count),
            str(rejected_count),
            f"{completion_rate:.2f}%",
            f"{average_turnaround:.2f}"
        ]
    ]

    summary_table = Table(
        summary_data,
        repeatRows=1
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, 0),
                    8
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, 0),
                    8
                )
            ]
        )
    )

    elements.append(summary_table)

    elements.append(
        Spacer(1, 15)
    )

    # ========================================================
    # APPROVAL DATA TABLE
    # ========================================================

    table_data = [
        [
            "Approval ID",
            "Decision ID",
            "Decision Title",
            "Reviewer",
            "Level",
            "Status",
            "Assigned Date",
            "Completed Date",
            "Turnaround (Hours)"
        ]
    ]

    for approval in approvals:

        reviewer_name = (
            approval.reviewer.full_name
            if approval.reviewer
            else "Unknown"
        )

        turnaround_hours = ""

        if (
            approval.created_at
            and approval.completed_at
        ):
            duration = (
                approval.completed_at -
                approval.created_at
            )

            turnaround_hours = (
                f"{duration.total_seconds() / 3600:.2f}"
            )

        table_data.append(
            [
                str(approval.id),
                str(approval.decision_id),

                (
                    approval.decision.title
                    if approval.decision
                    else "Unknown"
                ),

                reviewer_name,

                str(approval.approval_level),

                approval.status,

                str(approval.created_at),

                (
                    str(approval.completed_at)
                    if approval.completed_at
                    else ""
                ),

                turnaround_hours
            ]
        )

    approval_table = Table(
        table_data,
        repeatRows=1,
        colWidths=[
            55,
            55,
            120,
            90,
            40,
            65,
            100,
            100,
            75
        ]
    )

    approval_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.black
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (1, -1),
                    "CENTER"
                )
            ]
        )
    )

    elements.append(
        approval_table
    )

    # ========================================================
    # BUILD PDF
    # ========================================================

    document.build(elements)

    pdf_buffer.seek(0)

    # ========================================================
    # RETURN PDF
    # ========================================================

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=approval_report.pdf"
        }
    )
# ============================================================
# TEAM REPORT PDF EXPORT
# GET /reports/teams/pdf
# ============================================================

@router.get("/teams/pdf")
def export_team_report_pdf(
    team_id: Optional[int] = Query(
        None,
        description="Filter by team ID"
    ),
    team: Optional[str] = Query(
        None,
        description="Filter by team name"
    ),
    decision_status: Optional[str] = Query(
        None,
        alias="status",
        description="Filter by decision status"
    ),
    category: Optional[str] = Query(
        None,
        description="Filter by decision category"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Filter decisions created from this date"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Filter decisions created up to this date"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # --------------------------------------------------------
    # Validate dates
    # --------------------------------------------------------
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )

    # --------------------------------------------------------
    # Validate decision status
    # --------------------------------------------------------
    allowed_statuses = {
        "Draft",
        "Under Review",
        "Approved",
        "Rejected",
        "Archived"
    }

    if decision_status:
        matched_status = None

        for allowed_status in allowed_statuses:
            if allowed_status.lower() == decision_status.lower():
                matched_status = allowed_status
                break

        if matched_status is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Invalid status. Allowed values are: "
                    "Draft, Under Review, Approved, Rejected, Archived"
                )
            )

        decision_status = matched_status

    # --------------------------------------------------------
    # Get teams
    # --------------------------------------------------------
    team_query = db.query(Team)

    if team_id is not None:
        team_query = team_query.filter(Team.id == team_id)

    if team:
        team_query = team_query.filter(Team.name.ilike(f"%{team}%"))

    teams = team_query.order_by(Team.name.asc()).all()

    # --------------------------------------------------------
    # Build report data
    # --------------------------------------------------------
    report_rows = []

    for team_obj in teams:

        # Members
        member_count = (
            db.query(User)
            .filter(User.team_id == team_obj.id)
            .count()
        )

        # Decisions created by members of this team
        decision_query = (
            db.query(Decision)
            .join(User, Decision.created_by == User.id)
            .filter(User.team_id == team_obj.id)
        )

        if decision_status:
            decision_query = decision_query.filter(
                Decision.status == decision_status
            )

        if category:
            decision_query = decision_query.filter(
                Decision.category == category
            )

        if start_date:
            start_datetime = datetime.combine(
                start_date,
                time.min
            )
            decision_query = decision_query.filter(
                Decision.created_at >= start_datetime
            )

        if end_date:
            end_datetime = datetime.combine(
                end_date + timedelta(days=1),
                time.min
            )
            decision_query = decision_query.filter(
                Decision.created_at < end_datetime
            )

        decisions = decision_query.all()

        total_decisions = len(decisions)

        approved_decisions = sum(
            1 for d in decisions
            if d.status == "Approved"
        )

        rejected_decisions = sum(
            1 for d in decisions
            if d.status == "Rejected"
        )

        pending_decisions = sum(
            1 for d in decisions
            if d.status in {"Draft", "Under Review"}
        )

        # ----------------------------------------------------
        # Approval statistics
        # ----------------------------------------------------
        decision_ids = [d.id for d in decisions]

        if decision_ids:
            approvals = (
                db.query(Approval)
                .filter(
                    Approval.decision_id.in_(decision_ids)
                )
                .all()
            )
        else:
            approvals = []

        total_approvals = len(approvals)

        approved_approvals = sum(
            1 for a in approvals
            if a.status == "Approved"
        )

        rejected_approvals = sum(
            1 for a in approvals
            if a.status == "Rejected"
        )

        pending_approvals = sum(
            1 for a in approvals
            if a.status == "Pending"
        )

        completed_approvals = (
            approved_approvals + rejected_approvals
        )

        approval_completion_rate = (
            (completed_approvals / total_approvals) * 100
            if total_approvals > 0
            else 0
        )

        report_rows.append({
            "team_name": team_obj.name,
            "member_count": member_count,
            "total_decisions": total_decisions,
            "approved_decisions": approved_decisions,
            "rejected_decisions": rejected_decisions,
            "pending_decisions": pending_decisions,
            "total_approvals": total_approvals,
            "approved_approvals": approved_approvals,
            "rejected_approvals": rejected_approvals,
            "pending_approvals": pending_approvals,
            "approval_completion_rate": approval_completion_rate
        })

    # --------------------------------------------------------
    # Create PDF
    # --------------------------------------------------------
    pdf_buffer = BytesIO()

    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=landscape(A4),
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(
        Paragraph(
            "Team Report",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            f"Generated at: {datetime.utcnow()}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 12))

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------
    total_teams = len(report_rows)

    total_members = sum(
        row["member_count"]
        for row in report_rows
    )

    total_decisions = sum(
        row["total_decisions"]
        for row in report_rows
    )

    total_approved = sum(
        row["approved_decisions"]
        for row in report_rows
    )

    total_rejected = sum(
        row["rejected_decisions"]
        for row in report_rows
    )

    total_pending = sum(
        row["pending_decisions"]
        for row in report_rows
    )

    summary_data = [
        [
            "Teams",
            "Members",
            "Decisions",
            "Approved",
            "Rejected",
            "Pending"
        ],
        [
            str(total_teams),
            str(total_members),
            str(total_decisions),
            str(total_approved),
            str(total_rejected),
            str(total_pending)
        ]
    ]

    summary_table = Table(
        summary_data,
        repeatRows=1
    )

    summary_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, 0),
                8
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, 0),
                8
            )
        ])
    )

    elements.append(summary_table)
    elements.append(Spacer(1, 15))

    # --------------------------------------------------------
    # Detailed table
    # --------------------------------------------------------
    table_data = [[
        "Team",
        "Members",
        "Total Decisions",
        "Approved",
        "Rejected",
        "Pending",
        "Total Approvals",
        "Approved Approvals",
        "Rejected Approvals",
        "Pending Approvals",
        "Approval Completion %"
    ]]

    for row in report_rows:
        table_data.append([
            row["team_name"],
            str(row["member_count"]),
            str(row["total_decisions"]),
            str(row["approved_decisions"]),
            str(row["rejected_decisions"]),
            str(row["pending_decisions"]),
            str(row["total_approvals"]),
            str(row["approved_approvals"]),
            str(row["rejected_approvals"]),
            str(row["pending_approvals"]),
            f'{row["approval_completion_rate"]:.2f}%'
        ])

    team_table = Table(
        table_data,
        repeatRows=1,
        colWidths=[
            85,
            50,
            70,
            55,
            55,
            55,
            65,
            70,
            70,
            70,
            75
        ]
    )

    team_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.black
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                6
            ),
            (
                "ALIGN",
                (1, 1),
                (-1, -1),
                "CENTER"
            )
        ])
    )

    elements.append(team_table)

    # --------------------------------------------------------
    # Build PDF
    # --------------------------------------------------------
    document.build(elements)

    pdf_buffer.seek(0)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=team_report.pdf"
        }
    )
# ============================================================
# DECISION REPORT EXCEL EXPORT
# GET /reports/decisions/excel
# ============================================================

@router.get("/decisions/excel")
def export_decision_report_excel(
    category: Optional[str] = Query(
        None,
        description="Filter decisions by category"
    ),
    decision_status: Optional[str] = Query(
        None,
        alias="status",
        description="Filter decisions by status"
    ),
    created_by: Optional[int] = Query(
        None,
        description="Filter decisions by creator user ID"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Filter decisions created from this date"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Filter decisions created up to this date"
    ),
    tag: Optional[str] = Query(
        None,
        description="Filter decisions by tag"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # --------------------------------------------------------
    # Validate dates
    # --------------------------------------------------------
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )

    # --------------------------------------------------------
    # Validate decision status
    # --------------------------------------------------------
    allowed_statuses = {
        "Draft",
        "Under Review",
        "Approved",
        "Rejected",
        "Archived"
    }

    if decision_status:
        matched_status = None

        for allowed_status in allowed_statuses:
            if allowed_status.lower() == decision_status.lower():
                matched_status = allowed_status
                break

        if matched_status is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Invalid status. Allowed values are: "
                    "Draft, Under Review, Approved, Rejected, Archived"
                )
            )

        decision_status = matched_status

    # --------------------------------------------------------
    # Query decisions
    # --------------------------------------------------------
    query = (
        db.query(Decision)
        .options(
            joinedload(Decision.user),
            joinedload(Decision.alternatives),
            joinedload(Decision.approvals),
            joinedload(Decision.tags)
        )
    )

    # --------------------------------------------------------
    # Apply filters
    # --------------------------------------------------------
    if category:
        query = query.filter(
            Decision.category == category
        )

    if decision_status:
        query = query.filter(
            Decision.status == decision_status
        )

    if created_by is not None:
        query = query.filter(
            Decision.created_by == created_by
        )

    if start_date:
        start_datetime = datetime.combine(
            start_date,
            time.min
        )

        query = query.filter(
            Decision.created_at >= start_datetime
        )

    if end_date:
        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min
        )

        query = query.filter(
            Decision.created_at < end_datetime
        )

    if tag:
        query = query.join(
            Decision.tags
        ).filter(
            Decision.tags.any(
                name=tag
            )
        )

    # --------------------------------------------------------
    # Get all matching decisions
    # --------------------------------------------------------
    decisions = (
        query
        .order_by(Decision.created_at.desc())
        .all()
    )

    # --------------------------------------------------------
    # Create Excel workbook
    # --------------------------------------------------------
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment
    from openpyxl.utils import get_column_letter

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Decision Report"

    # --------------------------------------------------------
    # Header row
    # --------------------------------------------------------
    headers = [
        "Decision ID",
        "Title",
        "Category",
        "Status",
        "Created By",
        "Created Date",
        "Updated Date",
        "Number of Alternatives",
        "Number of Approvals",
        "Tags"
    ]

    worksheet.append(headers)

    # Make headers bold
    for cell in worksheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(
            horizontal="center"
        )

    # --------------------------------------------------------
    # Add decision rows
    # --------------------------------------------------------
    for decision_item in decisions:

        created_by_name = "Unknown"

        if decision_item.user:
            created_by_name = (
                decision_item.user.full_name
                or decision_item.user.email
                or "Unknown"
            )

        tag_names = ", ".join(
            tag_item.name
            for tag_item in decision_item.tags
        )

        worksheet.append([
            decision_item.id,
            decision_item.title,
            decision_item.category,
            decision_item.status,
            created_by_name,
            decision_item.created_at,
            decision_item.updated_at,
            len(decision_item.alternatives),
            len(decision_item.approvals),
            tag_names
        ])

    # --------------------------------------------------------
    # Format worksheet
    # --------------------------------------------------------
    worksheet.freeze_panes = "A2"

    for column_cells in worksheet.columns:
        max_length = 0

        column_letter = get_column_letter(
            column_cells[0].column
        )

        for cell in column_cells:
            try:
                cell_length = len(str(cell.value))
                if cell_length > max_length:
                    max_length = cell_length
            except Exception:
                pass

        worksheet.column_dimensions[
            column_letter
        ].width = min(max_length + 2, 40)

    # --------------------------------------------------------
    # Save workbook to memory
    # --------------------------------------------------------
    excel_buffer = BytesIO()

    workbook.save(excel_buffer)
    excel_buffer.seek(0)

    # --------------------------------------------------------
    # Return Excel file
    # --------------------------------------------------------
    return StreamingResponse(
        excel_buffer,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=decision_report.xlsx"
        }
    )
# ============================================================
# TEAM REPORT EXCEL EXPORT
# GET /reports/teams/excel
# ============================================================

@router.get("/teams/excel")
def export_team_report_excel(
    team_id: Optional[int] = Query(
        None,
        description="Filter by team ID"
    ),
    team: Optional[str] = Query(
        None,
        description="Filter by team name"
    ),
    decision_status: Optional[str] = Query(
        None,
        alias="status",
        description="Filter by decision status"
    ),
    category: Optional[str] = Query(
        None,
        description="Filter by decision category"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Filter decisions created from this date"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Filter decisions created up to this date"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # --------------------------------------------------------
    # Validate dates
    # --------------------------------------------------------
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )

    # --------------------------------------------------------
    # Validate decision status
    # --------------------------------------------------------
    allowed_statuses = {
        "Draft",
        "Under Review",
        "Approved",
        "Rejected",
        "Archived"
    }

    if decision_status:
        matched_status = None

        for allowed_status in allowed_statuses:
            if allowed_status.lower() == decision_status.lower():
                matched_status = allowed_status
                break

        if matched_status is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Invalid status. Allowed values are: "
                    "Draft, Under Review, Approved, Rejected, Archived"
                )
            )

        decision_status = matched_status

    # --------------------------------------------------------
    # Get teams
    # --------------------------------------------------------
    team_query = db.query(Team)

    if team_id is not None:
        team_query = team_query.filter(
            Team.id == team_id
        )

    if team:
        team_query = team_query.filter(
            Team.name.ilike(f"%{team}%")
        )

    teams = (
        team_query
        .order_by(Team.name.asc())
        .all()
    )

    # --------------------------------------------------------
    # Build report rows
    # --------------------------------------------------------
    report_rows = []

    for team_obj in teams:

        # Count team members
        member_count = (
            db.query(User)
            .filter(User.team_id == team_obj.id)
            .count()
        )

        # ----------------------------------------------------
        # Get decisions created by team members
        # ----------------------------------------------------
        decision_query = (
            db.query(Decision)
            .join(
                User,
                Decision.created_by == User.id
            )
            .filter(
                User.team_id == team_obj.id
            )
        )

        if decision_status:
            decision_query = decision_query.filter(
                Decision.status == decision_status
            )

        if category:
            decision_query = decision_query.filter(
                Decision.category == category
            )

        if start_date:
            start_datetime = datetime.combine(
                start_date,
                time.min
            )

            decision_query = decision_query.filter(
                Decision.created_at >= start_datetime
            )

        if end_date:
            end_datetime = datetime.combine(
                end_date + timedelta(days=1),
                time.min
            )

            decision_query = decision_query.filter(
                Decision.created_at < end_datetime
            )

        decisions = decision_query.all()

        # ----------------------------------------------------
        # Decision statistics
        # ----------------------------------------------------
        total_decisions = len(decisions)

        approved_decisions = sum(
            1
            for decision_item in decisions
            if decision_item.status == "Approved"
        )

        rejected_decisions = sum(
            1
            for decision_item in decisions
            if decision_item.status == "Rejected"
        )

        pending_decisions = sum(
            1
            for decision_item in decisions
            if decision_item.status in {
                "Draft",
                "Under Review"
            }
        )

        # ----------------------------------------------------
        # Approval statistics
        # ----------------------------------------------------
        decision_ids = [
            decision_item.id
            for decision_item in decisions
        ]

        if decision_ids:
            approvals = (
                db.query(Approval)
                .filter(
                    Approval.decision_id.in_(decision_ids)
                )
                .all()
            )
        else:
            approvals = []

        total_approvals = len(approvals)

        approved_approvals = sum(
            1
            for approval_item in approvals
            if approval_item.status == "Approved"
        )

        rejected_approvals = sum(
            1
            for approval_item in approvals
            if approval_item.status == "Rejected"
        )

        pending_approvals = sum(
            1
            for approval_item in approvals
            if approval_item.status == "Pending"
        )

        completed_approvals = (
            approved_approvals +
            rejected_approvals
        )

        approval_completion_rate = (
            (completed_approvals / total_approvals) * 100
            if total_approvals > 0
            else 0
        )

        report_rows.append({
            "team_name": team_obj.name,
            "member_count": member_count,
            "total_decisions": total_decisions,
            "approved_decisions": approved_decisions,
            "rejected_decisions": rejected_decisions,
            "pending_decisions": pending_decisions,
            "total_approvals": total_approvals,
            "approved_approvals": approved_approvals,
            "rejected_approvals": rejected_approvals,
            "pending_approvals": pending_approvals,
            "approval_completion_rate":
                approval_completion_rate
        })

    # --------------------------------------------------------
    # Create Excel workbook
    # --------------------------------------------------------
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment
    from openpyxl.utils import get_column_letter

    workbook = Workbook()

    worksheet = workbook.active
    worksheet.title = "Team Report"

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------
    worksheet["A1"] = "Team Report"
    worksheet["A1"].font = Font(
        bold=True,
        size=16
    )

    worksheet["A2"] = "Generated At"
    worksheet["B2"] = datetime.utcnow()

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------
    total_teams = len(report_rows)

    total_members = sum(
        row["member_count"]
        for row in report_rows
    )

    total_decisions = sum(
        row["total_decisions"]
        for row in report_rows
    )

    total_approved = sum(
        row["approved_decisions"]
        for row in report_rows
    )

    total_rejected = sum(
        row["rejected_decisions"]
        for row in report_rows
    )

    total_pending = sum(
        row["pending_decisions"]
        for row in report_rows
    )

    worksheet["A4"] = "Summary"
    worksheet["A4"].font = Font(bold=True)

    summary_headers = [
        "Total Teams",
        "Total Members",
        "Total Decisions",
        "Approved",
        "Rejected",
        "Pending"
    ]

    summary_values = [
        total_teams,
        total_members,
        total_decisions,
        total_approved,
        total_rejected,
        total_pending
    ]

    for column_index, value in enumerate(
        summary_headers,
        start=1
    ):
        cell = worksheet.cell(
            row=5,
            column=column_index
        )
        cell.value = value
        cell.font = Font(bold=True)
        cell.alignment = Alignment(
            horizontal="center"
        )

    for column_index, value in enumerate(
        summary_values,
        start=1
    ):
        worksheet.cell(
            row=6,
            column=column_index
        ).value = value

    # --------------------------------------------------------
    # Detailed report
    # --------------------------------------------------------
    headers = [
        "Team Name",
        "Member Count",
        "Total Decisions",
        "Approved Decisions",
        "Rejected Decisions",
        "Pending Decisions",
        "Total Approvals",
        "Approved Approvals",
        "Rejected Approvals",
        "Pending Approvals",
        "Approval Completion Rate"
    ]

    header_row = 8

    for column_index, header in enumerate(
        headers,
        start=1
    ):
        cell = worksheet.cell(
            row=header_row,
            column=column_index
        )

        cell.value = header
        cell.font = Font(bold=True)
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True
        )

    # --------------------------------------------------------
    # Add data
    # --------------------------------------------------------
    for row_index, row in enumerate(
        report_rows,
        start=header_row + 1
    ):
        values = [
            row["team_name"],
            row["member_count"],
            row["total_decisions"],
            row["approved_decisions"],
            row["rejected_decisions"],
            row["pending_decisions"],
            row["total_approvals"],
            row["approved_approvals"],
            row["rejected_approvals"],
            row["pending_approvals"],
            row["approval_completion_rate"] / 100
        ]

        for column_index, value in enumerate(
            values,
            start=1
        ):
            cell = worksheet.cell(
                row=row_index,
                column=column_index
            )

            cell.value = value
            cell.alignment = Alignment(
                vertical="top"
            )

            # Format completion rate as percentage
            if column_index == 11:
                cell.number_format = "0.00%"

    # --------------------------------------------------------
    # Freeze header
    # --------------------------------------------------------
    worksheet.freeze_panes = "A9"

    # --------------------------------------------------------
    # Auto-adjust column widths
    # --------------------------------------------------------
    for column_cells in worksheet.columns:

        max_length = 0

        column_letter = get_column_letter(
            column_cells[0].column
        )

        for cell in column_cells:
            try:
                cell_length = len(str(cell.value))

                if cell_length > max_length:
                    max_length = cell_length

            except Exception:
                pass

        worksheet.column_dimensions[
            column_letter
        ].width = min(
            max_length + 2,
            35
        )

    # --------------------------------------------------------
    # Save Excel file to memory
    # --------------------------------------------------------
    excel_buffer = BytesIO()

    workbook.save(excel_buffer)

    excel_buffer.seek(0)

    # --------------------------------------------------------
    # Return Excel file
    # --------------------------------------------------------
    return StreamingResponse(
        excel_buffer,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=team_report.xlsx"
        }
    )
# ============================================================
# AUDIT REPORT EXCEL EXPORT
# GET /reports/audit/excel
# ============================================================

@router.get("/audit/excel")
def export_audit_report_excel(
    user_id: Optional[int] = Query(
        None,
        description="Filter audit logs by user ID"
    ),
    action: Optional[str] = Query(
        None,
        description="Filter audit logs by action"
    ),
    entity_type: Optional[str] = Query(
        None,
        description="Filter audit logs by entity type"
    ),
    entity_id: Optional[int] = Query(
        None,
        description="Filter audit logs by entity ID"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Filter audit logs from this date"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Filter audit logs up to this date"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # --------------------------------------------------------
    # Admin authorization
    # --------------------------------------------------------
    if current_user.role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # --------------------------------------------------------
    # Validate dates
    # --------------------------------------------------------
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )

    # --------------------------------------------------------
    # Build audit log query
    # --------------------------------------------------------
    query = (
        db.query(AuditLog)
        .outerjoin(
            User,
            AuditLog.user_id == User.id
        )
    )

    # --------------------------------------------------------
    # Apply filters
    # --------------------------------------------------------
    if user_id is not None:
        query = query.filter(
            AuditLog.user_id == user_id
        )

    if action:
        query = query.filter(
            AuditLog.action == action
        )

    if entity_type:
        query = query.filter(
            AuditLog.entity_type == entity_type
        )

    if entity_id is not None:
        query = query.filter(
            AuditLog.entity_id == entity_id
        )

    if start_date:
        start_datetime = datetime.combine(
            start_date,
            time.min
        )

        query = query.filter(
            AuditLog.created_at >= start_datetime
        )

    if end_date:
        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min
        )

        query = query.filter(
            AuditLog.created_at < end_datetime
        )

    # --------------------------------------------------------
    # Get audit logs
    # --------------------------------------------------------
    audit_logs = (
        query
        .order_by(AuditLog.created_at.desc())
        .all()
    )

    # --------------------------------------------------------
    # Create Excel workbook
    # --------------------------------------------------------
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment
    from openpyxl.utils import get_column_letter

    workbook = Workbook()

    worksheet = workbook.active
    worksheet.title = "Audit Report"

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------
    worksheet["A1"] = "Audit Report"
    worksheet["A1"].font = Font(
        bold=True,
        size=16
    )

    worksheet["A2"] = "Generated At"
    worksheet["B2"] = datetime.utcnow()

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------
    worksheet["A4"] = "Summary"
    worksheet["A4"].font = Font(bold=True)

    worksheet["A5"] = "Total Audit Logs"
    worksheet["B5"] = len(audit_logs)

    # --------------------------------------------------------
    # Header row
    # --------------------------------------------------------
    headers = [
        "Audit Log ID",
        "User",
        "User Email",
        "Action",
        "Entity Type",
        "Entity ID",
        "Description",
        "IP Address",
        "Request Method",
        "Endpoint",
        "Created Date"
    ]

    header_row = 7

    for column_index, header in enumerate(
        headers,
        start=1
    ):
        cell = worksheet.cell(
            row=header_row,
            column=column_index
        )

        cell.value = header
        cell.font = Font(bold=True)
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True
        )

    # --------------------------------------------------------
    # Add audit log rows
    # --------------------------------------------------------
    for row_index, audit_log in enumerate(
        audit_logs,
        start=header_row + 1
    ):
        audit_user = (
            db.query(User)
            .filter(User.id == audit_log.user_id)
            .first()
            if audit_log.user_id is not None
            else None
        )

        user_name = "Unknown"
        user_email = ""

        if audit_user:
            user_name = (
                audit_user.full_name
                or audit_user.email
                or "Unknown"
            )

            user_email = audit_user.email or ""

        values = [
            audit_log.id,
            user_name,
            user_email,
            audit_log.action,
            audit_log.entity_type,
            audit_log.entity_id,
            audit_log.description,
            audit_log.ip_address or "",
            audit_log.request_method or "",
            audit_log.endpoint or "",
            audit_log.created_at
        ]

        for column_index, value in enumerate(
            values,
            start=1
        ):
            cell = worksheet.cell(
                row=row_index,
                column=column_index
            )

            cell.value = value

            cell.alignment = Alignment(
                vertical="top",
                wrap_text=True
            )

    # --------------------------------------------------------
    # Freeze header
    # --------------------------------------------------------
    worksheet.freeze_panes = "A8"

    # --------------------------------------------------------
    # Auto-adjust column widths
    # --------------------------------------------------------
    for column_cells in worksheet.columns:

        max_length = 0

        column_letter = get_column_letter(
            column_cells[0].column
        )

        for cell in column_cells:
            try:
                cell_length = len(str(cell.value))

                if cell_length > max_length:
                    max_length = cell_length

            except Exception:
                pass

        worksheet.column_dimensions[
            column_letter
        ].width = min(
            max_length + 2,
            40
        )

    # --------------------------------------------------------
    # Save workbook to memory
    # --------------------------------------------------------
    excel_buffer = BytesIO()

    workbook.save(excel_buffer)

    excel_buffer.seek(0)

    # --------------------------------------------------------
    # Return Excel file
    # --------------------------------------------------------
    return StreamingResponse(
        excel_buffer,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=audit_report.xlsx"
        }
    )
# ============================================================
# AUDIT REPORT PDF EXPORT
# GET /reports/audit/pdf
# ============================================================

@router.get("/audit/pdf")
def export_audit_report_pdf(
    user_id: Optional[int] = Query(
        None,
        description="Filter audit logs by user ID"
    ),
    action: Optional[str] = Query(
        None,
        description="Filter audit logs by action"
    ),
    entity_type: Optional[str] = Query(
        None,
        description="Filter audit logs by entity type"
    ),
    entity_id: Optional[int] = Query(
        None,
        description="Filter audit logs by entity ID"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Filter audit logs from this date"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Filter audit logs up to this date"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # --------------------------------------------------------
    # Admin authorization
    # --------------------------------------------------------
    if current_user.role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # --------------------------------------------------------
    # Validate dates
    # --------------------------------------------------------
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )

    # --------------------------------------------------------
    # Build query
    # --------------------------------------------------------
    query = (
        db.query(AuditLog)
        .outerjoin(
            User,
            AuditLog.user_id == User.id
        )
    )

    # --------------------------------------------------------
    # Apply filters
    # --------------------------------------------------------
    if user_id is not None:
        query = query.filter(
            AuditLog.user_id == user_id
        )

    if action:
        query = query.filter(
            AuditLog.action == action
        )

    if entity_type:
        query = query.filter(
            AuditLog.entity_type == entity_type
        )

    if entity_id is not None:
        query = query.filter(
            AuditLog.entity_id == entity_id
        )

    if start_date:
        start_datetime = datetime.combine(
            start_date,
            time.min
        )

        query = query.filter(
            AuditLog.created_at >= start_datetime
        )

    if end_date:
        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min
        )

        query = query.filter(
            AuditLog.created_at < end_datetime
        )

    # --------------------------------------------------------
    # Get audit logs
    # --------------------------------------------------------
    audit_logs = (
        query
        .order_by(AuditLog.created_at.desc())
        .all()
    )

    # --------------------------------------------------------
    # Create PDF
    # --------------------------------------------------------
    pdf_buffer = BytesIO()

    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=landscape(A4),
        rightMargin=20,
        leftMargin=20,
        topMargin=25,
        bottomMargin=25
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(
        Paragraph(
            "Audit Report",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            f"Generated at: {datetime.utcnow()}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 12))

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------
    summary_data = [
        ["Total Audit Logs"],
        [str(len(audit_logs))]
    ]

    summary_table = Table(
        summary_data,
        repeatRows=1
    )

    summary_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, 0),
                8
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, 0),
                8
            )
        ])
    )

    elements.append(summary_table)
    elements.append(Spacer(1, 15))

    # --------------------------------------------------------
    # Detailed table
    # --------------------------------------------------------
    table_data = [[
        "Audit ID",
        "User",
        "Email",
        "Action",
        "Entity Type",
        "Entity ID",
        "Description",
        "IP Address",
        "Method",
        "Endpoint",
        "Created Date"
    ]]

    for audit_log in audit_logs:

        audit_user = (
            db.query(User)
            .filter(User.id == audit_log.user_id)
            .first()
            if audit_log.user_id is not None
            else None
        )

        user_name = "Unknown"
        user_email = ""

        if audit_user:
            user_name = (
                audit_user.full_name
                or audit_user.email
                or "Unknown"
            )

            user_email = audit_user.email or ""

        table_data.append([
            str(audit_log.id),
            user_name,
            user_email,
            audit_log.action,
            audit_log.entity_type,
            str(audit_log.entity_id)
            if audit_log.entity_id is not None
            else "",
            audit_log.description,
            audit_log.ip_address or "",
            audit_log.request_method or "",
            audit_log.endpoint or "",
            str(audit_log.created_at)
        ])

    # --------------------------------------------------------
    # PDF table
    # --------------------------------------------------------
    audit_table = Table(
        table_data,
        repeatRows=1,
        colWidths=[
            45,
            70,
            90,
            55,
            65,
            50,
            150,
            70,
            45,
            100,
            90
        ]
    )

    audit_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.black
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                6
            ),
            (
                "ALIGN",
                (0, 0),
                (0, -1),
                "CENTER"
            )
        ])
    )

    elements.append(audit_table)

    # --------------------------------------------------------
    # Build PDF
    # --------------------------------------------------------
    document.build(elements)

    pdf_buffer.seek(0)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=audit_report.pdf"
        }
    )
# ============================================================
# APPROVAL REPORT EXCEL EXPORT
# GET /reports/approvals/excel
# ============================================================

@router.get("/approvals/excel")
def export_approval_report_excel(
    approval_status: Optional[str] = Query(
        None,
        alias="status",
        description="Filter approvals by status"
    ),
    reviewer: Optional[int] = Query(
        None,
        description="Filter approvals by reviewer user ID"
    ),
    decision: Optional[int] = Query(
        None,
        description="Filter approvals by decision ID"
    ),
    approval_level: Optional[int] = Query(
        None,
        description="Filter approvals by approval level"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Filter approvals assigned from this date"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Filter approvals assigned up to this date"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # --------------------------------------------------------
    # Validate dates
    # --------------------------------------------------------
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )

    # --------------------------------------------------------
    # Validate approval status
    # --------------------------------------------------------
    allowed_statuses = {
        "Pending",
        "Approved",
        "Rejected"
    }

    if approval_status:
        matched_status = None

        for allowed_status in allowed_statuses:
            if allowed_status.lower() == approval_status.lower():
                matched_status = allowed_status
                break

        if matched_status is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Invalid approval status. Allowed values are: "
                    "Pending, Approved, Rejected"
                )
            )

        approval_status = matched_status

    # --------------------------------------------------------
    # Validate approval level
    # --------------------------------------------------------
    if approval_level is not None and approval_level < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="approval_level must be greater than or equal to 1"
        )

    # --------------------------------------------------------
    # Build approval query
    # --------------------------------------------------------
    query = (
        db.query(Approval)
        .join(
            Decision,
            Approval.decision_id == Decision.id
        )
        .options(
            joinedload(Approval.decision),
            joinedload(Approval.reviewer)
        )
    )

    # --------------------------------------------------------
    # Apply filters
    # --------------------------------------------------------
    if approval_status:
        query = query.filter(
            Approval.status == approval_status
        )

    if reviewer is not None:
        query = query.filter(
            Approval.reviewer_id == reviewer
        )

    if decision is not None:
        query = query.filter(
            Approval.decision_id == decision
        )

    if approval_level is not None:
        query = query.filter(
            Approval.approval_level == approval_level
        )

    if start_date:
        start_datetime = datetime.combine(
            start_date,
            time.min
        )

        query = query.filter(
            Approval.created_at >= start_datetime
        )

    if end_date:
        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min
        )

        query = query.filter(
            Approval.created_at < end_datetime
        )

    # --------------------------------------------------------
    # Get approvals
    # --------------------------------------------------------
    approvals = (
        query
        .order_by(Approval.created_at.desc())
        .all()
    )

    # --------------------------------------------------------
    # Calculate summary
    # --------------------------------------------------------
    total_approvals = len(approvals)

    pending_count = sum(
        1
        for approval_item in approvals
        if approval_item.status == "Pending"
    )

    approved_count = sum(
        1
        for approval_item in approvals
        if approval_item.status == "Approved"
    )

    rejected_count = sum(
        1
        for approval_item in approvals
        if approval_item.status == "Rejected"
    )

    completed_count = (
        approved_count +
        rejected_count
    )

    completion_rate = (
        (completed_count / total_approvals) * 100
        if total_approvals > 0
        else 0
    )

    turnaround_values = []

    for approval_item in approvals:
        if (
            approval_item.created_at
            and approval_item.completed_at
        ):
            duration = (
                approval_item.completed_at
                - approval_item.created_at
            )

            turnaround_values.append(
                duration.total_seconds() / 3600
            )

    average_turnaround = (
        sum(turnaround_values)
        / len(turnaround_values)
        if turnaround_values
        else 0
    )

    # --------------------------------------------------------
    # Import Excel libraries
    # --------------------------------------------------------
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment
    from openpyxl.utils import get_column_letter

    # --------------------------------------------------------
    # Create workbook
    # --------------------------------------------------------
    workbook = Workbook()

    worksheet = workbook.active
    worksheet.title = "Approval Report"

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------
    worksheet["A1"] = "Approval Report"
    worksheet["A1"].font = Font(
        bold=True,
        size=16
    )

    worksheet["A2"] = "Generated At"
    worksheet["B2"] = datetime.utcnow()

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------
    worksheet["A4"] = "Summary"
    worksheet["A4"].font = Font(bold=True)

    summary_headers = [
        "Total",
        "Pending",
        "Approved",
        "Rejected",
        "Completion Rate",
        "Average Turnaround (Hours)"
    ]

    summary_values = [
        total_approvals,
        pending_count,
        approved_count,
        rejected_count,
        completion_rate / 100,
        average_turnaround
    ]

    for column_index, header in enumerate(
        summary_headers,
        start=1
    ):
        cell = worksheet.cell(
            row=5,
            column=column_index
        )

        cell.value = header
        cell.font = Font(bold=True)
        cell.alignment = Alignment(
            horizontal="center"
        )

    for column_index, value in enumerate(
        summary_values,
        start=1
    ):
        cell = worksheet.cell(
            row=6,
            column=column_index
        )

        cell.value = value

        if column_index == 5:
            cell.number_format = "0.00%"

        if column_index == 6:
            cell.number_format = "0.00"

    # --------------------------------------------------------
    # Detailed report headers
    # --------------------------------------------------------
    headers = [
        "Approval ID",
        "Decision ID",
        "Decision Title",
        "Reviewer",
        "Reviewer Email",
        "Approval Level",
        "Status",
        "Assigned Date",
        "Completed Date",
        "Turnaround (Hours)"
    ]

    header_row = 8

    for column_index, header in enumerate(
        headers,
        start=1
    ):
        cell = worksheet.cell(
            row=header_row,
            column=column_index
        )

        cell.value = header
        cell.font = Font(bold=True)
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True
        )

    # --------------------------------------------------------
    # Add approval rows
    # --------------------------------------------------------
    for row_index, approval_item in enumerate(
        approvals,
        start=header_row + 1
    ):
        reviewer_name = "Unknown"
        reviewer_email = ""

        if approval_item.reviewer:
            reviewer_name = (
                approval_item.reviewer.full_name
                or approval_item.reviewer.email
                or "Unknown"
            )

            reviewer_email = (
                approval_item.reviewer.email
                or ""
            )

        turnaround_hours = None

        if (
            approval_item.created_at
            and approval_item.completed_at
        ):
            duration = (
                approval_item.completed_at
                - approval_item.created_at
            )

            turnaround_hours = (
                duration.total_seconds() / 3600
            )

        values = [
            approval_item.id,
            approval_item.decision_id,
            (
                approval_item.decision.title
                if approval_item.decision
                else "Unknown"
            ),
            reviewer_name,
            reviewer_email,
            approval_item.approval_level,
            approval_item.status,
            approval_item.created_at,
            approval_item.completed_at,
            turnaround_hours
        ]

        for column_index, value in enumerate(
            values,
            start=1
        ):
            cell = worksheet.cell(
                row=row_index,
                column=column_index
            )

            cell.value = value

            cell.alignment = Alignment(
                vertical="top",
                wrap_text=True
            )

            if column_index == 10 and value is not None:
                cell.number_format = "0.00"

    # --------------------------------------------------------
    # Freeze header
    # --------------------------------------------------------
    worksheet.freeze_panes = "A9"

    # --------------------------------------------------------
    # Auto-adjust column widths
    # --------------------------------------------------------
    for column_cells in worksheet.columns:

        max_length = 0

        column_letter = get_column_letter(
            column_cells[0].column
        )

        for cell in column_cells:
            try:
                cell_length = len(str(cell.value))

                if cell_length > max_length:
                    max_length = cell_length

            except Exception:
                pass

        worksheet.column_dimensions[
            column_letter
        ].width = min(
            max_length + 2,
            40
        )

    # --------------------------------------------------------
    # Save workbook to memory
    # --------------------------------------------------------
    excel_buffer = BytesIO()

    workbook.save(excel_buffer)

    excel_buffer.seek(0)

    # --------------------------------------------------------
    # Return Excel file
    # --------------------------------------------------------
    return StreamingResponse(
        excel_buffer,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=approval_report.xlsx"
        }
    )