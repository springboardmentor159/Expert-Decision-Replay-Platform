import io
import math
from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.audit_log import AuditLog
from app.models.decision import Decision
from app.models.enums import (
    AuditAction,
    AuditEntityType,
    DecisionStatus,
    UserRole,
)
from app.models.user import User
from app.schemas.report import (
    ApprovalReportItem,
    ApprovalReportResponse,
    ApprovalReportSummary,
    AuditReportItem,
    AuditReportResponse,
    DecisionReportItem,
    DecisionReportResponse,
    DecisionReportSummary,
    TeamApprovalStats,
    TeamReportItem,
    TeamReportResponse,
)

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)

# ---------------------------------------------------------------------------
# Allowed sort columns per endpoint
# ---------------------------------------------------------------------------
_DECISION_SORT_MAP = {
    "created_date": Decision.created_at,
    "updated_date": Decision.updated_at,
    "title": Decision.title,
}

_APPROVAL_SORT_MAP = {
    "created_date": AuditLog.created_at,
    "approval_date": AuditLog.created_at,
}

_TEAM_SORT_MAP = {
    "team_name": User.department,
}

_AUDIT_SORT_MAP = {
    "created_date": AuditLog.created_at,
}

_VALID_DECISION_STATUSES = {s.value for s in DecisionStatus}
_VALID_AUDIT_ACTIONS = {a.value for a in AuditAction}
_VALID_AUDIT_ENTITY_TYPES = {e.value for e in AuditEntityType}


# ---------------------------------------------------------------------------
# Shared validators
# ---------------------------------------------------------------------------

def _parse_date(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        d = date.fromisoformat(value)
        return datetime(d.year, d.month, d.day)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid date format: '{value}'. Expected YYYY-MM-DD.",
        )


def _validate_date_range(start_date: datetime | None, end_date: datetime | None) -> None:
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date must not be after end_date.",
        )


def _validate_sort(sort_by: str | None, allowed: dict) -> None:
    if sort_by is not None and sort_by not in allowed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid sort field: '{sort_by}'. Allowed: {sorted(allowed.keys())}",
        )


def _paginate(total: int, page: int, page_size: int) -> int:
    return math.ceil(total / page_size) if total > 0 else 1


def _get_user_name(db: Session, user_id: int) -> str:
    user = db.query(User).filter(User.id == user_id).first()
    return user.full_name if user else f"User #{user_id}"


def _get_decision_title(db: Session, decision_id: int) -> str:
    d = db.query(Decision).filter(Decision.id == decision_id).first()
    return d.title if d else f"Decision #{decision_id}"


def _apply_sort(query, sort_by: str | None, sort_map: dict, sort_order: str, default_col):
    if sort_by and sort_by in sort_map:
        col = sort_map[sort_by]
        return query.order_by(col.desc() if sort_order == "desc" else col.asc())
    return query.order_by(default_col.desc() if sort_order == "desc" else default_col.asc())


# ---------------------------------------------------------------------------
# Reusable query builders — called by both JSON and export endpoints
# ---------------------------------------------------------------------------

def _build_decisions_query(
    db: Session,
    category: str | None,
    status_filter: DecisionStatus | None,
    creator: int | None,
    sd: datetime | None,
    ed: datetime | None,
):
    query = db.query(Decision)
    if category is not None:
        query = query.filter(Decision.category == category)
    if status_filter is not None:
        query = query.filter(Decision.status == status_filter.value)
    if creator is not None:
        query = query.filter(Decision.created_by == creator)
    if sd:
        query = query.filter(Decision.created_at >= sd)
    if ed:
        query = query.filter(Decision.created_at < ed + timedelta(days=1))
    return query


def _build_decision_items(db: Session, decisions) -> list[DecisionReportItem]:
    items = []
    for d in decisions:
        alt_count = len(d.alternatives)
        approval_count = (
            db.query(func.count(AuditLog.id))
            .filter(
                AuditLog.entity_type == "decision",
                AuditLog.entity_id == d.id,
                AuditLog.action == AuditAction.APPROVE.value,
            )
            .scalar()
        )
        creator_name = _get_user_name(db, d.created_by)
        items.append(
            DecisionReportItem(
                id=d.id,
                title=d.title,
                category=d.category,
                status=d.status.value if isinstance(d.status, DecisionStatus) else d.status,
                creator=creator_name,
                created_at=d.created_at,
                updated_at=d.updated_at,
                alternative_count=alt_count,
                approval_count=approval_count,
                tags=[],
            )
        )
    return items


