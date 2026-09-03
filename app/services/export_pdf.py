from datetime import datetime
import io
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _get_base_styles():
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#64748B"),
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=8,
        spaceAfter=6,
    )
    cell_style = ParagraphStyle(
        "ReportCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1E293B"),
    )
    cell_bold = ParagraphStyle(
        "ReportCellBold",
        parent=cell_style,
        fontName="Helvetica-Bold",
    )
    th_style = ParagraphStyle(
        "ReportTH",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
    )
    return {
        "title": title_style,
        "subtitle": subtitle_style,
        "heading": section_heading,
        "cell": cell_style,
        "cell_bold": cell_bold,
        "th": th_style,
    }


def _build_header(elements, title: str, filters_applied: Dict[str, Any], styles):
    elements.append(Paragraph(title, styles["title"]))
    generated_text = f"Generated On: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} | Platform: Expert Decision Replay"
    elements.append(Paragraph(generated_text, styles["subtitle"]))
    elements.append(Spacer(1, 8))

    # Applied Filters Box
    active_filters = {k: v for k, v in filters_applied.items() if v is not None and v != ""}
    if active_filters:
        filter_str = ", ".join(f"<b>{k}</b>: {v}" for k, v in active_filters.items())
    else:
        filter_str = "None (All records included)"
    
    filter_p = Paragraph(f"<b>Applied Filters:</b> {filter_str}", styles["cell"])
    filter_table = Table([[filter_p]], colWidths=["100%"])
    filter_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(filter_table)
    elements.append(Spacer(1, 10))


# =============================================================================
# 1. DECISION REPORT PDF
# =============================================================================

def generate_decisions_pdf(items: List[Any], summary: Any, filters_applied: Dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=0.4 * inch,
        rightMargin=0.4 * inch,
        topMargin=0.4 * inch,
        bottomMargin=0.4 * inch,
    )
    styles = _get_base_styles()
    elements = []

    _build_header(elements, "Decisions Report", filters_applied, styles)

    # Summary Table
    elements.append(Paragraph("Summary Statistics", styles["heading"]))
    sum_data = [
        [
            Paragraph("<b>Total Decisions</b>", styles["cell"]),
            Paragraph("<b>Draft</b>", styles["cell"]),
            Paragraph("<b>Under Review</b>", styles["cell"]),
            Paragraph("<b>Approved</b>", styles["cell"]),
            Paragraph("<b>Rejected</b>", styles["cell"]),
            Paragraph("<b>Archived</b>", styles["cell"]),
        ],
        [
            Paragraph(str(getattr(summary, "total_decisions", 0)), styles["cell_bold"]),
            Paragraph(str(getattr(summary, "draft_decisions", 0)), styles["cell"]),
            Paragraph(str(getattr(summary, "under_review_decisions", 0)), styles["cell"]),
            Paragraph(str(getattr(summary, "approved_decisions", 0)), styles["cell"]),
            Paragraph(str(getattr(summary, "rejected_decisions", 0)), styles["cell"]),
            Paragraph(str(getattr(summary, "archived_decisions", 0)), styles["cell"]),
        ]
    ]
    sum_table = Table(sum_data, colWidths=[120, 110, 120, 110, 110, 110])
    sum_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F8FAFC")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(sum_table)
    elements.append(Spacer(1, 12))

    # Data Table
    elements.append(Paragraph(f"Decision Records ({len(items)} items)", styles["heading"]))
    headers = ["ID", "Title", "Category", "Status", "Created By", "Created Date", "Alts", "Apprvs", "Tags"]
    col_widths = [35, 175, 85, 75, 100, 75, 40, 45, 110]

    data = [[Paragraph(h, styles["th"]) for h in headers]]
    for item in items:
        creator = getattr(item, "creator_name", None) or f"User #{getattr(item, 'created_by', '')}"
        created_str = item.created_at.strftime("%Y-%m-%d") if hasattr(item, "created_at") and item.created_at else ""
        tags_str = ", ".join(item.tags) if hasattr(item, "tags") and item.tags else "-"
        data.append([
            Paragraph(str(item.id), styles["cell"]),
            Paragraph(item.title, styles["cell_bold"]),
            Paragraph(item.category, styles["cell"]),
            Paragraph(item.status, styles["cell"]),
            Paragraph(creator, styles["cell"]),
            Paragraph(created_str, styles["cell"]),
            Paragraph(str(getattr(item, "alternatives_count", 0)), styles["cell"]),
            Paragraph(str(getattr(item, "approvals_count", 0)), styles["cell"]),
            Paragraph(tags_str, styles["cell"]),
        ])

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            table_style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F8FAFC")))
    table.setStyle(TableStyle(table_style))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


# =============================================================================
# 2. APPROVAL REPORT PDF
# =============================================================================

