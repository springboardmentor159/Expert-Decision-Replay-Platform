from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


# =========================================================
# COMMON PDF HELPERS
# =========================================================

def format_value(value):
    """
    Convert Python values into readable PDF text.
    """

    if value is None:
        return "-"

    if isinstance(value, datetime):
        return value.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    return str(value)


def create_pdf_document(title: str):
    """
    Create a landscape A4 PDF document.
    """

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title=title,
    )

    return buffer, document


def get_pdf_styles():
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        spaceAfter=8,
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontSize=12,
        spaceBefore=8,
        spaceAfter=6,
    )

    normal_style = ParagraphStyle(
        "ReportNormal",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
    )

    return (
        title_style,
        heading_style,
        normal_style,
    )


def add_summary_table(
    story,
    summary,
    heading_style,
    normal_style,
):
    if not summary:
        return

    story.append(
        Paragraph(
            "Summary",
            heading_style
        )
    )

    summary_data = [
        ["Metric", "Value"]
    ]

    for key, value in summary.items():

        readable_key = key.replace(
            "_",
            " "
        ).title()

        if isinstance(value, float):
            value = round(value, 2)

        summary_data.append([
            readable_key,
            format_value(value)
        ])

    table = Table(
        summary_data,
        repeatRows=1,
        colWidths=[
            65 * mm,
            40 * mm,
        ],
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1F4E78")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "FONTNAME",
                (0, 1),
                (-1, -1),
                "Helvetica"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
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
                "MIDDLE"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
        ])
    )

    story.append(table)
    story.append(Spacer(1, 8))


def add_filters_table(
    story,
    filters,
    heading_style,
    normal_style,
):
    applied_filters = {
        key: value
        for key, value in filters.items()
        if value is not None
        and value != ""
    }

    story.append(
        Paragraph(
            "Applied Filters",
            heading_style
        )
    )

    if not applied_filters:

        story.append(
            Paragraph(
                "No filters applied",
                normal_style
            )
        )

        story.append(
            Spacer(1, 8)
        )

        return

    filter_data = [
        ["Filter", "Value"]
    ]

    for key, value in applied_filters.items():

        readable_key = key.replace(
            "_",
            " "
        ).title()

        filter_data.append([
            readable_key,
            format_value(value)
        ])

    table = Table(
        filter_data,
        repeatRows=1,
        colWidths=[
            65 * mm,
            100 * mm,
        ],
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#5B9BD5")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
        ])
    )

    story.append(table)
    story.append(Spacer(1, 8))


def create_data_table(
    headers,
    rows,
    column_widths=None,
):
    """
    Create a readable report data table.
    """

    table_data = [
        headers
    ]

    for row in rows:
        table_data.append([
            format_value(value)
            for value in row
        ])

    table = Table(
        table_data,
        repeatRows=1,
        colWidths=column_widths,
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1F4E78")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "FONTNAME",
                (0, 1),
                (-1, -1),
                "Helvetica"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.grey
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                4
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                4
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                4
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                4
            ),
        ])
    )

    return table


# =========================================================
# DECISION PDF
# =========================================================