def _build_decision_summary(db: Session) -> DecisionReportSummary:
    rows = (
        db.query(Decision.status, func.count(Decision.id))
        .group_by(Decision.status)
        .all()
    )
    counts = {s.value: 0 for s in DecisionStatus}
    for status_val, count in rows:
        key = status_val.value if isinstance(status_val, DecisionStatus) else str(status_val)
        if key in counts:
            counts[key] = count
    return DecisionReportSummary(
        total=sum(counts.values()),
        draft=counts[DecisionStatus.DRAFT.value],
        under_review=counts[DecisionStatus.UNDER_REVIEW.value],
        approved=counts[DecisionStatus.APPROVED.value],
        rejected=counts[DecisionStatus.REJECTED.value],
        archived=counts[DecisionStatus.ARCHIVED.value],
    )


def _build_approvals_query(
    db: Session,
    current_user: User,
    status_filter: str | None,
    reviewer: int | None,
    decision: int | None,
    sd: datetime | None,
    ed: datetime | None,
):
    query = db.query(AuditLog).filter(
        AuditLog.entity_type == AuditEntityType.DECISION.value,
        AuditLog.action.in_([AuditAction.APPROVE.value, AuditAction.REJECT.value]),
    )
    if current_user.role not in (UserRole.MANAGER, UserRole.ADMINISTRATOR):
        query = query.filter(AuditLog.user_id == current_user.id)
    elif reviewer is not None:
        query = query.filter(AuditLog.user_id == reviewer)
    if decision is not None:
        query = query.filter(AuditLog.entity_id == decision)
    if sd:
        query = query.filter(AuditLog.created_at >= sd)
    if ed:
        query = query.filter(AuditLog.created_at < ed + timedelta(days=1))
    if status_filter is not None:
        if status_filter.lower() == "approved":
            query = query.filter(AuditLog.action == AuditAction.APPROVE.value)
        elif status_filter.lower() == "rejected":
            query = query.filter(AuditLog.action == AuditAction.REJECT.value)
    return query


def _build_approval_items(db: Session, logs) -> list[ApprovalReportItem]:
    items = []
    for log in logs:
        reviewer_name = _get_user_name(db, log.user_id)
        decision_title = _get_decision_title(db, log.entity_id) if log.entity_id else "N/A"
        approval_status = "Approved" if log.action == AuditAction.APPROVE.value else "Rejected"
        items.append(
            ApprovalReportItem(
                id=log.id,
                decision_id=log.entity_id or 0,
                decision_title=decision_title,
                reviewer=reviewer_name,
                level=None,
                status=approval_status,
                assigned_date=None,
                completed_date=log.created_at,
                turnaround_time_hours=None,
            )
        )
    return items


def _build_approval_summary(db: Session) -> ApprovalReportSummary:
    all_approvals = (
        db.query(AuditLog)
        .filter(
            AuditLog.entity_type == AuditEntityType.DECISION.value,
            AuditLog.action.in_([AuditAction.APPROVE.value, AuditAction.REJECT.value]),
        )
        .all()
    )
    total = len(all_approvals)
    approved = sum(1 for a in all_approvals if a.action == AuditAction.APPROVE.value)
    rejected = sum(1 for a in all_approvals if a.action == AuditAction.REJECT.value)
    completion_rate = (approved + rejected) / total if total > 0 else 0.0
    return ApprovalReportSummary(
        total=total,
        pending=0,
        approved=approved,
        rejected=rejected,
        average_turnaround_hours=None,
        completion_rate=completion_rate,
    )


