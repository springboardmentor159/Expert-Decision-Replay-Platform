from datetime import datetime
from typing import Literal
from io import BytesIO

from fastapi.responses import StreamingResponse

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)

from openpyxl import Workbook
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
# =========================================================
# PDF / EXCEL EXPORT HELPERS
# =========================================================

def _create_pdf(title: str, headers: list[str], rows: list[list]):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()

    elements = [
        Paragraph(title, styles["Title"]),
        Spacer(1, 15),
    ]

    table_data = [headers] + rows

    table = Table(
        table_data,
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), "grey"),
                ("TEXTCOLOR", (0, 0), (-1, 0), "white"),
                ("GRID", (0, 0), (-1, -1), 0.5, "black"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), ["white", "lightgrey"]),
            ]
        )
    )

    elements.append(table)

    document.build(elements)

    buffer.seek(0)
    return buffer


def _create_excel(
    sheet_name: str,
    headers: list[str],
    rows: list[list],
):
    workbook = Workbook()

    worksheet = workbook.active
    worksheet.title = sheet_name

    worksheet.append(headers)

    for row in rows:
        worksheet.append(row)

    # Header formatting
    for cell in worksheet[1]:
        cell.font = cell.font.copy(bold=True)

    # Automatically size columns
    for column_cells in worksheet.columns:
        max_length = 0
        column_letter = column_cells[0].column_letter

        for cell in column_cells:
            if cell.value is not None:
                max_length = max(
                    max_length,
                    len(str(cell.value)),
                )

        worksheet.column_dimensions[column_letter].width = min(
            max_length + 2,
            40,
        )

    buffer = BytesIO()
    workbook.save(buffer)

    buffer.seek(0)
    return buffer


# =========================================================
# DECISION REPORT - PDF
# =========================================================

@router.get("/decisions/pdf")
def decision_report_pdf(
    category: str | None = Query(default=None),
    decision_status: str | None = Query(default=None),
    created_by: int | None = Query(default=None, ge=1),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    tag: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if start_date is not None and end_date is not None and end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="end_date must be greater than or equal to start_date",
        )

    report = get_decision_report(
        db=db,
        category=category,
        decision_status=decision_status,
        created_by=created_by,
        start_date=start_date,
        end_date=end_date,
        tag=tag,
        page=1,
        page_size=100,
        sort_by="created_at",
        sort_order="desc",
    )

    headers = [
        "ID",
        "Title",
        "Category",
        "Status",
        "Creator",
        "Alternatives",
        "Approvals",
    ]

    rows = [
        [
            item["id"],
            item["title"],
            item["category"],
            item["status"],
            item["creator_name"],
            item["alternative_count"],
            item["approval_count"],
        ]
        for item in report["items"]
    ]

    buffer = _create_pdf(
        "Decision Report",
        headers,
        rows,
    )

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=decision_report.pdf"
        },
    )


# =========================================================
# DECISION REPORT - EXCEL
# =========================================================

@router.get("/decisions/excel")
def decision_report_excel(
    category: str | None = Query(default=None),
    decision_status: str | None = Query(default=None),
    created_by: int | None = Query(default=None, ge=1),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    tag: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if start_date is not None and end_date is not None and end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="end_date must be greater than or equal to start_date",
        )

    report = get_decision_report(
        db=db,
        category=category,
        decision_status=decision_status,
        created_by=created_by,
        start_date=start_date,
        end_date=end_date,
        tag=tag,
        page=1,
        page_size=100,
        sort_by="created_at",
        sort_order="desc",
    )

    headers = [
        "ID",
        "Title",
        "Category",
        "Status",
        "Creator",
        "Alternatives",
        "Approvals",
    ]

    rows = [
        [
            item["id"],
            item["title"],
            item["category"],
            item["status"],
            item["creator_name"],
            item["alternative_count"],
            item["approval_count"],
        ]
        for item in report["items"]
    ]

    buffer = _create_excel(
        "Decisions",
        headers,
        rows,
    )

    return StreamingResponse(
        buffer,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": "attachment; filename=decision_report.xlsx"
        },
    )


# =========================================================
# APPROVAL REPORT - PDF
# =========================================================

