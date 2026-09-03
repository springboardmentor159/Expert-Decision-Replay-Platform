"""
Sprint 12: Reports and Export Module.

Centralized, read-only reporting on top of data already produced by
earlier sprints (Decisions, Approvals, Users/Teams, Audit & Compliance).
Nothing here writes to the database - it only queries and, optionally,
renders the result as PDF or Excel.

Reuses the existing JWT auth (app.utils.security.get_current_user /
require_role) - no new authentication mechanism is introduced.
"""
from datetime import datetime, date, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload, selectinload

from app.db.database import get_db
from app.models.decision import Decision
from app.models.approval import Approval
from app.models.alternative import Alternative
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.tag import Tag
from app.schemas.decision import DecisionStatus
from app.schemas.audit import AuditAction, EntityType
from app.schemas.report import (
    DecisionReportItem,
    DecisionReportSummary,
    DecisionReportResponse,
    ApprovalReportItem,
    ApprovalReportSummary,
    ApprovalReportResponse,
    TeamApprovalStats,
    TeamReportItem,
    TeamReportResponse,
    AuditReportItem,
    AuditReportResponse,
)
from app.utils.security import get_current_user, require_role
from app.utils.report_export import build_pdf_report, build_excel_report


router = APIRouter(prefix="/reports", tags=["Reports & Export"])


# =======================================================================
# Shared helpers
# =======================================================================

def _validate_date_range(start_date: Optional[date], end_date: Optional[date]) -> None:
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date must not be after end_date",
        )


def _end_of_day_bound(end_date: date):
    """end_date is inclusive - convert to an exclusive upper bound."""
    return end_date + timedelta(days=1)


def _validate_sort(sort: str, order: str, allowed: dict) -> None:
    if sort not in allowed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid sort field. Allowed values: {', '.join(allowed)}",
        )
    if order not in ("asc", "desc"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid order. Allowed values: asc, desc",
        )


def _apply_sort(query, sort: str, order: str, allowed: dict):
    column = allowed[sort]
    return query.order_by(column.asc() if order == "asc" else column.desc())


def _paginate_query(query, page: int, page_size: int):
    total = query.distinct().count()
    items = query.distinct().offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def _dept_user_ids_subquery(db: Session, department: str):
    return db.query(User.id).filter(User.department == department).subquery()


def _stream_bytes(buffer, media_type: str, filename: str) -> StreamingResponse:
    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


PDF_MEDIA_TYPE = "application/pdf"
EXCEL_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


# =======================================================================
# 1. DECISION REPORTS
# =======================================================================

DECISION_SORT_FIELDS = {
    "created_date": Decision.created_at,
    "updated_date": Decision.updated_at,
    "title": Decision.title,
}


def _decision_scope_filters(current_user: User, db: Session) -> list:
    """
    Role-based visibility for the decision report:
      - Administrator: everything
      - Manager: decisions created by anyone in their department
      - Reviewer: decisions they created, or that they are/were a reviewer on
      - Employee: only decisions they created
    """
    role = current_user.role

    if role == "Administrator":
        return []

    if role == "Manager":
        dept_ids = _dept_user_ids_subquery(db, current_user.department)
        return [Decision.created_by.in_(dept_ids)]

    if role == "Reviewer":
        reviewed_decision_ids = (
            db.query(Approval.decision_id)
            .filter(Approval.reviewer_id == current_user.id)
            .subquery()
        )
        return [
            or_(
                Decision.created_by == current_user.id,
                Decision.id.in_(reviewed_decision_ids),
            )
        ]

    # Employee (default)
    return [Decision.created_by == current_user.id]


def _decision_report_filters(
    category: Optional[str],
    status_filter: Optional[DecisionStatus],
    created_by: Optional[int],
    start_date: Optional[date],
    end_date: Optional[date],
) -> list:
    filters = []

    if category is not None:
        filters.append(Decision.category == category)

    if status_filter is not None:
        filters.append(Decision.status == status_filter.value)

    if created_by is not None:
        filters.append(Decision.created_by == created_by)

    if start_date is not None:
        filters.append(Decision.created_at >= start_date)

    if end_date is not None:
        filters.append(Decision.created_at < _end_of_day_bound(end_date))

    return filters


