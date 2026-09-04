import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)

from app.schemas.report import (
    DecisionReportItem,
    DecisionReportSummary,
    ApprovalReportItem,
    ApprovalReportSummary,
    TeamReportItem,
    TeamReportSummary,
    AuditReportItem,
    AuditReportSummary,
)


def _build_header_and_filters(
    title: str,
    filters: dict,
    user_name: str,
    styles,
    generated_at: datetime | None = None,
) -> list:
    flowables = []
    if generated_at is None:
        generated_at = datetime.utcnow()

    # Title
    flowables.append(Paragraph(title, styles["ReportTitle"]))
    flowables.append(
        Paragraph(
            f"Expert Decision Replay Platform &bull; Generated on: {generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')} &bull; By: {user_name}",
            styles["ReportSubtitle"],
        )
    )
    flowables.append(Spacer(1, 10))

    # Applied Filters Box
    filter_items = [f"<b>{k}:</b> {v}" for k, v in filters.items() if v is not None and v != ""]
    filter_text = " | ".join(filter_items) if filter_items else "None (All records included)"

    filter_table = Table(
        [[Paragraph(f"<b>Applied Filters:</b> {filter_text}", styles["FilterText"])]],
        colWidths=["100%"],
    )
    filter_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ])
    )
    flowables.append(filter_table)
    flowables.append(Spacer(1, 14))

    return flowables


def _get_custom_styles():
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0F172A"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportSubtitle",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#64748B"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#1E293B"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="FilterText",
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#334155"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableHeader",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=10,
            textColor=colors.white,
            alignment=1,  # Center
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableCell",
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#1E293B"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableCellCenter",
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#1E293B"),
            alignment=1,
        )
    )
    styles.add(
        ParagraphStyle(
            name="KpiLabel",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#475569"),
            alignment=1,
        )
    )
    styles.add(
        ParagraphStyle(
            name="KpiValue",
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=15,
            textColor=colors.HexColor("#0F172A"),
            alignment=1,
        )
    )
    styles.add(
        ParagraphStyle(
            name="EmptyNotice",
            fontName="Helvetica-Oblique",
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#64748B"),
            alignment=1,
        )
    )

    return styles


# 1. DECISION REPORT PDF GENERATOR
def generate_decisions_pdf(
    items: list[DecisionReportItem],
    summary: DecisionReportSummary,
    filters: dict,
    user_name: str = "Administrator",
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=24,
        rightMargin=24,
        topMargin=24,
        bottomMargin=24,
    )
    styles = _get_custom_styles()
    story = []

    # Header & Filters
    story.extend(_build_header_and_filters("Decision Management Report", filters, user_name, styles))

    # Summary Statistics KPI Grid
    story.append(Paragraph("Summary Statistics", styles["SectionHeading"]))
    kpi_data = [
        [
            Paragraph("TOTAL DECISIONS", styles["KpiLabel"]),
            Paragraph("DRAFT", styles["KpiLabel"]),
            Paragraph("UNDER REVIEW", styles["KpiLabel"]),
            Paragraph("APPROVED", styles["KpiLabel"]),
            Paragraph("REJECTED", styles["KpiLabel"]),
            Paragraph("ARCHIVED", styles["KpiLabel"]),
        ],
        [
            Paragraph(str(summary.total_decisions), styles["KpiValue"]),
            Paragraph(str(summary.draft_decisions), styles["KpiValue"]),
            Paragraph(str(summary.decisions_under_review), styles["KpiValue"]),
            Paragraph(str(summary.approved_decisions), styles["KpiValue"]),
            Paragraph(str(summary.rejected_decisions), styles["KpiValue"]),
            Paragraph(str(summary.archived_decisions), styles["KpiValue"]),
        ],
    ]
    kpi_table = Table(kpi_data, colWidths=[120, 120, 120, 120, 120, 120])
    kpi_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ])
    )
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    # Data Table
    story.append(Paragraph(f"Decision Records ({len(items)})", styles["SectionHeading"]))
    if not items:
        story.append(Paragraph("No decisions found matching the specified filter criteria.", styles["EmptyNotice"]))
    else:
        table_headers = [
            Paragraph("ID", styles["TableHeader"]),
            Paragraph("Title", styles["TableHeader"]),
            Paragraph("Category", styles["TableHeader"]),
            Paragraph("Status", styles["TableHeader"]),
            Paragraph("Created By", styles["TableHeader"]),
            Paragraph("Created Date", styles["TableHeader"]),
            Paragraph("Alts", styles["TableHeader"]),
            Paragraph("Appr", styles["TableHeader"]),
            Paragraph("Tags", styles["TableHeader"]),
        ]
        table_rows = [table_headers]

        for item in items:
            tags_str = ", ".join(item.tags) if item.tags else "-"
            creator_str = item.creator_name or f"User #{item.created_by}"
            table_rows.append([
                Paragraph(str(item.decision_id), styles["TableCellCenter"]),
                Paragraph(item.decision_title, styles["TableCell"]),
                Paragraph(item.category, styles["TableCell"]),
                Paragraph(item.status, styles["TableCellCenter"]),
                Paragraph(creator_str, styles["TableCell"]),
                Paragraph(item.created_date.strftime("%Y-%m-%d"), styles["TableCellCenter"]),
                Paragraph(str(item.number_of_alternatives), styles["TableCellCenter"]),
                Paragraph(str(item.number_of_approvals), styles["TableCellCenter"]),
                Paragraph(tags_str, styles["TableCell"]),
            ])

        col_widths = [35, 180, 85, 75, 95, 70, 35, 35, 114]
        data_table = Table(table_rows, colWidths=col_widths, repeatRows=1)
        data_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(data_table)

    doc.build(story)
    return buffer.getvalue()