def generate_approvals_pdf(items: List[Any], summary: Any, filters_applied: Dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=0.4 * inch,
        rightMargin=0.4 * inch,
        topMargin=0.4 * inch,
        bottomMargin=0.4 * inch,
    )
    styles = _get_base_styles()
    elements = []

    _build_header(elements, "Approvals Report", filters_applied, styles)

    # Summary Table
    elements.append(Paragraph("Summary Statistics", styles["heading"]))
    avg_turnaround = f"{summary.average_turnaround_time_hours} hrs" if getattr(summary, "average_turnaround_time_hours", None) is not None else "N/A"
    completion_rate = f"{getattr(summary, 'completion_rate', 0.0)}%"

    sum_data = [
        [
            Paragraph("<b>Total Approvals</b>", styles["cell"]),
            Paragraph("<b>Pending</b>", styles["cell"]),
            Paragraph("<b>Approved</b>", styles["cell"]),
            Paragraph("<b>Rejected</b>", styles["cell"]),
            Paragraph("<b>Avg Turnaround</b>", styles["cell"]),
            Paragraph("<b>Completion Rate</b>", styles["cell"]),
        ],
        [
            Paragraph(str(getattr(summary, "total_approvals", 0)), styles["cell_bold"]),
            Paragraph(str(getattr(summary, "pending_approvals", 0)), styles["cell"]),
            Paragraph(str(getattr(summary, "approved_approvals", 0)), styles["cell"]),
            Paragraph(str(getattr(summary, "rejected_approvals", 0)), styles["cell"]),
            Paragraph(avg_turnaround, styles["cell"]),
            Paragraph(completion_rate, styles["cell_bold"]),
        ]
    ]
    sum_table = Table(sum_data, colWidths=[120, 110, 110, 110, 120, 110])
    sum_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F8FAFC")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(sum_table)
    elements.append(Spacer(1, 12))

    # Data Table
    elements.append(Paragraph(f"Approval Records ({len(items)} items)", styles["heading"]))
    headers = ["ID", "Dec ID", "Decision Title", "Reviewer", "Level", "Status", "Assigned Date", "Completed Date", "Turnaround"]
    col_widths = [30, 45, 180, 110, 40, 65, 75, 75, 60]

    data = [[Paragraph(h, styles["th"]) for h in headers]]
    for item in items:
        reviewer = getattr(item, "reviewer_name", None) or f"User #{getattr(item, 'reviewer_id', '')}"
        assigned_str = item.created_at.strftime("%Y-%m-%d") if hasattr(item, "created_at") and item.created_at else ""
        completed_str = item.completed_at.strftime("%Y-%m-%d") if hasattr(item, "completed_at") and item.completed_at else "-"
        turnaround_str = f"{item.turnaround_time_hours} hrs" if getattr(item, "turnaround_time_hours", None) is not None else "-"
        dec_title = getattr(item, "decision_title", "") or f"Decision #{item.decision_id}"

        data.append([
            Paragraph(str(item.id), styles["cell"]),
            Paragraph(str(item.decision_id), styles["cell"]),
            Paragraph(dec_title, styles["cell_bold"]),
            Paragraph(reviewer, styles["cell"]),
            Paragraph(str(item.approval_level), styles["cell"]),
            Paragraph(item.status, styles["cell"]),
            Paragraph(assigned_str, styles["cell"]),
            Paragraph(completed_str, styles["cell"]),
            Paragraph(turnaround_str, styles["cell"]),
        ])

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            table_style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F8FAFC")))
    table.setStyle(TableStyle(table_style))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


# =============================================================================
# 3. TEAM REPORT PDF
# =============================================================================