def _decision_base_query(
    db: Session,
    current_user: User,
    category: Optional[str],
    status_filter: Optional[DecisionStatus],
    created_by: Optional[int],
    tag: Optional[str],
    start_date: Optional[date],
    end_date: Optional[date],
):
    filters = _decision_report_filters(category, status_filter, created_by, start_date, end_date)
    filters += _decision_scope_filters(current_user, db)

    query = db.query(Decision).filter(*filters)

    if tag is not None:
        query = query.join(Decision.tags).filter(Tag.name == tag)

    return query


def _decision_summary(query) -> DecisionReportSummary:
    counts = {s.value: 0 for s in DecisionStatus}

    rows = (
        query.with_entities(Decision.status, func.count(func.distinct(Decision.id)))
        .group_by(Decision.status)
        .all()
    )
    for status_value, count in rows:
        counts[status_value] = count

    return DecisionReportSummary(
        total_decisions=sum(counts.values()),
        draft_decisions=counts[DecisionStatus.DRAFT.value],
        under_review=counts[DecisionStatus.UNDER_REVIEW.value],
        approved_decisions=counts[DecisionStatus.APPROVED.value],
        rejected_decisions=counts[DecisionStatus.REJECTED.value],
        archived_decisions=counts[DecisionStatus.ARCHIVED.value],
    )


def _decision_items(db: Session, decisions: list[Decision]) -> list[DecisionReportItem]:
    ids = [d.id for d in decisions]

    alt_counts = dict(
        db.query(Alternative.decision_id, func.count(Alternative.id))
        .filter(Alternative.decision_id.in_(ids))
        .group_by(Alternative.decision_id)
        .all()
    ) if ids else {}

    appr_counts = dict(
        db.query(Approval.decision_id, func.count(Approval.id))
        .filter(Approval.decision_id.in_(ids))
        .group_by(Approval.decision_id)
        .all()
    ) if ids else {}

    items = []
    for d in decisions:
        items.append(
            DecisionReportItem(
                decision_id=d.id,
                title=d.title,
                category=d.category,
                status=d.status,
                created_by=d.created_by,
                created_by_name=d.creator.full_name if d.creator else None,
                created_at=d.created_at,
                updated_at=d.updated_at,
                alternatives_count=alt_counts.get(d.id, 0),
                approvals_count=appr_counts.get(d.id, 0),
                tags=[t.name for t in d.tags],
            )
        )
    return items


def _decision_report_dataset(
    db: Session,
    current_user: User,
    category: Optional[str],
    status_filter: Optional[DecisionStatus],
    created_by: Optional[int],
    tag: Optional[str],
    start_date: Optional[date],
    end_date: Optional[date],
    sort: str,
    order: str,
):
    base_query = _decision_base_query(
        db, current_user, category, status_filter, created_by, tag, start_date, end_date
    )
    summary = _decision_summary(base_query)

    query = base_query.options(joinedload(Decision.creator), selectinload(Decision.tags))
    query = _apply_sort(query, sort, order, DECISION_SORT_FIELDS)

    return query, summary