def _build_teams_data(
    db: Session,
    team: str | None,
    sd: datetime | None,
    ed: datetime | None,
    status_filter: DecisionStatus | None,
    category: str | None,
):
    dept_query = db.query(User.department).filter(User.department.isnot(None)).distinct()
    if team is not None:
        dept_query = dept_query.filter(User.department == team)
    departments = [row[0] for row in dept_query.all()]

    items = []
    for dept in departments:
        member_ids = [
            uid for (uid,) in db.query(User.id).filter(User.department == dept).all()
        ]
        dec_query = db.query(Decision).filter(Decision.created_by.in_(member_ids))
        if sd:
            dec_query = dec_query.filter(Decision.created_at >= sd)
        if ed:
            dec_query = dec_query.filter(Decision.created_at < ed + timedelta(days=1))
        if status_filter is not None:
            dec_query = dec_query.filter(Decision.status == status_filter.value)
        if category is not None:
            dec_query = dec_query.filter(Decision.category == category)

        decision_count = dec_query.count()
        decision_ids = [d.id for d in dec_query.all()]
        approved = rejected = pending = 0
        if decision_ids:
            approval_rows = (
                db.query(AuditLog.action, func.count(AuditLog.id))
                .filter(
                    AuditLog.entity_type == AuditEntityType.DECISION.value,
                    AuditLog.entity_id.in_(decision_ids),
                    AuditLog.action.in_([AuditAction.APPROVE.value, AuditAction.REJECT.value]),
                )
                .group_by(AuditLog.action)
                .all()
            )
            for action_val, count in approval_rows:
                if action_val == AuditAction.APPROVE.value:
                    approved = count
                elif action_val == AuditAction.REJECT.value:
                    rejected = count

        items.append(
            TeamReportItem(
                team=dept,
                member_count=len(member_ids),
                decision_count=decision_count,
                approval_stats=TeamApprovalStats(pending=pending, approved=approved, rejected=rejected),
            )
        )
    return items


def _build_audit_query(
    db: Session,
    current_user: User,
    user_filter: int | None,
    action: AuditAction | None,
    entity_type: AuditEntityType | None,
    entity_id: int | None,
    sd: datetime | None,
    ed: datetime | None,
):
    query = db.query(AuditLog)
    if current_user.role not in (UserRole.MANAGER, UserRole.ADMINISTRATOR):
        query = query.filter(AuditLog.user_id == current_user.id)
    elif user_filter is not None:
        query = query.filter(AuditLog.user_id == user_filter)
    if action is not None:
        query = query.filter(AuditLog.action == action.value)
    if entity_type is not None:
        query = query.filter(AuditLog.entity_type == entity_type.value)
    if entity_id is not None:
        query = query.filter(AuditLog.entity_id == entity_id)
    if sd:
        query = query.filter(AuditLog.created_at >= sd)
    if ed:
        query = query.filter(AuditLog.created_at < ed + timedelta(days=1))
    return query


def _build_audit_items(db: Session, logs) -> list[AuditReportItem]:
    items = []
    for log in logs:
        user_name = _get_user_name(db, log.user_id)
        items.append(
            AuditReportItem(
                id=log.id,
                user=user_name,
                action=log.action,
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                description=log.description,
                timestamp=log.created_at,
                ip_address=log.ip_address,
            )
        )
    return items


# ---------------------------------------------------------------------------
# Build active filter description for export headers
# ---------------------------------------------------------------------------

def _build_filter_description(**kwargs) -> str:
    parts = []
    for key, value in kwargs.items():
        if value is not None and value != "" and value != "desc":
            if key in ("start_date", "end_date"):
                parts.append(f"{key}: {value}")
            elif key == "status_filter":
                parts.append(f"status: {value}")
            else:
                parts.append(f"{key}: {value}")
    return ", ".join(parts) if parts else "None"


# ---------------------------------------------------------------------------
# PDF generation helpers
# ---------------------------------------------------------------------------

def _make_pdf(title: str, filter_desc: str, headers: list[str], rows: list[list[str]], summary_lines: list[str]):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(title, styles["Title"]))
    elements.append(Spacer(1, 6))

    # Date + filters
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    elements.append(Paragraph(f"Filters: {filter_desc}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Summary
    if summary_lines:
        summary_style = ParagraphStyle("Summary", parent=styles["Normal"], fontSize=10, leading=14)
        for line in summary_lines:
            elements.append(Paragraph(line, summary_style))
        elements.append(Spacer(1, 12))

    # Table
    if rows:
        table_data = [headers] + rows
        table = Table(table_data, repeatRows=1)
        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ])
        )
        elements.append(table)
    else:
        elements.append(Paragraph("No records found.", styles["Normal"]))

    doc.build(elements)
    buf.seek(0)
    return buf