# 2. APPROVAL REPORT PDF GENERATOR
def generate_approvals_pdf(
    items: list[ApprovalReportItem],
    summary: ApprovalReportSummary,
    filters: dict,
    user_name: str = "Administrator",
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=24,
        rightMargin=24,
        topMargin=24,
        bottomMargin=24,
    )
    styles = _get_custom_styles()
    story = []

    story.extend(_build_header_and_filters("Approval Workflow & Compliance Report", filters, user_name, styles))

    # Summary Statistics KPI Grid
    story.append(Paragraph("Summary Statistics", styles["SectionHeading"]))
    avg_turnaround = (
        f"{summary.average_approval_turnaround_time_hours:.1f} hrs"
        if summary.average_approval_turnaround_time_hours is not None
        else "N/A"
    )
    kpi_data = [
        [
            Paragraph("TOTAL APPROVALS", styles["KpiLabel"]),
            Paragraph("PENDING", styles["KpiLabel"]),
            Paragraph("APPROVED", styles["KpiLabel"]),
            Paragraph("REJECTED", styles["KpiLabel"]),
            Paragraph("AVG TURNAROUND", styles["KpiLabel"]),
            Paragraph("COMPLETION RATE", styles["KpiLabel"]),
        ],
        [
            Paragraph(str(summary.total_approvals), styles["KpiValue"]),
            Paragraph(str(summary.pending_approvals), styles["KpiValue"]),
            Paragraph(str(summary.approved_approvals), styles["KpiValue"]),
            Paragraph(str(summary.rejected_approvals), styles["KpiValue"]),
            Paragraph(avg_turnaround, styles["KpiValue"]),
            Paragraph(f"{summary.approval_completion_rate:.1f}%", styles["KpiValue"]),
        ],
    ]
    kpi_table = Table(kpi_data, colWidths=[120, 120, 120, 120, 120, 120])
    kpi_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ])
    )
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    # Data Table
    story.append(Paragraph(f"Approval Records ({len(items)})", styles["SectionHeading"]))
    if not items:
        story.append(Paragraph("No approval records found matching the specified filter criteria.", styles["EmptyNotice"]))
    else:
        table_headers = [
            Paragraph("Approval ID", styles["TableHeader"]),
            Paragraph("Decision ID", styles["TableHeader"]),
            Paragraph("Decision Title", styles["TableHeader"]),
            Paragraph("Reviewer", styles["TableHeader"]),
            Paragraph("Level", styles["TableHeader"]),
            Paragraph("Status", styles["TableHeader"]),
            Paragraph("Assigned Date", styles["TableHeader"]),
            Paragraph("Completed Date", styles["TableHeader"]),
            Paragraph("Turnaround", styles["TableHeader"]),
        ]
        table_rows = [table_headers]

        for item in items:
            reviewer_str = item.reviewer_name or f"User #{item.reviewer_id}"
            completed_str = item.completed_date.strftime("%Y-%m-%d %H:%M") if item.completed_date else "-"
            turnaround_str = (
                f"{item.approval_turnaround_time_hours:.1f}h"
                if item.approval_turnaround_time_hours is not None
                else "-"
            )
            table_rows.append([
                Paragraph(str(item.approval_id), styles["TableCellCenter"]),
                Paragraph(str(item.decision_id), styles["TableCellCenter"]),
                Paragraph(item.decision_title, styles["TableCell"]),
                Paragraph(reviewer_str, styles["TableCell"]),
                Paragraph(str(item.approval_level), styles["TableCellCenter"]),
                Paragraph(item.approval_status, styles["TableCellCenter"]),
                Paragraph(item.assigned_date.strftime("%Y-%m-%d %H:%M"), styles["TableCellCenter"]),
                Paragraph(completed_str, styles["TableCellCenter"]),
                Paragraph(turnaround_str, styles["TableCellCenter"]),
            ])

        col_widths = [60, 60, 174, 100, 40, 65, 85, 85, 55]
        data_table = Table(table_rows, colWidths=col_widths, repeatRows=1)
        data_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#047857")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(data_table)

    doc.build(story)
    return buffer.getvalue()