def generate_teams_pdf(items: List[Any], summary: Any, filters_applied: Dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=0.4 * inch,
        rightMargin=0.4 * inch,
        topMargin=0.4 * inch,
        bottomMargin=0.4 * inch,
    )
    styles = _get_base_styles()
    elements = []

    _build_header(elements, "Team & Department Report", filters_applied, styles)

    # Summary Table
    elements.append(Paragraph("Organization Summary", styles["heading"]))
    sum_data = [
        [
            Paragraph("<b>Total Teams</b>", styles["cell"]),
            Paragraph("<b>Total Members</b>", styles["cell"]),
            Paragraph("<b>Total Decisions</b>", styles["cell"]),
            Paragraph("<b>Approved</b>", styles["cell"]),
            Paragraph("<b>Rejected</b>", styles["cell"]),
            Paragraph("<b>Pending</b>", styles["cell"]),
        ],
        [
            Paragraph(str(getattr(summary, "total_teams", 0)), styles["cell_bold"]),
            Paragraph(str(getattr(summary, "total_members", 0)), styles["cell"]),
            Paragraph(str(getattr(summary, "total_decisions", 0)), styles["cell"]),
            Paragraph(str(getattr(summary, "approved_decisions", 0)), styles["cell"]),
            Paragraph(str(getattr(summary, "rejected_decisions", 0)), styles["cell"]),
            Paragraph(str(getattr(summary, "pending_decisions", 0)), styles["cell"]),
        ]
    ]
    sum_table = Table(sum_data, colWidths=[120, 110, 120, 110, 110, 110])
    sum_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F8FAFC")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(sum_table)
    elements.append(Spacer(1, 12))

    # Data Table
    elements.append(Paragraph(f"Team Performance Breakdown ({len(items)} teams)", styles["heading"]))
    headers = ["Team / Department", "Members", "Total Decs", "Approved", "Rejected", "Pending", "Team Apprvs", "Apprv Rate", "Avg Turnaround"]
    col_widths = [140, 55, 65, 55, 55, 55, 65, 65, 80]

    data = [[Paragraph(h, styles["th"]) for h in headers]]
    for item in items:
        apprv_stats = getattr(item, "team_approval_statistics", None)
        tot_apprv = getattr(apprv_stats, "total_approvals", 0) if apprv_stats else 0
        comp_rate = f"{getattr(apprv_stats, 'completion_rate', 0.0)}%" if apprv_stats else "0.0%"
        avg_turn = f"{apprv_stats.average_turnaround_time_hours} hrs" if apprv_stats and apprv_stats.average_turnaround_time_hours is not None else "N/A"

        data.append([
            Paragraph(item.team_name, styles["cell_bold"]),
            Paragraph(str(item.member_count), styles["cell"]),
            Paragraph(str(item.total_decisions), styles["cell"]),
            Paragraph(str(item.approved_decisions), styles["cell"]),
            Paragraph(str(item.rejected_decisions), styles["cell"]),
            Paragraph(str(item.pending_decisions), styles["cell"]),
            Paragraph(str(tot_apprv), styles["cell"]),
            Paragraph(comp_rate, styles["cell"]),
            Paragraph(avg_turn, styles["cell"]),
        ])

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            table_style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F8FAFC")))
    table.setStyle(TableStyle(table_style))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


# =============================================================================
# 4. AUDIT REPORT PDF
# =============================================================================

def generate_audit_pdf(items: List[Any], summary: Any, filters_applied: Dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=0.4 * inch,
        rightMargin=0.4 * inch,
        topMargin=0.4 * inch,
        bottomMargin=0.4 * inch,
    )
    styles = _get_base_styles()
    elements = []

    _build_header(elements, "Audit & Compliance Report", filters_applied, styles)

    # Summary
    elements.append(Paragraph("Audit Summary", styles["heading"]))
    actions_breakdown = getattr(summary, "actions_breakdown", {}) or {}
    top_actions = ", ".join(f"{k}: {v}" for k, v in list(actions_breakdown.items())[:6]) or "None"

    sum_data = [
        [
            Paragraph("<b>Total Audit Logs</b>", styles["cell"]),
            Paragraph("<b>Top Actions Recorded</b>", styles["cell"]),
        ],
        [
            Paragraph(str(getattr(summary, "total_audit_logs", 0)), styles["cell_bold"]),
            Paragraph(top_actions, styles["cell"]),
        ]
    ]
    sum_table = Table(sum_data, colWidths=[150, 530])
    sum_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F8FAFC")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(sum_table)
    elements.append(Spacer(1, 12))

    # Data Table
    elements.append(Paragraph(f"Audit Trail Records ({len(items)} items)", styles["heading"]))
    headers = ["ID", "Timestamp", "User", "Action", "Entity Type", "Entity ID", "IP Address", "Description"]
    col_widths = [30, 85, 95, 60, 75, 45, 75, 215]

    data = [[Paragraph(h, styles["th"]) for h in headers]]
    for item in items:
        user_str = getattr(item, "user_name", None) or (f"User #{item.user_id}" if getattr(item, "user_id", None) else "System")
        time_str = item.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(item, "created_at") and item.created_at else ""
        ent_id = str(item.entity_id) if getattr(item, "entity_id", None) is not None else "-"
        ip_str = getattr(item, "ip_address", None) or "-"

        data.append([
            Paragraph(str(item.id), styles["cell"]),
            Paragraph(time_str, styles["cell"]),
            Paragraph(user_str, styles["cell"]),
            Paragraph(item.action, styles["cell_bold"]),
            Paragraph(item.entity_type, styles["cell"]),
            Paragraph(ent_id, styles["cell"]),
            Paragraph(ip_str, styles["cell"]),
            Paragraph(item.description, styles["cell"]),
        ])

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            table_style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F8FAFC")))
    table.setStyle(TableStyle(table_style))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