def generate_decision_pdf(report, filters):
    buffer, document = create_pdf_document(
        "Decision Report"
    )

    title_style, heading_style, normal_style = (
        get_pdf_styles()
    )

    story = []

    story.append(
        Paragraph(
            "Expert Decision Replay Platform",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Decision Report",
            heading_style
        )
    )

    story.append(
        Paragraph(
            "Generated: "
            + datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            normal_style
        )
    )

    story.append(Spacer(1, 8))

    add_filters_table(
        story,
        filters,
        heading_style,
        normal_style,
    )

    add_summary_table(
        story,
        report.get("summary", {}),
        heading_style,
        normal_style,
    )

    headers = [
        "ID",
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

    rows = []

    for item in report.get("data", []):

        creator = item.get(
            "created_by",
            {}
        )

        rows.append([
            item.get("decision_id"),
            item.get("title"),
            item.get("category"),
            item.get("status"),
            creator.get("name"),
            item.get("created_date"),
            item.get("updated_date"),
            item.get("number_alternatives"),
            item.get("number_approvals"),
            ", ".join(
                item.get("tags", [])
            ) or "-",
        ])

    story.append(
        Paragraph(
            "Decision Data",
            heading_style
        )
    )

    table = create_data_table(
        headers,
        rows,
        column_widths=[
            12 * mm,
            55 * mm,
            28 * mm,
            25 * mm,
            28 * mm,
            35 * mm,
            35 * mm,
            22 * mm,
            22 * mm,
            35 * mm,
        ],
    )

    story.append(table)

    document.build(story)

    buffer.seek(0)

    return buffer


# =========================================================
# APPROVAL PDF
# =========================================================

def generate_approval_pdf(report, filters):
    buffer, document = create_pdf_document(
        "Approval Report"
    )

    title_style, heading_style, normal_style = (
        get_pdf_styles()
    )

    story = []

    story.append(
        Paragraph(
            "Expert Decision Replay Platform",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Approval Report",
            heading_style
        )
    )

    story.append(
        Paragraph(
            "Generated: "
            + datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            normal_style
        )
    )

    story.append(Spacer(1, 8))

    add_filters_table(
        story,
        filters,
        heading_style,
        normal_style,
    )

    add_summary_table(
        story,
        report.get("summary", {}),
        heading_style,
        normal_style,
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
        "Turnaround Hours",
    ]

    rows = []

    for item in report.get("data", []):

        reviewer = item.get(
            "reviewer",
            {}
        )

        rows.append([
            item.get("approval_id"),
            item.get("decision_id"),
            item.get("decision_title"),
            reviewer.get("name"),
            item.get("approval_level"),
            item.get("approval_status"),
            item.get("assigned_date"),
            item.get("completed_date"),
            item.get("turnaround_time_hours"),
        ])

    story.append(
        Paragraph(
            "Approval Data",
            heading_style
        )
    )

    table = create_data_table(
        headers,
        rows,
        column_widths=[
            20 * mm,
            20 * mm,
            50 * mm,
            35 * mm,
            30 * mm,
            25 * mm,
            35 * mm,
            35 * mm,
            30 * mm,
        ],
    )

    story.append(table)

    document.build(story)

    buffer.seek(0)

    return buffer


# =========================================================
# TEAM PDF
# =========================================================

def generate_team_pdf(report, filters):
    buffer, document = create_pdf_document(
        "Team Report"
    )

    title_style, heading_style, normal_style = (
        get_pdf_styles()
    )

    story = []

    story.append(
        Paragraph(
            "Expert Decision Replay Platform",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Team Report",
            heading_style
        )
    )

    story.append(
        Paragraph(
            "Generated: "
            + datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            normal_style
        )
    )

    story.append(Spacer(1, 8))

    add_filters_table(
        story,
        filters,
        heading_style,
        normal_style,
    )

    add_summary_table(
        story,
        report.get("summary", {}),
        heading_style,
        normal_style,
    )

    headers = [
        "Team",
        "Members",
        "Decisions",
        "Approved",
        "Rejected",
        "Pending",
        "Approval Total",
        "Approval Approved",
        "Approval Rejected",
        "Approval Pending",
        "Completion %",
    ]

    rows = []

    for item in report.get("data", []):

        statistics = item.get(
            "approval_statistics",
            {}
        )

        rows.append([
            item.get("team"),
            item.get("member_count"),
            item.get("total_decisions"),
            item.get("approved"),
            item.get("rejected"),
            item.get("pending"),
            statistics.get("total"),
            statistics.get("approved"),
            statistics.get("rejected"),
            statistics.get("pending"),
            statistics.get("completion_rate"),
        ])

    story.append(
        Paragraph(
            "Team Data",
            heading_style
        )
    )

    table = create_data_table(
        headers,
        rows,
        column_widths=[
            40 * mm,
            22 * mm,
            22 * mm,
            22 * mm,
            22 * mm,
            22 * mm,
            25 * mm,
            30 * mm,
            30 * mm,
            30 * mm,
            25 * mm,
        ],
    )

    story.append(table)

    document.build(story)

    buffer.seek(0)

    return buffer


# =========================================================
# AUDIT PDF
# =========================================================

def generate_audit_pdf(report, filters):
    buffer, document = create_pdf_document(
        "Audit Report"
    )

    title_style, heading_style, normal_style = (
        get_pdf_styles()
    )

    story = []

    story.append(
        Paragraph(
            "Expert Decision Replay Platform",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Audit Report",
            heading_style
        )
    )

    story.append(
        Paragraph(
            "Generated: "
            + datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            normal_style
        )
    )

    story.append(Spacer(1, 8))

    add_filters_table(
        story,
        filters,
        heading_style,
        normal_style,
    )

    add_summary_table(
        story,
        report.get("summary", {}),
        heading_style,
        normal_style,
    )

    headers = [
        "Audit ID",
        "User",
        "Action",
        "Entity Type",
        "Entity ID",
        "Description",
        "Timestamp",
        "IP Address",
        "Method",
        "Endpoint",
    ]

    rows = []

    for item in report.get("data", []):

        user = item.get(
            "user",
            {}
        )

        rows.append([
            item.get("audit_id"),
            user.get("name"),
            item.get("action"),
            item.get("entity_type"),
            item.get("entity_id"),
            item.get("description"),
            item.get("timestamp"),
            item.get("ip_address"),
            item.get("request_method"),
            item.get("endpoint"),
        ])

    story.append(
        Paragraph(
            "Audit Data",
            heading_style
        )
    )

    table = create_data_table(
        headers,
        rows,
        column_widths=[
            18 * mm,
            30 * mm,
            25 * mm,
            28 * mm,
            20 * mm,
            65 * mm,
            35 * mm,
            28 * mm,
            20 * mm,
            55 * mm,
        ],
    )

    story.append(table)

    document.build(story)

    buffer.seek(0)

    return buffer