# ---------------------------------------------------------------------------
# Excel generation helpers
# ---------------------------------------------------------------------------

_HEADER_FONT = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
_HEADER_FILL = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
_HEADER_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)
_CELL_ALIGN = Alignment(vertical="top", wrap_text=True)
_THIN_BORDER = Border(
    left=Side(style="thin", color="CCCCCC"),
    right=Side(style="thin", color="CCCCCC"),
    top=Side(style="thin", color="CCCCCC"),
    bottom=Side(style="thin", color="CCCCCC"),
)


def _make_excel(title: str, sheet_name: str, headers: list[str], rows: list[list], summary_rows: list[list] | None = None):
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    row_idx = 1

    # Title row
    ws.merge_cells(start_row=row_idx, start_column=1, end_row=row_idx, end_column=len(headers))
    title_cell = ws.cell(row=row_idx, column=1, value=title)
    title_cell.font = Font(name="Calibri", bold=True, size=14)
    row_idx += 1

    # Timestamp
    ws.merge_cells(start_row=row_idx, start_column=1, end_row=row_idx, end_column=len(headers))
    ws.cell(row=row_idx, column=1, value=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    row_idx += 2

    # Summary section
    if summary_rows:
        for label, value in summary_rows:
            ws.cell(row=row_idx, column=1, value=label).font = Font(bold=True)
            ws.cell(row=row_idx, column=2, value=value)
            row_idx += 1
        row_idx += 1

    # Header row
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=row_idx, column=col_idx, value=header)
        cell.font = _HEADER_FONT
        cell.fill = _HEADER_FILL
        cell.alignment = _HEADER_ALIGN
        cell.border = _THIN_BORDER
    row_idx += 1

    # Data rows
    for row_data in rows:
        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.alignment = _CELL_ALIGN
            cell.border = _THIN_BORDER
        row_idx += 1

    # Auto-width (approximate) — use get_column_letter to avoid merged cell issue
    for col_idx in range(1, len(headers) + 1):
        max_len = len(str(headers[col_idx - 1]))
        for data_row in rows:
            if col_idx - 1 < len(data_row):
                max_len = max(max_len, len(str(data_row[col_idx - 1])))
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = min(max_len + 4, 50)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


# ===========================================================================
# JSON endpoints (unchanged from Phase 1)
# ===========================================================================