# 3. TEAM REPORT PDF GENERATOR
def generate_teams_pdf(
    items: list[TeamReportItem],
    summary: TeamReportSummary,
    filters: dict,
    user_name: str = "Administrator",
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=24,
        rightMargin=24,
        topMargin=24,
        bottomMargin=24,
    )
    styles = _get_custom_styles()
    story = []

    story.extend(_build_header_and_filters("Team Performance & Decision Report", filters, user_name, styles))

    # Summary Statistics KPI Grid
    story.append(Paragraph("Overall Organization Statistics", styles["SectionHeading"]))
    kpi_data = [
        [
            Paragraph("TOTAL TEAMS", styles["KpiLabel"]),
            Paragraph("TOTAL MEMBERS", styles["KpiLabel"]),
            Paragraph("TOTAL DECISIONS", styles["KpiLabel"]),
            Paragraph("TOTAL APPROVALS", styles["KpiLabel"]),
        ],
        [
            Paragraph(str(summary.total_teams), styles["KpiValue"]),
            Paragraph(str(summary.total_members), styles["KpiValue"]),
            Paragraph(str(summary.total_decisions), styles["KpiValue"]),
            Paragraph(str(summary.total_approvals), styles["KpiValue"]),
        ],
    ]
    kpi_table = Table(kpi_data, colWidths=[180, 180, 180, 180])
    kpi_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ])
    )
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    # Data Table
    story.append(Paragraph(f"Team Performance Breakdown ({len(items)})", styles["SectionHeading"]))
    if not items:
        story.append(Paragraph("No team data found matching the specified criteria.", styles["EmptyNotice"]))
    else:
        table_headers = [
            Paragraph("Team / Dept Name", styles["TableHeader"]),
            Paragraph("Members", styles["TableHeader"]),
            Paragraph("Total Dec.", styles["TableHeader"]),
            Paragraph("Approved", styles["TableHeader"]),
            Paragraph("Rejected", styles["TableHeader"]),
            Paragraph("Pending", styles["TableHeader"]),
            Paragraph("Total Appr.", styles["TableHeader"]),
            Paragraph("Appr. Rate", styles["TableHeader"]),
            Paragraph("Avg Turnaround", styles["TableHeader"]),
        ]
        table_rows = [table_headers]

        for item in items:
            avg_t = (
                f"{item.team_approval_statistics.average_turnaround_time_hours:.1f}h"
                if item.team_approval_statistics.average_turnaround_time_hours is not None
                else "N/A"
            )
            table_rows.append([
                Paragraph(item.team_name, styles["TableCell"]),
                Paragraph(str(item.number_of_members), styles["TableCellCenter"]),
                Paragraph(str(item.total_decisions), styles["TableCellCenter"]),
                Paragraph(str(item.approved_decisions), styles["TableCellCenter"]),
                Paragraph(str(item.rejected_decisions), styles["TableCellCenter"]),
                Paragraph(str(item.pending_decisions), styles["TableCellCenter"]),
                Paragraph(str(item.team_approval_statistics.total_approvals), styles["TableCellCenter"]),
                Paragraph(f"{item.team_approval_statistics.completion_rate:.1f}%", styles["TableCellCenter"]),
                Paragraph(avg_t, styles["TableCellCenter"]),
            ])

        col_widths = [134, 60, 65, 65, 65, 65, 75, 75, 110]
        data_table = Table(table_rows, colWidths=col_widths, repeatRows=1)
        data_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4338CA")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(data_table)

    doc.build(story)
    return buffer.getvalue()