@router.get("/decisions", response_model=DecisionReportResponse)
def get_decision_report(
    category: Optional[str] = Query(default=None, description="Filter by decision category"),
    status_filter: Optional[DecisionStatus] = Query(default=None, alias="status"),
    created_by: Optional[int] = Query(default=None, description="Filter by creator user id"),
    tag: Optional[str] = Query(default=None, description="Filter by tag name"),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort: str = Query(default="created_date"),
    order: str = Query(default="desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _validate_date_range(start_date, end_date)
    _validate_sort(sort, order, DECISION_SORT_FIELDS)

    query, summary = _decision_report_dataset(
        db, current_user, category, status_filter, created_by, tag, start_date, end_date, sort, order
    )

    decisions, total = _paginate_query(query, page, page_size)
    items = _decision_items(db, decisions)

    return DecisionReportResponse(
        items=items,
        summary=summary,
        page=page,
        page_size=page_size,
        total=total,
        generated_at=datetime.utcnow(),
        filters_applied={
            "category": category,
            "status": status_filter.value if status_filter else None,
            "created_by": created_by,
            "tag": tag,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
        },
    )


_DECISION_COLUMNS = [
    "Decision ID", "Title", "Category", "Status", "Created By",
    "Created Date", "Updated Date", "Alternatives", "Approvals", "Tags",
]


def _decision_rows(items: list[DecisionReportItem]) -> list[list[Any]]:
    return [
        [
            i.decision_id,
            i.title,
            i.category,
            i.status,
            i.created_by_name or i.created_by,
            i.created_at.strftime("%Y-%m-%d %H:%M"),
            i.updated_at.strftime("%Y-%m-%d %H:%M"),
            i.alternatives_count,
            i.approvals_count,
            ", ".join(i.tags),
        ]
        for i in items
    ]


@router.get("/decisions/export/pdf")
def export_decision_report_pdf(
    category: Optional[str] = Query(default=None),
    status_filter: Optional[DecisionStatus] = Query(default=None, alias="status"),
    created_by: Optional[int] = Query(default=None),
    tag: Optional[str] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    sort: str = Query(default="created_date"),
    order: str = Query(default="desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _validate_date_range(start_date, end_date)
    _validate_sort(sort, order, DECISION_SORT_FIELDS)

    query, summary = _decision_report_dataset(
        db, current_user, category, status_filter, created_by, tag, start_date, end_date, sort, order
    )
    items = _decision_items(db, query.distinct().all())

    buffer = build_pdf_report(
        report_title="Decision Report",
        filters={
            "category": category,
            "status": status_filter.value if status_filter else None,
            "created_by": created_by,
            "tag": tag,
            "start_date": start_date,
            "end_date": end_date,
        },
        summary=summary.model_dump(),
        columns=_DECISION_COLUMNS,
        rows=_decision_rows(items),
    )
    return _stream_bytes(buffer, PDF_MEDIA_TYPE, "decision_report.pdf")


@router.get("/decisions/export/excel")
def export_decision_report_excel(
    category: Optional[str] = Query(default=None),
    status_filter: Optional[DecisionStatus] = Query(default=None, alias="status"),
    created_by: Optional[int] = Query(default=None),
    tag: Optional[str] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    sort: str = Query(default="created_date"),
    order: str = Query(default="desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _validate_date_range(start_date, end_date)
    _validate_sort(sort, order, DECISION_SORT_FIELDS)

    query, summary = _decision_report_dataset(
        db, current_user, category, status_filter, created_by, tag, start_date, end_date, sort, order
    )
    items = _decision_items(db, query.distinct().all())

    buffer = build_excel_report(
        report_title="Decision Report",
        filters={
            "category": category,
            "status": status_filter.value if status_filter else None,
            "created_by": created_by,
            "tag": tag,
            "start_date": start_date,
            "end_date": end_date,
        },
        summary=summary.model_dump(),
        columns=_DECISION_COLUMNS,
        rows=_decision_rows(items),
    )
    return _stream_bytes(buffer, EXCEL_MEDIA_TYPE, "decision_report.xlsx")


# =======================================================================
# 2. APPROVAL REPORTS
# =======================================================================

APPROVAL_SORT_FIELDS = {
    "assigned_date": Approval.created_at,
    "approval_date": Approval.completed_at,
}


def _approval_scope_filters(current_user: User, db: Session) -> list:
    """
    Role-based visibility for the approval report. Decision is always
    joined in the base query, so Decision.created_by is safe to filter on.
      - Administrator: everything
      - Manager: approvals on decisions created within their department
      - Reviewer: approvals assigned to them
      - Employee: approvals on decisions they created
    """
    role = current_user.role

    if role == "Administrator":
        return []

    if role == "Manager":
        dept_ids = _dept_user_ids_subquery(db, current_user.department)
        return [Decision.created_by.in_(dept_ids)]

    if role == "Reviewer":
        return [Approval.reviewer_id == current_user.id]

    return [Decision.created_by == current_user.id]


def _approval_report_filters(
    approval_status: Optional[str],
    reviewer_id: Optional[int],
    decision_id: Optional[int],
    approval_level: Optional[int],
    start_date: Optional[date],
    end_date: Optional[date],
) -> list:
    filters = []

    if approval_status is not None:
        filters.append(Approval.status == approval_status)

    if reviewer_id is not None:
        filters.append(Approval.reviewer_id == reviewer_id)

    if decision_id is not None:
        filters.append(Approval.decision_id == decision_id)

    if approval_level is not None:
        filters.append(Approval.level == approval_level)

    if start_date is not None:
        filters.append(Approval.created_at >= start_date)

    if end_date is not None:
        filters.append(Approval.created_at < _end_of_day_bound(end_date))

    return filters


def _approval_base_query(
    db: Session,
    current_user: User,
    approval_status,
    reviewer_id,
    decision_id,
    approval_level,
    start_date,
    end_date,
):
    filters = _approval_report_filters(
        approval_status, reviewer_id, decision_id, approval_level, start_date, end_date
    )
    filters += _approval_scope_filters(current_user, db)

    query = (
        db.query(Approval)
        .join(Decision, Approval.decision_id == Decision.id)
        .filter(*filters)
    )
    return query


def _approval_summary(query) -> ApprovalReportSummary:
    total = query.distinct().count()

    pending = query.filter(Approval.status == "Pending").distinct().count()
    approved = query.filter(Approval.status == "Approved").distinct().count()
    rejected = query.filter(Approval.status == "Rejected").distinct().count()

    turnaround_seconds = func.extract("epoch", Approval.completed_at - Approval.created_at)
    avg_seconds = (
        query.filter(Approval.completed_at.isnot(None))
        .with_entities(func.avg(turnaround_seconds))
        .scalar()
    )
    avg_hours = round(avg_seconds / 3600, 2) if avg_seconds is not None else None

    completed = approved + rejected
    completion_rate = round((completed / total) * 100, 2) if total > 0 else 0.0

    return ApprovalReportSummary(
        total_approvals=total,
        pending_approvals=pending,
        approved_approvals=approved,
        rejected_approvals=rejected,
        average_turnaround_hours=avg_hours,
        approval_completion_rate=completion_rate,
    )


def _approval_items(approvals: list[Approval]) -> list[ApprovalReportItem]:
    items = []
    for a in approvals:
        turnaround = None
        if a.completed_at is not None:
            turnaround = round((a.completed_at - a.created_at).total_seconds() / 3600, 2)

        items.append(
            ApprovalReportItem(
                approval_id=a.id,
                decision_id=a.decision_id,
                decision_title=a.decision.title if a.decision else "",
                reviewer_id=a.reviewer_id,
                reviewer_name=a.reviewer.full_name if a.reviewer else None,
                approval_level=a.level,
                approval_status=a.status,
                assigned_date=a.created_at,
                completed_date=a.completed_at,
                turnaround_hours=turnaround,
            )
        )
    return items


def _approval_report_dataset(
    db, current_user, approval_status, reviewer_id, decision_id, approval_level,
    start_date, end_date, sort, order
):
    base_query = _approval_base_query(
        db, current_user, approval_status, reviewer_id, decision_id, approval_level, start_date, end_date
    )
    summary = _approval_summary(base_query)

    query = base_query.options(joinedload(Approval.decision), joinedload(Approval.reviewer))
    query = _apply_sort(query, sort, order, APPROVAL_SORT_FIELDS)

    return query, summary


@router.get("/approvals", response_model=ApprovalReportResponse)
def get_approval_report(
    approval_status: Optional[str] = Query(
        default=None, alias="status", pattern="^(Pending|Approved|Rejected)$"
    ),
    reviewer_id: Optional[int] = Query(default=None),
    decision_id: Optional[int] = Query(default=None),
    approval_level: Optional[int] = Query(default=None, alias="level"),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort: str = Query(default="assigned_date"),
    order: str = Query(default="desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _validate_date_range(start_date, end_date)
    _validate_sort(sort, order, APPROVAL_SORT_FIELDS)

    query, summary = _approval_report_dataset(
        db, current_user, approval_status, reviewer_id, decision_id, approval_level,
        start_date, end_date, sort, order
    )

    approvals, total = _paginate_query(query, page, page_size)
    items = _approval_items(approvals)

    return ApprovalReportResponse(
        items=items,
        summary=summary,
        page=page,
        page_size=page_size,
        total=total,
        generated_at=datetime.utcnow(),
        filters_applied={
            "status": approval_status,
            "reviewer_id": reviewer_id,
            "decision_id": decision_id,
            "level": approval_level,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
        },
    )


_APPROVAL_COLUMNS = [
    "Approval ID", "Decision ID", "Decision Title", "Reviewer", "Level",
    "Status", "Assigned Date", "Completed Date", "Turnaround (hrs)",
]


def _approval_rows(items: list[ApprovalReportItem]) -> list[list[Any]]:
    return [
        [
            i.approval_id,
            i.decision_id,
            i.decision_title,
            i.reviewer_name or i.reviewer_id,
            i.approval_level,
            i.approval_status,
            i.assigned_date.strftime("%Y-%m-%d %H:%M"),
            i.completed_date.strftime("%Y-%m-%d %H:%M") if i.completed_date else "",
            i.turnaround_hours if i.turnaround_hours is not None else "",
        ]
        for i in items
    ]


@router.get("/approvals/export/pdf")
def export_approval_report_pdf(
    approval_status: Optional[str] = Query(default=None, alias="status", pattern="^(Pending|Approved|Rejected)$"),
    reviewer_id: Optional[int] = Query(default=None),
    decision_id: Optional[int] = Query(default=None),
    approval_level: Optional[int] = Query(default=None, alias="level"),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    sort: str = Query(default="assigned_date"),
    order: str = Query(default="desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _validate_date_range(start_date, end_date)
    _validate_sort(sort, order, APPROVAL_SORT_FIELDS)

    query, summary = _approval_report_dataset(
        db, current_user, approval_status, reviewer_id, decision_id, approval_level,
        start_date, end_date, sort, order
    )
    items = _approval_items(query.distinct().all())

    buffer = build_pdf_report(
        report_title="Approval Report",
        filters={
            "status": approval_status, "reviewer_id": reviewer_id,
            "decision_id": decision_id, "level": approval_level,
            "start_date": start_date, "end_date": end_date,
        },
        summary=summary.model_dump(),
        columns=_APPROVAL_COLUMNS,
        rows=_approval_rows(items),
    )
    return _stream_bytes(buffer, PDF_MEDIA_TYPE, "approval_report.pdf")


@router.get("/approvals/export/excel")
def export_approval_report_excel(
    approval_status: Optional[str] = Query(default=None, alias="status", pattern="^(Pending|Approved|Rejected)$"),
    reviewer_id: Optional[int] = Query(default=None),
    decision_id: Optional[int] = Query(default=None),
    approval_level: Optional[int] = Query(default=None, alias="level"),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    sort: str = Query(default="assigned_date"),
    order: str = Query(default="desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _validate_date_range(start_date, end_date)
    _validate_sort(sort, order, APPROVAL_SORT_FIELDS)

    query, summary = _approval_report_dataset(
        db, current_user, approval_status, reviewer_id, decision_id, approval_level,
        start_date, end_date, sort, order
    )
    items = _approval_items(query.distinct().all())

    buffer = build_excel_report(
        report_title="Approval Report",
        filters={
            "status": approval_status, "reviewer_id": reviewer_id,
            "decision_id": decision_id, "level": approval_level,
            "start_date": start_date, "end_date": end_date,
        },
        summary=summary.model_dump(),
        columns=_APPROVAL_COLUMNS,
        rows=_approval_rows(items),
    )
    return _stream_bytes(buffer, EXCEL_MEDIA_TYPE, "approval_report.xlsx")


# =======================================================================
# 3. TEAM REPORTS
#
# NOTE: as in the dashboard module (Sprint 10), there is no dedicated
# team table in the schema - "team" means employees who share the same
# `department`. Only Manager (their own department) and Administrator
# (any/all departments) may view team reports.
# =======================================================================

def _team_stats(
    db: Session,
    department: str,
    status_filter: Optional[DecisionStatus],
    category: Optional[str],
    start_date: Optional[date],
    end_date: Optional[date],
) -> TeamReportItem:
    dept_ids = _dept_user_ids_subquery(db, department)

    member_count = db.query(func.count(User.id)).filter(User.department == department).scalar() or 0

    decision_filters = [Decision.created_by.in_(dept_ids)]
    if status_filter is not None:
        decision_filters.append(Decision.status == status_filter.value)
    if category is not None:
        decision_filters.append(Decision.category == category)
    if start_date is not None:
        decision_filters.append(Decision.created_at >= start_date)
    if end_date is not None:
        decision_filters.append(Decision.created_at < _end_of_day_bound(end_date))

    decision_query = db.query(Decision).filter(*decision_filters)
    total_decisions = decision_query.count()
    approved_decisions = decision_query.filter(Decision.status == DecisionStatus.APPROVED.value).count()
    rejected_decisions = decision_query.filter(Decision.status == DecisionStatus.REJECTED.value).count()
    pending_decisions = decision_query.filter(
        Decision.status.in_([DecisionStatus.DRAFT.value, DecisionStatus.UNDER_REVIEW.value])
    ).count()

    approval_query = (
        db.query(Approval)
        .join(Decision, Approval.decision_id == Decision.id)
        .filter(Decision.created_by.in_(dept_ids))
    )
    total_approvals = approval_query.count()
    approved_approvals = approval_query.filter(Approval.status == "Approved").count()
    rejected_approvals = approval_query.filter(Approval.status == "Rejected").count()
    pending_approvals = approval_query.filter(Approval.status == "Pending").count()
    completed = approved_approvals + rejected_approvals
    completion_rate = round((completed / total_approvals) * 100, 2) if total_approvals > 0 else 0.0

    return TeamReportItem(
        team_name=department,
        member_count=member_count,
        total_decisions=total_decisions,
        approved_decisions=approved_decisions,
        rejected_decisions=rejected_decisions,
        pending_decisions=pending_decisions,
        team_approval_stats=TeamApprovalStats(
            total_approvals=total_approvals,
            pending_approvals=pending_approvals,
            approved_approvals=approved_approvals,
            rejected_approvals=rejected_approvals,
            approval_completion_rate=completion_rate,
        ),
    )


def _resolve_visible_departments(
    db: Session, current_user: User, team: Optional[str]
) -> list[str]:
    if current_user.role == "Manager":
        if team is not None and team != current_user.department:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Managers may only view their own team's report",
            )
        return [current_user.department]

    # Administrator
    if team is not None:
        return [team]

    rows = db.query(User.department).distinct().order_by(User.department.asc()).all()
    return [r[0] for r in rows]


def _team_report_dataset(
    db: Session,
    current_user: User,
    team: Optional[str],
    status_filter: Optional[DecisionStatus],
    category: Optional[str],
    start_date: Optional[date],
    end_date: Optional[date],
) -> list[TeamReportItem]:
    departments = _resolve_visible_departments(db, current_user, team)
    return [
        _team_stats(db, dept, status_filter, category, start_date, end_date)
        for dept in departments
    ]


@router.get("/teams", response_model=TeamReportResponse)
def get_team_report(
    team: Optional[str] = Query(default=None, description="Filter by team/department name"),
    status_filter: Optional[DecisionStatus] = Query(default=None, alias="status"),
    category: Optional[str] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort: str = Query(default="team_name"),
    order: str = Query(default="asc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Manager", "Administrator")),
):
    _validate_date_range(start_date, end_date)
    if sort != "team_name" or order not in ("asc", "desc"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid sort field. Allowed values: team_name",
        )

    all_items = _team_report_dataset(db, current_user, team, status_filter, category, start_date, end_date)
    all_items.sort(key=lambda i: i.team_name, reverse=(order == "desc"))

    total = len(all_items)
    start_idx = (page - 1) * page_size
    page_items = all_items[start_idx:start_idx + page_size]

    return TeamReportResponse(
        items=page_items,
        page=page,
        page_size=page_size,
        total=total,
        generated_at=datetime.utcnow(),
        filters_applied={
            "team": team,
            "status": status_filter.value if status_filter else None,
            "category": category,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
        },
    )


_TEAM_COLUMNS = [
    "Team", "Members", "Total Decisions", "Approved", "Rejected", "Pending",
    "Total Approvals", "Approvals Approved", "Approvals Rejected",
    "Approvals Pending", "Approval Completion Rate (%)",
]


def _team_rows(items: list[TeamReportItem]) -> list[list[Any]]:
    return [
        [
            i.team_name,
            i.member_count,
            i.total_decisions,
            i.approved_decisions,
            i.rejected_decisions,
            i.pending_decisions,
            i.team_approval_stats.total_approvals,
            i.team_approval_stats.approved_approvals,
            i.team_approval_stats.rejected_approvals,
            i.team_approval_stats.pending_approvals,
            i.team_approval_stats.approval_completion_rate,
        ]
        for i in items
    ]


@router.get("/teams/export/pdf")
def export_team_report_pdf(
    team: Optional[str] = Query(default=None),
    status_filter: Optional[DecisionStatus] = Query(default=None, alias="status"),
    category: Optional[str] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Manager", "Administrator")),
):
    _validate_date_range(start_date, end_date)

    items = _team_report_dataset(db, current_user, team, status_filter, category, start_date, end_date)
    items.sort(key=lambda i: i.team_name)

    buffer = build_pdf_report(
        report_title="Team Report",
        filters={
            "team": team, "status": status_filter.value if status_filter else None,
            "category": category, "start_date": start_date, "end_date": end_date,
        },
        columns=_TEAM_COLUMNS,
        rows=_team_rows(items),
    )
    return _stream_bytes(buffer, PDF_MEDIA_TYPE, "team_report.pdf")


@router.get("/teams/export/excel")
def export_team_report_excel(
    team: Optional[str] = Query(default=None),
    status_filter: Optional[DecisionStatus] = Query(default=None, alias="status"),
    category: Optional[str] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Manager", "Administrator")),
):
    _validate_date_range(start_date, end_date)

    items = _team_report_dataset(db, current_user, team, status_filter, category, start_date, end_date)
    items.sort(key=lambda i: i.team_name)

    buffer = build_excel_report(
        report_title="Team Report",
        filters={
            "team": team, "status": status_filter.value if status_filter else None,
            "category": category, "start_date": start_date, "end_date": end_date,
        },
        columns=_TEAM_COLUMNS,
        rows=_team_rows(items),
    )
    return _stream_bytes(buffer, EXCEL_MEDIA_TYPE, "team_report.xlsx")


# =======================================================================
# 4. AUDIT REPORTS - Administrator only
# =======================================================================

AUDIT_SORT_FIELDS = {
    "created_date": AuditLog.created_at,
}


def _audit_report_filters(
    user_id: Optional[int],
    action: Optional[AuditAction],
    entity_type: Optional[EntityType],
    entity_id: Optional[int],
    start_date: Optional[date],
    end_date: Optional[date],
) -> list:
    filters = []

    if user_id is not None:
        filters.append(AuditLog.user_id == user_id)
    if action is not None:
        filters.append(AuditLog.action == action.value)
    if entity_type is not None:
        filters.append(AuditLog.entity_type == entity_type.value)
    if entity_id is not None:
        filters.append(AuditLog.entity_id == entity_id)
    if start_date is not None:
        filters.append(AuditLog.created_at >= start_date)
    if end_date is not None:
        filters.append(AuditLog.created_at < _end_of_day_bound(end_date))

    return filters


def _audit_report_dataset(db, user_id, action, entity_type, entity_id, start_date, end_date, sort, order):
    filters = _audit_report_filters(user_id, action, entity_type, entity_id, start_date, end_date)
    query = db.query(AuditLog).options(joinedload(AuditLog.user)).filter(*filters)
    query = _apply_sort(query, sort, order, AUDIT_SORT_FIELDS)
    return query


def _audit_items(logs: list[AuditLog]) -> list[AuditReportItem]:
    return [
        AuditReportItem(
            id=log.id,
            user_id=log.user_id,
            user_name=log.user.full_name if log.user else None,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            description=log.description,
            timestamp=log.created_at,
            ip_address=log.ip_address,
        )
        for log in logs
    ]


@router.get("/audit", response_model=AuditReportResponse)
def get_audit_report(
    user_id: Optional[int] = Query(default=None),
    action: Optional[AuditAction] = Query(default=None),
    entity_type: Optional[EntityType] = Query(default=None),
    entity_id: Optional[int] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort: str = Query(default="created_date"),
    order: str = Query(default="desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Administrator")),
):
    _validate_date_range(start_date, end_date)
    _validate_sort(sort, order, AUDIT_SORT_FIELDS)

    query = _audit_report_dataset(
        db, user_id, action, entity_type, entity_id, start_date, end_date, sort, order
    )
    logs, total = _paginate_query(query, page, page_size)
    items = _audit_items(logs)

    return AuditReportResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        generated_at=datetime.utcnow(),
        filters_applied={
            "user_id": user_id,
            "action": action.value if action else None,
            "entity_type": entity_type.value if entity_type else None,
            "entity_id": entity_id,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
        },
    )


_AUDIT_COLUMNS = [
    "ID", "User", "Action", "Entity Type", "Entity ID", "Description", "Timestamp", "IP Address",
]


def _audit_rows(items: list[AuditReportItem]) -> list[list[Any]]:
    return [
        [
            i.id,
            i.user_name or i.user_id,
            i.action,
            i.entity_type,
            i.entity_id,
            i.description,
            i.timestamp.strftime("%Y-%m-%d %H:%M"),
            i.ip_address or "",
        ]
        for i in items
    ]


@router.get("/audit/export/pdf")
def export_audit_report_pdf(
    user_id: Optional[int] = Query(default=None),
    action: Optional[AuditAction] = Query(default=None),
    entity_type: Optional[EntityType] = Query(default=None),
    entity_id: Optional[int] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    sort: str = Query(default="created_date"),
    order: str = Query(default="desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Administrator")),
):
    _validate_date_range(start_date, end_date)
    _validate_sort(sort, order, AUDIT_SORT_FIELDS)

    query = _audit_report_dataset(
        db, user_id, action, entity_type, entity_id, start_date, end_date, sort, order
    )
    items = _audit_items(query.all())

    buffer = build_pdf_report(
        report_title="Audit Report",
        filters={
            "user_id": user_id, "action": action.value if action else None,
            "entity_type": entity_type.value if entity_type else None,
            "entity_id": entity_id, "start_date": start_date, "end_date": end_date,
        },
        columns=_AUDIT_COLUMNS,
        rows=_audit_rows(items),
    )
    return _stream_bytes(buffer, PDF_MEDIA_TYPE, "audit_report.pdf")


@router.get("/audit/export/excel")
def export_audit_report_excel(
    user_id: Optional[int] = Query(default=None),
    action: Optional[AuditAction] = Query(default=None),
    entity_type: Optional[EntityType] = Query(default=None),
    entity_id: Optional[int] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    sort: str = Query(default="created_date"),
    order: str = Query(default="desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Administrator")),
):
    _validate_date_range(start_date, end_date)
    _validate_sort(sort, order, AUDIT_SORT_FIELDS)

    query = _audit_report_dataset(
        db, user_id, action, entity_type, entity_id, start_date, end_date, sort, order
    )
    items = _audit_items(query.all())

    buffer = build_excel_report(
        report_title="Audit Report",
        filters={
            "user_id": user_id, "action": action.value if action else None,
            "entity_type": entity_type.value if entity_type else None,
            "entity_id": entity_id, "start_date": start_date, "end_date": end_date,
        },
        columns=_AUDIT_COLUMNS,
        rows=_audit_rows(items),
    )
    return _stream_bytes(buffer, EXCEL_MEDIA_TYPE, "audit_report.xlsx")