@router.get("/decisions", response_model=DecisionReportResponse)
def report_decisions(
    category: Optional[str] = Query(None),
    status_filter: Optional[DecisionStatus] = Query(None, alias="status"),
    creator: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_order: Optional[str] = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sd = _parse_date(start_date)
    ed = _parse_date(end_date)
    _validate_date_range(sd, ed)
    _validate_sort(sort_by, _DECISION_SORT_MAP)
    if sort_order not in ("asc", "desc"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid sort_order: '{sort_order}'.")

    query = _build_decisions_query(db, category, status_filter, creator, sd, ed)
    total = query.count()
    query = _apply_sort(query, sort_by, _DECISION_SORT_MAP, sort_order, Decision.created_at)
    pages = _paginate(total, page, page_size)
    offset = (page - 1) * page_size
    decisions = query.offset(offset).limit(page_size).all()
    items = _build_decision_items(db, decisions)
    summary = _build_decision_summary(db)

    return DecisionReportResponse(items=items, summary=summary, total=total, page=page, page_size=page_size, pages=pages)


@router.get("/approvals", response_model=ApprovalReportResponse)
def report_approvals(
    status_filter: Optional[str] = Query(None, alias="status"),
    reviewer: Optional[int] = Query(None),
    decision: Optional[int] = Query(None),
    level: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_order: Optional[str] = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sd = _parse_date(start_date)
    ed = _parse_date(end_date)
    _validate_date_range(sd, ed)
    _validate_sort(sort_by, _APPROVAL_SORT_MAP)
    if sort_order not in ("asc", "desc"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid sort_order: '{sort_order}'.")
    if status_filter is not None and status_filter.lower() not in {"pending", "approved", "rejected"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid status: '{status_filter}'.")

    query = _build_approvals_query(db, current_user, status_filter, reviewer, decision, sd, ed)
    total = query.count()
    query = _apply_sort(query, sort_by, _APPROVAL_SORT_MAP, sort_order, AuditLog.created_at)
    pages = _paginate(total, page, page_size)
    offset = (page - 1) * page_size
    logs = query.offset(offset).limit(page_size).all()
    items = _build_approval_items(db, logs)
    summary = _build_approval_summary(db)

    return ApprovalReportResponse(items=items, summary=summary, total=total, page=page, page_size=page_size, pages=pages)


@router.get("/teams", response_model=TeamReportResponse)
def report_teams(
    team: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    status_filter: Optional[DecisionStatus] = Query(None, alias="status"),
    category: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_order: Optional[str] = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sd = _parse_date(start_date)
    ed = _parse_date(end_date)
    _validate_date_range(sd, ed)
    _validate_sort(sort_by, _TEAM_SORT_MAP)
    if sort_order not in ("asc", "desc"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid sort_order: '{sort_order}'.")

    items = _build_teams_data(db, team, sd, ed, status_filter, category)
    if sort_by == "team_name":
        items.sort(key=lambda x: x.team or "", reverse=(sort_order == "desc"))
    total = len(items)
    pages = _paginate(total, page, page_size)
    offset = (page - 1) * page_size
    paginated = items[offset : offset + page_size]

    return TeamReportResponse(items=paginated, total=total, page=page, page_size=page_size, pages=pages)


@router.get("/audit", response_model=AuditReportResponse)
def report_audit(
    user: Optional[int] = Query(None),
    action: Optional[AuditAction] = Query(None),
    entity_type: Optional[AuditEntityType] = Query(None),
    entity_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_order: Optional[str] = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sd = _parse_date(start_date)
    ed = _parse_date(end_date)
    _validate_date_range(sd, ed)
    _validate_sort(sort_by, _AUDIT_SORT_MAP)
    if sort_order not in ("asc", "desc"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid sort_order: '{sort_order}'.")

    query = _build_audit_query(db, current_user, user, action, entity_type, entity_id, sd, ed)
    total = query.count()
    query = _apply_sort(query, sort_by, _AUDIT_SORT_MAP, sort_order, AuditLog.created_at)
    pages = _paginate(total, page, page_size)
    offset = (page - 1) * page_size
    logs = query.offset(offset).limit(page_size).all()
    items = _build_audit_items(db, logs)

    return AuditReportResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)


# ===========================================================================
# PDF export endpoints
# ===========================================================================

def _fmt_dt(dt: datetime | None) -> str:
    return dt.strftime("%Y-%m-%d %H:%M") if dt else ""


@router.get("/decisions/export/pdf")
def export_decisions_pdf(
    category: Optional[str] = Query(None),
    status_filter: Optional[DecisionStatus] = Query(None, alias="status"),
    creator: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sd = _parse_date(start_date)
    ed = _parse_date(end_date)
    _validate_date_range(sd, ed)

    query = _build_decisions_query(db, category, status_filter, creator, sd, ed)
    query = query.order_by(Decision.created_at.desc())
    decisions = query.all()
    items = _build_decision_items(db, decisions)
    summary = _build_decision_summary(db)

    filter_desc = _build_filter_description(
        category=category, status_filter=status_filter, creator=creator,
        start_date=start_date, end_date=end_date,
    )

    headers = ["ID", "Title", "Category", "Status", "Creator", "Created", "Updated", "Alternatives", "Approvals"]
    rows = [
        [str(i.id), i.title, i.category, i.status, i.creator,
         _fmt_dt(i.created_at), _fmt_dt(i.updated_at), str(i.alternative_count), str(i.approval_count)]
        for i in items
    ]
    summary_lines = [
        f"<b>Summary:</b> Total={summary.total}, Draft={summary.draft}, Under Review={summary.under_review}, "
        f"Approved={summary.approved}, Rejected={summary.rejected}, Archived={summary.archived}",
    ]

    buf = _make_pdf("Decisions Report", filter_desc, headers, rows, summary_lines)
    return StreamingResponse(buf, media_type="application/pdf", headers={
        "Content-Disposition": "attachment; filename=decisions_report.pdf",
    })


@router.get("/approvals/export/pdf")
def export_approvals_pdf(
    status_filter: Optional[str] = Query(None, alias="status"),
    reviewer: Optional[int] = Query(None),
    decision: Optional[int] = Query(None),
    level: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sd = _parse_date(start_date)
    ed = _parse_date(end_date)
    _validate_date_range(sd, ed)
    if status_filter is not None and status_filter.lower() not in {"pending", "approved", "rejected"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid status: '{status_filter}'.")

    query = _build_approvals_query(db, current_user, status_filter, reviewer, decision, sd, ed)
    query = query.order_by(AuditLog.created_at.desc())
    logs = query.all()
    items = _build_approval_items(db, logs)
    summary = _build_approval_summary(db)

    filter_desc = _build_filter_description(
        status_filter=status_filter, reviewer=reviewer, decision=decision,
        start_date=start_date, end_date=end_date,
    )

    headers = ["ID", "Decision", "Reviewer", "Status", "Completed"]
    rows = [
        [str(i.id), i.decision_title, i.reviewer, i.status, _fmt_dt(i.completed_date)]
        for i in items
    ]
    summary_lines = [
        f"<b>Summary:</b> Total={summary.total}, Approved={summary.approved}, "
        f"Rejected={summary.rejected}, Completion Rate={summary.completion_rate:.1%}",
    ]

    buf = _make_pdf("Approvals Report", filter_desc, headers, rows, summary_lines)
    return StreamingResponse(buf, media_type="application/pdf", headers={
        "Content-Disposition": "attachment; filename=approvals_report.pdf",
    })


@router.get("/teams/export/pdf")
def export_teams_pdf(
    team: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    status_filter: Optional[DecisionStatus] = Query(None, alias="status"),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sd = _parse_date(start_date)
    ed = _parse_date(end_date)
    _validate_date_range(sd, ed)

    items = _build_teams_data(db, team, sd, ed, status_filter, category)

    filter_desc = _build_filter_description(
        team=team, start_date=start_date, end_date=end_date,
        status_filter=status_filter, category=category,
    )

    headers = ["Team", "Members", "Decisions", "Approved", "Rejected", "Pending"]
    rows = [
        [i.team, str(i.member_count), str(i.decision_count),
         str(i.approval_stats.approved), str(i.approval_stats.rejected), str(i.approval_stats.pending)]
        for i in items
    ]
    summary_lines = [f"<b>Total teams:</b> {len(items)}"]

    buf = _make_pdf("Teams Report", filter_desc, headers, rows, summary_lines)
    return StreamingResponse(buf, media_type="application/pdf", headers={
        "Content-Disposition": "attachment; filename=teams_report.pdf",
    })


@router.get("/audit/export/pdf")
def export_audit_pdf(
    user: Optional[int] = Query(None),
    action: Optional[AuditAction] = Query(None),
    entity_type: Optional[AuditEntityType] = Query(None),
    entity_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sd = _parse_date(start_date)
    ed = _parse_date(end_date)
    _validate_date_range(sd, ed)

    query = _build_audit_query(db, current_user, user, action, entity_type, entity_id, sd, ed)
    query = query.order_by(AuditLog.created_at.desc())
    logs = query.all()
    items = _build_audit_items(db, logs)

    filter_desc = _build_filter_description(
        user=user, action=action, entity_type=entity_type,
        entity_id=entity_id, start_date=start_date, end_date=end_date,
    )

    headers = ["ID", "User", "Action", "Entity Type", "Entity ID", "Description", "Timestamp", "IP Address"]
    rows = [
        [str(i.id), i.user, i.action, i.entity_type,
         str(i.entity_id) if i.entity_id else "", i.description or "",
         _fmt_dt(i.timestamp), i.ip_address or ""]
        for i in items
    ]

    buf = _make_pdf("Audit Report", filter_desc, headers, rows, [f"<b>Total records:</b> {len(items)}"])
    return StreamingResponse(buf, media_type="application/pdf", headers={
        "Content-Disposition": "attachment; filename=audit_report.pdf",
    })


# ===========================================================================
# Excel export endpoints
# ===========================================================================

@router.get("/decisions/export/excel")
def export_decisions_excel(
    category: Optional[str] = Query(None),
    status_filter: Optional[DecisionStatus] = Query(None, alias="status"),
    creator: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sd = _parse_date(start_date)
    ed = _parse_date(end_date)
    _validate_date_range(sd, ed)

    query = _build_decisions_query(db, category, status_filter, creator, sd, ed)
    query = query.order_by(Decision.created_at.desc())
    decisions = query.all()
    items = _build_decision_items(db, decisions)
    summary = _build_decision_summary(db)

    headers = ["ID", "Title", "Category", "Status", "Creator", "Created", "Updated", "Alternatives", "Approvals"]
    rows = [
        [i.id, i.title, i.category, i.status, i.creator,
         i.created_at, i.updated_at, i.alternative_count, i.approval_count]
        for i in items
    ]
    summary_rows = [
        ("Total", summary.total),
        ("Draft", summary.draft),
        ("Under Review", summary.under_review),
        ("Approved", summary.approved),
        ("Rejected", summary.rejected),
        ("Archived", summary.archived),
    ]

    buf = _make_excel("Decisions Report", "Decisions", headers, rows, summary_rows)
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={
        "Content-Disposition": "attachment; filename=decisions_report.xlsx",
    })


@router.get("/approvals/export/excel")
def export_approvals_excel(
    status_filter: Optional[str] = Query(None, alias="status"),
    reviewer: Optional[int] = Query(None),
    decision: Optional[int] = Query(None),
    level: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sd = _parse_date(start_date)
    ed = _parse_date(end_date)
    _validate_date_range(sd, ed)
    if status_filter is not None and status_filter.lower() not in {"pending", "approved", "rejected"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid status: '{status_filter}'.")

    query = _build_approvals_query(db, current_user, status_filter, reviewer, decision, sd, ed)
    query = query.order_by(AuditLog.created_at.desc())
    logs = query.all()
    items = _build_approval_items(db, logs)
    summary = _build_approval_summary(db)

    headers = ["ID", "Decision ID", "Decision", "Reviewer", "Level", "Status", "Assigned", "Completed", "Turnaround (hrs)"]
    rows = [
        [i.id, i.decision_id, i.decision_title, i.reviewer, i.level or "",
         i.status, i.assigned_date, i.completed_date, i.turnaround_time_hours or ""]
        for i in items
    ]
    summary_rows = [
        ("Total", summary.total),
        ("Pending", summary.pending),
        ("Approved", summary.approved),
        ("Rejected", summary.rejected),
        ("Completion Rate", f"{summary.completion_rate:.1%}"),
    ]

    buf = _make_excel("Approvals Report", "Approvals", headers, rows, summary_rows)
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={
        "Content-Disposition": "attachment; filename=approvals_report.xlsx",
    })


@router.get("/teams/export/excel")
def export_teams_excel(
    team: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    status_filter: Optional[DecisionStatus] = Query(None, alias="status"),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sd = _parse_date(start_date)
    ed = _parse_date(end_date)
    _validate_date_range(sd, ed)

    items = _build_teams_data(db, team, sd, ed, status_filter, category)

    headers = ["Team", "Members", "Decisions", "Approved", "Rejected", "Pending"]
    rows = [
        [i.team, i.member_count, i.decision_count,
         i.approval_stats.approved, i.approval_stats.rejected, i.approval_stats.pending]
        for i in items
    ]

    buf = _make_excel("Teams Report", "Teams", headers, rows, [("Total Teams", len(items))])
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={
        "Content-Disposition": "attachment; filename=teams_report.xlsx",
    })


@router.get("/audit/export/excel")
def export_audit_excel(
    user: Optional[int] = Query(None),
    action: Optional[AuditAction] = Query(None),
    entity_type: Optional[AuditEntityType] = Query(None),
    entity_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sd = _parse_date(start_date)
    ed = _parse_date(end_date)
    _validate_date_range(sd, ed)

    query = _build_audit_query(db, current_user, user, action, entity_type, entity_id, sd, ed)
    query = query.order_by(AuditLog.created_at.desc())
    logs = query.all()
    items = _build_audit_items(db, logs)

    headers = ["ID", "User", "Action", "Entity Type", "Entity ID", "Description", "Timestamp", "IP Address"]
    rows = [
        [i.id, i.user, i.action, i.entity_type,
         i.entity_id or "", i.description or "", i.timestamp, i.ip_address or ""]
        for i in items
    ]

    buf = _make_excel("Audit Report", "Audit", headers, rows, [("Total Records", len(items))])
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={
        "Content-Disposition": "attachment; filename=audit_report.xlsx",
    })