# 4. AUDIT REPORT PDF GENERATOR
def generate_audit_pdf(
    items: list[AuditReportItem],
    summary: AuditReportSummary,
    filters: dict,
    user_name: str = "Administrator",
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=24,
        rightMargin=24,
        topMargin=24,
        bottomMargin=24,
    )
    styles = _get_custom_styles()
    story = []

    story.extend(_build_header_and_filters("System Audit & Compliance Activity Report", filters, user_name, styles))

    # Summary Statistics KPI Grid
    story.append(Paragraph("Audit Summary Breakdown", styles["SectionHeading"]))

    top_actions = ", ".join([f"{k}: {v}" for k, v in list(summary.actions_breakdown.items())[:4]]) or "None"
    top_entities = ", ".join([f"{k}: {v}" for k, v in list(summary.entity_types_breakdown.items())[:4]]) or "None"

    kpi_data = [
        [
            Paragraph("TOTAL AUDIT RECORDS", styles["KpiLabel"]),
            Paragraph("TOP ACTIONS BREAKDOWN", styles["KpiLabel"]),
            Paragraph("TOP ENTITY TYPES", styles["KpiLabel"]),
        ],
        [
            Paragraph(str(summary.total_audit_records), styles["KpiValue"]),
            Paragraph(top_actions, styles["TableCellCenter"]),
            Paragraph(top_entities, styles["TableCellCenter"]),
        ],
    ]
    kpi_table = Table(kpi_data, colWidths=[180, 270, 274])
    kpi_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    # Data Table
    story.append(Paragraph(f"Audit Activity Trail ({len(items)})", styles["SectionHeading"]))
    if not items:
        story.append(Paragraph("No audit logs found matching the specified criteria.", styles["EmptyNotice"]))
    else:
        table_headers = [
            Paragraph("ID", styles["TableHeader"]),
            Paragraph("Timestamp", styles["TableHeader"]),
            Paragraph("User", styles["TableHeader"]),
            Paragraph("Action", styles["TableHeader"]),
            Paragraph("Entity Type", styles["TableHeader"]),
            Paragraph("Entity ID", styles["TableHeader"]),
            Paragraph("Description", styles["TableHeader"]),
            Paragraph("IP Address", styles["TableHeader"]),
        ]
        table_rows = [table_headers]

        for item in items:
            user_str = item.user_name or f"User #{item.user_id}"
            entity_id_str = str(item.entity_id) if item.entity_id is not None else "-"
            table_rows.append([
                Paragraph(str(item.audit_id), styles["TableCellCenter"]),
                Paragraph(item.timestamp.strftime("%Y-%m-%d %H:%M:%S"), styles["TableCellCenter"]),
                Paragraph(user_str, styles["TableCell"]),
                Paragraph(item.action, styles["TableCellCenter"]),
                Paragraph(item.entity_type, styles["TableCellCenter"]),
                Paragraph(entity_id_str, styles["TableCellCenter"]),
                Paragraph(item.description, styles["TableCell"]),
                Paragraph(item.ip_address or "-", styles["TableCellCenter"]),
            ])

        col_widths = [35, 95, 95, 80, 75, 45, 224, 75]
        data_table = Table(table_rows, colWidths=col_widths, repeatRows=1)
        data_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(data_table)

    doc.build(story)
    return buffer.getvalue()
