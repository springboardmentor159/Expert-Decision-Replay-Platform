from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from openpyxl import Workbook
from openpyxl.utils import get_column_letter

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from app.core.security import get_current_user
from app.db.database import get_db
from app.services.report import (
    get_decision_report,
    get_approval_report,
    get_team_report,
    get_audit_report,
)

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


# =========================================================
# COMMON HELPERS
# =========================================================

def _parse_datetime(value: str | None):
    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid date format: {value}",
        )


def _filters_dict(**kwargs):
    return {
        key: value
        for key, value in kwargs.items()
        if value is not None
    }


def _format_filter_text(filters: dict):
    if not filters:
        return "None"

    return "\n".join(
        f"{key}: {value}"
        for key, value in filters.items()
    )


def _pdf_response(
    buffer: BytesIO,
    filename: str,
):
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            )
        },
    )


def _excel_response(
    buffer: BytesIO,
    filename: str,
):
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            )
        },
    )


# =========================================================
# DECISION REPORT
# =========================================================

@router.get("/decisions")
def decision_report(
    category: str | None = None,
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    created_by: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    tag: str | None = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_date",
    order: str = "desc",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_decision_report(
        db=db,
        current_user=current_user,
        category=category,
        status_filter=status_filter,
        created_by=created_by,
        start_date=_parse_datetime(start_date),
        end_date=_parse_datetime(end_date),
        tag=tag,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
    )


# =========================================================
# APPROVAL REPORT
# =========================================================

@router.get("/approvals")
def approval_report(
    approval_status: str | None = Query(
        default=None,
        alias="status",
    ),
    reviewer: int | None = None,
    decision: int | None = Query(
        default=None,
        alias="decision_id",
    ),
    approval_level: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "approval_date",
    order: str = "desc",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_approval_report(
        db=db,
        current_user=current_user,
        approval_status=approval_status,
        reviewer=reviewer,
        decision_id=decision,
        approval_level=approval_level,
        start_date=_parse_datetime(start_date),
        end_date=_parse_datetime(end_date),
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
    )


# =========================================================
# TEAM REPORT
# =========================================================

@router.get("/teams")
def team_report(
    team: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    decision_status: str | None = Query(
        default=None,
        alias="status",
    ),
    category: str | None = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "team_name",
    order: str = "asc",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_team_report(
        db=db,
        current_user=current_user,
        team=team,
        start_date=_parse_datetime(start_date),
        end_date=_parse_datetime(end_date),
        decision_status=decision_status,
        category=category,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
    )


# =========================================================
# AUDIT REPORT
# =========================================================

@router.get("/audit")
def audit_report(
    user_id: int | None = None,
    action: str | None = None,
    entity_type: str | None = None,
    entity_id: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "timestamp",
    order: str = "desc",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_audit_report(
        db=db,
        current_user=current_user,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        start_date=_parse_datetime(start_date),
        end_date=_parse_datetime(end_date),
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
    )


# =========================================================
# PDF GENERATION
# =========================================================

def _build_pdf(
    title: str,
    filters: dict,
    summary_lines: list[str],
    headers: list[str],
    rows: list[list],
):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            title,
            styles["Title"],
        )
    )

    story.append(
        Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            "<b>Applied Filters</b>",
            styles["Heading3"],
        )
    )

    filter_text = _format_filter_text(filters)

    story.append(
        Paragraph(
            filter_text.replace("\n", "<br/>"),
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 8))

    if summary_lines:
        story.append(
            Paragraph(
                "<b>Summary</b>",
                styles["Heading3"],
            )
        )

        for line in summary_lines:
            story.append(
                Paragraph(
                    line,
                    styles["Normal"],
                )
            )

        story.append(Spacer(1, 8))

    table_data = [headers] + rows

    table = Table(
        table_data,
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.black,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    story.append(table)

    document.build(story)

    return buffer


# =========================================================
# EXCEL GENERATION
# =========================================================

def _build_excel(
    title: str,
    headers: list[str],
    rows: list[list],
    summary: list[tuple[str, str]] | None = None,
):
    buffer = BytesIO()

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = title[:31]

    current_row = 1

    worksheet.cell(
        row=current_row,
        column=1,
        value=title,
    )

    current_row += 1

    worksheet.cell(
        row=current_row,
        column=1,
        value="Generated",
    )

    worksheet.cell(
        row=current_row,
        column=2,
        value=datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    )

    current_row += 2

    if summary:
        worksheet.cell(
            row=current_row,
            column=1,
            value="Summary",
        )

        current_row += 1

        for key, value in summary:
            worksheet.cell(
                row=current_row,
                column=1,
                value=key,
            )

            worksheet.cell(
                row=current_row,
                column=2,
                value=value,
            )

            current_row += 1

        current_row += 1

    for column_index, header in enumerate(
        headers,
        start=1,
    ):
        worksheet.cell(
            row=current_row,
            column=column_index,
            value=header,
        )

    header_row = current_row
    current_row += 1

    for row in rows:
        for column_index, value in enumerate(
            row,
            start=1,
        ):
            if isinstance(value, datetime):
                value = value.replace(
                    tzinfo=None
                )

            worksheet.cell(
                row=current_row,
                column=column_index,
                value=value,
            )

        current_row += 1

    # Header formatting
    for cell in worksheet[header_row]:
        cell.font = cell.font.copy(
            bold=True
        )

    # Auto-size columns
    for column_cells in worksheet.columns:
        max_length = 0

        for cell in column_cells:
            if cell.value is not None:
                max_length = max(
                    max_length,
                    len(str(cell.value)),
                )

        column_letter = get_column_letter(
            column_cells[0].column
        )

        worksheet.column_dimensions[
            column_letter
        ].width = min(
            max(max_length + 2, 12),
            50,
        )

    worksheet.freeze_panes = (
        f"A{header_row + 1}"
    )

    workbook.save(buffer)

    return buffer


# =========================================================
# DECISION PDF EXPORT
# =========================================================

@router.get("/decisions/export/pdf")
def export_decisions_pdf(
    category: str | None = None,
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    created_by: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    tag: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    report = get_decision_report(
        db=db,
        current_user=current_user,
        category=category,
        status_filter=status_filter,
        created_by=created_by,
        start_date=_parse_datetime(start_date),
        end_date=_parse_datetime(end_date),
        tag=tag,
        page=1,
        page_size=100,
        sort_by="created_date",
        order="desc",
    )

    filters = _filters_dict(
        category=category,
        status=status_filter,
        created_by=created_by,
        start_date=start_date,
        end_date=end_date,
        tag=tag,
    )

    summary = [
        f"Total decisions: {report.summary.total_decisions}",
        f"Draft: {report.summary.draft}",
        f"Under Review: {report.summary.under_review}",
        f"Approved: {report.summary.approved}",
        f"Rejected: {report.summary.rejected}",
        f"Archived: {report.summary.archived}",
    ]

    headers = [
        "Decision ID",
        "Title",
        "Category",
        "Status",
        "Created By",
        "Created Date",
        "Updated Date",
        "Alternatives",
        "Approvals",
        "Tags",
    ]

    rows = [
        [
            row.decision_id,
            row.title,
            row.category,
            row.status,
            row.created_by or "",
            row.created_date,
            row.updated_date,
            row.number_of_alternatives,
            row.number_of_approvals,
            ", ".join(row.tags),
        ]
        for row in report.data
    ]

    buffer = _build_pdf(
        "Decision Report",
        filters,
        summary,
        headers,
        rows,
    )

    return _pdf_response(
        buffer,
        "decision_report.pdf",
    )


# =========================================================
# APPROVAL PDF EXPORT
# =========================================================

@router.get("/approvals/export/pdf")
def export_approvals_pdf(
    approval_status: str | None = Query(
        default=None,
        alias="status",
    ),
    reviewer: int | None = None,
    decision: int | None = Query(
        default=None,
        alias="decision_id",
    ),
    approval_level: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    report = get_approval_report(
        db=db,
        current_user=current_user,
        approval_status=approval_status,
        reviewer=reviewer,
        decision_id=decision,
        approval_level=approval_level,
        start_date=_parse_datetime(start_date),
        end_date=_parse_datetime(end_date),
        page=1,
        page_size=100,
        sort_by="approval_date",
        order="desc",
    )

    filters = _filters_dict(
        status=approval_status,
        reviewer=reviewer,
        decision_id=decision,
        approval_level=approval_level,
        start_date=start_date,
        end_date=end_date,
    )

    summary = [
        f"Total approvals: {report.stats.total_approvals}",
        f"Pending: {report.stats.pending}",
        f"Approved: {report.stats.approved}",
        f"Rejected: {report.stats.rejected}",
        (
            "Average turnaround: "
            f"{report.stats.average_approval_turnaround or 'N/A'}"
        ),
        (
            "Completion rate: "
            f"{report.stats.completion_rate}%"
        ),
    ]

    headers = [
        "Approval ID",
        "Decision ID",
        "Decision Title",
        "Reviewer",
        "Approval Level",
        "Status",
        "Assigned Date",
        "Completed Date",
        "Turnaround",
    ]

    rows = [
        [
            row.approval_id,
            row.decision_id,
            row.decision_title,
            row.reviewer or "",
            row.approval_level,
            row.approval_status,
            row.assigned_date,
            row.completed_date,
            row.approval_turnaround_time or "",
        ]
        for row in report.data
    ]

    buffer = _build_pdf(
        "Approval Report",
        filters,
        summary,
        headers,
        rows,
    )

    return _pdf_response(
        buffer,
        "approval_report.pdf",
    )


# =========================================================
# TEAM PDF EXPORT
# =========================================================

@router.get("/teams/export/pdf")
def export_teams_pdf(
    team: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    decision_status: str | None = Query(
        default=None,
        alias="status",
    ),
    category: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    report = get_team_report(
        db=db,
        current_user=current_user,
        team=team,
        start_date=_parse_datetime(start_date),
        end_date=_parse_datetime(end_date),
        decision_status=decision_status,
        category=category,
        page=1,
        page_size=100,
        sort_by="team_name",
        order="asc",
    )

    filters = _filters_dict(
        team=team,
        start_date=start_date,
        end_date=end_date,
        status=decision_status,
        category=category,
    )

    headers = [
        "Team Name",
        "Members",
        "Total Decisions",
        "Approved",
        "Rejected",
        "Pending",
        "Approval Statistics",
    ]

    rows = [
        [
            row.team_name,
            row.number_of_members,
            row.total_decisions,
            row.approved_decisions,
            row.rejected_decisions,
            row.pending_decisions,
            str(row.team_approval_statistics),
        ]
        for row in report.data
    ]

    buffer = _build_pdf(
        "Team Report",
        filters,
        [],
        headers,
        rows,
    )

    return _pdf_response(
        buffer,
        "team_report.pdf",
    )


# =========================================================
# AUDIT PDF EXPORT
# =========================================================

@router.get("/audit/export/pdf")
def export_audit_pdf(
    user_id: int | None = None,
    action: str | None = None,
    entity_type: str | None = None,
    entity_id: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    report = get_audit_report(
        db=db,
        current_user=current_user,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        start_date=_parse_datetime(start_date),
        end_date=_parse_datetime(end_date),
        page=1,
        page_size=100,
        sort_by="timestamp",
        order="desc",
    )

    filters = _filters_dict(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        start_date=start_date,
        end_date=end_date,
    )

    headers = [
        "User",
        "Action",
        "Entity Type",
        "Entity ID",
        "Description",
        "Timestamp",
        "IP Address",
    ]

    rows = [
        [
            row.user or "",
            row.action,
            row.entity_type,
            row.entity_id,
            row.description,
            row.timestamp,
            row.ip_address or "",
        ]
        for row in report.data
    ]

    buffer = _build_pdf(
        "Audit Report",
        filters,
        [],
        headers,
        rows,
    )

    return _pdf_response(
        buffer,
        "audit_report.pdf",
    )


# =========================================================
# DECISION EXCEL EXPORT
# =========================================================

@router.get("/decisions/export/excel")
def export_decisions_excel(
    category: str | None = None,
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    created_by: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    tag: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    report = get_decision_report(
        db=db,
        current_user=current_user,
        category=category,
        status_filter=status_filter,
        created_by=created_by,
        start_date=_parse_datetime(start_date),
        end_date=_parse_datetime(end_date),
        tag=tag,
        page=1,
        page_size=100,
        sort_by="created_date",
        order="desc",
    )

    headers = [
        "Decision ID",
        "Title",
        "Category",
        "Status",
        "Created By",
        "Created Date",
        "Updated Date",
        "Alternatives",
        "Approvals",
        "Tags",
    ]

    rows = [
        [
            row.decision_id,
            row.title,
            row.category,
            row.status,
            row.created_by or "",
            row.created_date,
            row.updated_date,
            row.number_of_alternatives,
            row.number_of_approvals,
            ", ".join(row.tags),
        ]
        for row in report.data
    ]

    summary = [
        ("Total Decisions", str(report.summary.total_decisions)),
        ("Draft", str(report.summary.draft)),
        ("Under Review", str(report.summary.under_review)),
        ("Approved", str(report.summary.approved)),
        ("Rejected", str(report.summary.rejected)),
        ("Archived", str(report.summary.archived)),
    ]

    buffer = _build_excel(
        "Decision Report",
        headers,
        rows,
        summary,
    )

    return _excel_response(
        buffer,
        "decision_report.xlsx",
    )


# =========================================================
# APPROVAL EXCEL EXPORT
# =========================================================

@router.get("/approvals/export/excel")
def export_approvals_excel(
    approval_status: str | None = Query(
        default=None,
        alias="status",
    ),
    reviewer: int | None = None,
    decision: int | None = Query(
        default=None,
        alias="decision_id",
    ),
    approval_level: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    report = get_approval_report(
        db=db,
        current_user=current_user,
        approval_status=approval_status,
        reviewer=reviewer,
        decision_id=decision,
        approval_level=approval_level,
        start_date=_parse_datetime(start_date),
        end_date=_parse_datetime(end_date),
        page=1,
        page_size=100,
        sort_by="approval_date",
        order="desc",
    )

    headers = [
        "Approval ID",
        "Decision ID",
        "Decision Title",
        "Reviewer",
        "Approval Level",
        "Status",
        "Assigned Date",
        "Completed Date",
        "Turnaround",
    ]

    rows = [
        [
            row.approval_id,
            row.decision_id,
            row.decision_title,
            row.reviewer or "",
            row.approval_level,
            row.approval_status,
            row.assigned_date,
            row.completed_date,
            row.approval_turnaround_time or "",
        ]
        for row in report.data
    ]

    summary = [
        ("Total Approvals", str(report.stats.total_approvals)),
        ("Pending", str(report.stats.pending)),
        ("Approved", str(report.stats.approved)),
        ("Rejected", str(report.stats.rejected)),
        (
            "Average Turnaround",
            str(
                report.stats.average_approval_turnaround
                or "N/A"
            ),
        ),
        (
            "Completion Rate",
            f"{report.stats.completion_rate}%",
        ),
    ]

    buffer = _build_excel(
        "Approval Report",
        headers,
        rows,
        summary,
    )

    return _excel_response(
        buffer,
        "approval_report.xlsx",
    )


# =========================================================
# TEAM EXCEL EXPORT
# =========================================================

@router.get("/teams/export/excel")
def export_teams_excel(
    team: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    decision_status: str | None = Query(
        default=None,
        alias="status",
    ),
    category: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    report = get_team_report(
        db=db,
        current_user=current_user,
        team=team,
        start_date=_parse_datetime(start_date),
        end_date=_parse_datetime(end_date),
        decision_status=decision_status,
        category=category,
        page=1,
        page_size=100,
        sort_by="team_name",
        order="asc",
    )

    headers = [
        "Team Name",
        "Members",
        "Total Decisions",
        "Approved",
        "Rejected",
        "Pending",
        "Approval Statistics",
    ]

    rows = [
        [
            row.team_name,
            row.number_of_members,
            row.total_decisions,
            row.approved_decisions,
            row.rejected_decisions,
            row.pending_decisions,
            str(row.team_approval_statistics),
        ]
        for row in report.data
    ]

    buffer = _build_excel(
        "Team Report",
        headers,
        rows,
    )

    return _excel_response(
        buffer,
        "team_report.xlsx",
    )


# =========================================================
# AUDIT EXCEL EXPORT
# =========================================================

@router.get("/audit/export/excel")
def export_audit_excel(
    user_id: int | None = None,
    action: str | None = None,
    entity_type: str | None = None,
    entity_id: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    report = get_audit_report(
        db=db,
        current_user=current_user,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        start_date=_parse_datetime(start_date),
        end_date=_parse_datetime(end_date),
        page=1,
        page_size=100,
        sort_by="timestamp",
        order="desc",
    )

    headers = [
        "User",
        "Action",
        "Entity Type",
        "Entity ID",
        "Description",
        "Timestamp",
        "IP Address",
    ]

    rows = [
        [
            row.user or "",
            row.action,
            row.entity_type,
            row.entity_id,
            row.description,
            row.timestamp,
            row.ip_address or "",
        ]
        for row in report.data
    ]

    buffer = _build_excel(
        "Audit Report",
        headers,
        rows,
    )

    return _excel_response(
        buffer,
        "audit_report.xlsx",
    )