@router.get("/approvals/pdf")
def approval_report_pdf(
    approval_status: str | None = Query(default=None),
    reviewer_id: int | None = Query(default=None, ge=1),
    decision_id: int | None = Query(default=None, ge=1),
    approval_level: str | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if start_date is not None and end_date is not None and end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="end_date must be greater than or equal to start_date",
        )

    report = get_approval_report(
        db=db,
        approval_status=approval_status,
        reviewer_id=reviewer_id,
        decision_id=decision_id,
        approval_level=approval_level,
        start_date=start_date,
        end_date=end_date,
        page=1,
        page_size=100,
        sort_by="created_at",
        sort_order="desc",
    )

    headers = [
        "ID",
        "Decision ID",
        "Decision",
        "Reviewer",
        "Level",
        "Status",
        "Turnaround Hours",
    ]

    rows = [
        [
            item["id"],
            item["decision_id"],
            item["decision_title"],
            item["reviewer_name"],
            item["approval_level"],
            item["status"],
            item["turnaround_hours"],
        ]
        for item in report["items"]
    ]

    buffer = _create_pdf(
        "Approval Report",
        headers,
        rows,
    )

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=approval_report.pdf"
        },
    )


# =========================================================
# APPROVAL REPORT - EXCEL
# =========================================================

@router.get("/approvals/excel")
def approval_report_excel(
    approval_status: str | None = Query(default=None),
    reviewer_id: int | None = Query(default=None, ge=1),
    decision_id: int | None = Query(default=None, ge=1),
    approval_level: str | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if start_date is not None and end_date is not None and end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="end_date must be greater than or equal to start_date",
        )

    report = get_approval_report(
        db=db,
        approval_status=approval_status,
        reviewer_id=reviewer_id,
        decision_id=decision_id,
        approval_level=approval_level,
        start_date=start_date,
        end_date=end_date,
        page=1,
        page_size=100,
        sort_by="created_at",
        sort_order="desc",
    )

    headers = [
        "ID",
        "Decision ID",
        "Decision",
        "Reviewer",
        "Level",
        "Status",
        "Turnaround Hours",
    ]

    rows = [
        [
            item["id"],
            item["decision_id"],
            item["decision_title"],
            item["reviewer_name"],
            item["approval_level"],
            item["status"],
            item["turnaround_hours"],
        ]
        for item in report["items"]
    ]

    buffer = _create_excel(
        "Approvals",
        headers,
        rows,
    )

    return StreamingResponse(
        buffer,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": "attachment; filename=approval_report.xlsx"
        },
    )


# =========================================================
# TEAM REPORT - PDF
# =========================================================

@router.get("/teams/pdf")
def team_report_pdf(
    team: str | None = Query(default=None),
    decision_status: str | None = Query(default=None),
    category: str | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if start_date is not None and end_date is not None and end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="end_date must be greater than or equal to start_date",
        )

    report = get_team_report(
        db=db,
        team=team,
        decision_status=decision_status,
        category=category,
        start_date=start_date,
        end_date=end_date,
        page=1,
        page_size=100,
        sort_by="team_name",
        sort_order="asc",
    )

    headers = [
        "Team",
        "Members",
        "Decisions",
        "Approved",
        "Rejected",
        "Pending",
        "Approvals",
        "Approved Approvals",
        "Rejected Approvals",
        "Pending Approvals",
        "Completion %",
    ]

    rows = [
        [
            item["team_name"],
            item["member_count"],
            item["total_decisions"],
            item["approved_decisions"],
            item["rejected_decisions"],
            item["pending_decisions"],
            item["total_approvals"],
            item["approved_approvals"],
            item["rejected_approvals"],
            item["pending_approvals"],
            item["approval_completion_rate"],
        ]
        for item in report["items"]
    ]

    buffer = _create_pdf(
        "Team Report",
        headers,
        rows,
    )

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=team_report.pdf"
        },
    )


# =========================================================
# TEAM REPORT - EXCEL
# =========================================================

@router.get("/teams/excel")
def team_report_excel(
    team: str | None = Query(default=None),
    decision_status: str | None = Query(default=None),
    category: str | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if start_date is not None and end_date is not None and end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="end_date must be greater than or equal to start_date",
        )

    report = get_team_report(
        db=db,
        team=team,
        decision_status=decision_status,
        category=category,
        start_date=start_date,
        end_date=end_date,
        page=1,
        page_size=100,
        sort_by="team_name",
        sort_order="asc",
    )

    headers = [
        "Team",
        "Members",
        "Decisions",
        "Approved",
        "Rejected",
        "Pending",
        "Approvals",
        "Approved Approvals",
        "Rejected Approvals",
        "Pending Approvals",
        "Completion %",
    ]

    rows = [
        [
            item["team_name"],
            item["member_count"],
            item["total_decisions"],
            item["approved_decisions"],
            item["rejected_decisions"],
            item["pending_decisions"],
            item["total_approvals"],
            item["approved_approvals"],
            item["rejected_approvals"],
            item["pending_approvals"],
            item["approval_completion_rate"],
        ]
        for item in report["items"]
    ]

    buffer = _create_excel(
        "Teams",
        headers,
        rows,
    )

    return StreamingResponse(
        buffer,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": "attachment; filename=team_report.xlsx"
        },
    )


