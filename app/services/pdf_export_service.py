import io
from datetime import datetime
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and print 'Page X of Y' and professional footer.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header rule & text
        self.drawString(36, self._pagesize[1] - 25, "Expert Decision Replay Platform — Official Report")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, self._pagesize[1] - 28, self._pagesize[0] - 36, self._pagesize[1] - 28)

        # Footer rule & text
        self.line(36, 30, self._pagesize[0] - 36, 30)
        footer_text = f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} | Confidential"
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawString(36, 18, footer_text)
        self.drawRightString(self._pagesize[0] - 36, 18, page_str)
        self.restoreState()


def _get_styles():
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=4,
    )
    
    subtitle_style = ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=10,
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=10,
        spaceAfter=6,
    )

    meta_label = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#334155'),
    )

    meta_val = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#475569'),
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1,  # Center
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1E293B'),
    )

    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=table_cell,
        alignment=1,
    )

    return {
        'title': title_style,
        'subtitle': subtitle_style,
        'section': section_heading,
        'meta_label': meta_label,
        'meta_val': meta_val,
        'th': table_header,
        'td': table_cell,
        'td_c': table_cell_center,
    }


def _build_metadata_box(filters: Dict[str, Any], styles: dict, doc_width: float) -> Table:
    filter_entries = []
    for k, v in filters.items():
        if v is not None and v != "":
            display_val = str(v)
            if isinstance(v, list):
                display_val = ", ".join(str(x) for x in v)
            filter_entries.append((k.replace('_', ' ').title(), display_val))
    
    if not filter_entries:
        filter_entries = [("Filters Applied", "None (All Records Included)")]

    # Split into 2-column key-value rows
    data = []
    row = []
    for label, val in filter_entries:
        row.extend([Paragraph(f"<b>{label}:</b>", styles['meta_label']), Paragraph(val, styles['meta_val'])])
        if len(row) == 4:
            data.append(row)
            row = []
    if row:
        while len(row) < 4:
            row.extend(["", ""])
        data.append(row)

    col_widths = [doc_width * 0.18, doc_width * 0.32, doc_width * 0.18, doc_width * 0.32]
    box_table = Table(data, colWidths=col_widths)
    box_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    return box_table


# =============================================================================
# 1. DECISIONS REPORT PDF
# =============================================================================

def generate_decision_report_pdf(
    items: List[dict],
    summary: dict,
    filters: Dict[str, Any],
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=40,
    )
    doc_width = landscape(letter)[0] - 72
    styles = _get_styles()
    story = []

    # Title & Metadata
    story.append(Paragraph("Decisions Summary & Detail Report", styles['title']))
    story.append(Paragraph(f"Expert Decision Replay Platform • Generated: {datetime.utcnow().strftime('%B %d, %Y %H:%M UTC')}", styles['subtitle']))
    story.append(_build_metadata_box(filters, styles, doc_width))
    story.append(Spacer(1, 10))

    # Summary Statistics Cards
    story.append(Paragraph("Executive Summary Statistics", styles['section']))
    summary_data = [
        [
            Paragraph("<b>Total Decisions</b>", styles['meta_label']),
            Paragraph("<b>Draft</b>", styles['meta_label']),
            Paragraph("<b>Under Review</b>", styles['meta_label']),
            Paragraph("<b>Approved</b>", styles['meta_label']),
            Paragraph("<b>Rejected</b>", styles['meta_label']),
            Paragraph("<b>Archived</b>", styles['meta_label']),
        ],
        [
            Paragraph(f"<font size=11 color='#1E293B'><b>{summary.get('total_decisions', 0)}</b></font>", styles['td_c']),
            Paragraph(f"<font size=11 color='#64748B'><b>{summary.get('draft_decisions', 0)}</b></font>", styles['td_c']),
            Paragraph(f"<font size=11 color='#F59E0B'><b>{summary.get('decisions_under_review', 0)}</b></font>", styles['td_c']),
            Paragraph(f"<font size=11 color='#10B981'><b>{summary.get('approved_decisions', 0)}</b></font>", styles['td_c']),
            Paragraph(f"<font size=11 color='#EF4444'><b>{summary.get('rejected_decisions', 0)}</b></font>", styles['td_c']),
            Paragraph(f"<font size=11 color='#94A3B8'><b>{summary.get('archived_decisions', 0)}</b></font>", styles['td_c']),
        ]
    ]
    card_widths = [doc_width / 6.0] * 6
    summary_table = Table(summary_data, colWidths=card_widths)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # Data Table
    story.append(Paragraph(f"Decision Records ({len(items)} items)", styles['section']))
    
    headers = [
        Paragraph("ID", styles['th']),
        Paragraph("Title", styles['th']),
        Paragraph("Category", styles['th']),
        Paragraph("Status", styles['th']),
        Paragraph("Created By", styles['th']),
        Paragraph("Created Date", styles['th']),
        Paragraph("Updated Date", styles['th']),
        Paragraph("Alts", styles['th']),
        Paragraph("Appr", styles['th']),
        Paragraph("Tags", styles['th']),
    ]
    table_data = [headers]

    for it in items:
        tags_str = ", ".join(it.get('tags', [])) if it.get('tags') else "-"
        created_str = it['created_at'].strftime('%Y-%m-%d') if isinstance(it.get('created_at'), datetime) else str(it.get('created_at', ''))[:10]
        updated_str = it['updated_at'].strftime('%Y-%m-%d') if isinstance(it.get('updated_at'), datetime) else str(it.get('updated_at', ''))[:10]

        table_data.append([
            Paragraph(str(it.get('decision_id', '')), styles['td_c']),
            Paragraph(it.get('title', ''), styles['td']),
            Paragraph(it.get('category', ''), styles['td']),
            Paragraph(it.get('status', ''), styles['td_c']),
            Paragraph(str(it.get('created_by_name') or it.get('created_by', '')), styles['td']),
            Paragraph(created_str, styles['td_c']),
            Paragraph(updated_str, styles['td_c']),
            Paragraph(str(it.get('number_of_alternatives', 0)), styles['td_c']),
            Paragraph(str(it.get('number_of_approvals', 0)), styles['td_c']),
            Paragraph(tags_str, styles['td']),
        ])

    col_widths = [
        doc_width * 0.05,
        doc_width * 0.22,
        doc_width * 0.12,
        doc_width * 0.10,
        doc_width * 0.12,
        doc_width * 0.09,
        doc_width * 0.09,
        doc_width * 0.05,
        doc_width * 0.05,
        doc_width * 0.11,
    ]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t)

    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()


# =============================================================================
# 2. APPROVALS REPORT PDF
# =============================================================================

def generate_approval_report_pdf(
    items: List[dict],
    summary: dict,
    filters: Dict[str, Any],
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=40,
    )
    doc_width = landscape(letter)[0] - 72
    styles = _get_styles()
    story = []

    # Title & Metadata
    story.append(Paragraph("Approvals Workflow & Performance Report", styles['title']))
    story.append(Paragraph(f"Expert Decision Replay Platform • Generated: {datetime.utcnow().strftime('%B %d, %Y %H:%M UTC')}", styles['subtitle']))
    story.append(_build_metadata_box(filters, styles, doc_width))
    story.append(Spacer(1, 10))

    # Summary Statistics Cards
    story.append(Paragraph("Approval Metrics & Turnaround Summary", styles['section']))
    avg_tt = summary.get('average_turnaround_time_hours')
    avg_tt_str = f"{avg_tt:.2f} hrs" if avg_tt is not None else "N/A"
    comp_rate = summary.get('approval_completion_rate', 0.0)

    summary_data = [
        [
            Paragraph("<b>Total Approvals</b>", styles['meta_label']),
            Paragraph("<b>Pending</b>", styles['meta_label']),
            Paragraph("<b>Approved</b>", styles['meta_label']),
            Paragraph("<b>Rejected</b>", styles['meta_label']),
            Paragraph("<b>Avg Turnaround</b>", styles['meta_label']),
            Paragraph("<b>Completion Rate</b>", styles['meta_label']),
        ],
        [
            Paragraph(f"<font size=11 color='#1E293B'><b>{summary.get('total_approvals', 0)}</b></font>", styles['td_c']),
            Paragraph(f"<font size=11 color='#F59E0B'><b>{summary.get('pending_approvals', 0)}</b></font>", styles['td_c']),
            Paragraph(f"<font size=11 color='#10B981'><b>{summary.get('approved_approvals', 0)}</b></font>", styles['td_c']),
            Paragraph(f"<font size=11 color='#EF4444'><b>{summary.get('rejected_approvals', 0)}</b></font>", styles['td_c']),
            Paragraph(f"<font size=11 color='#2563EB'><b>{avg_tt_str}</b></font>", styles['td_c']),
            Paragraph(f"<font size=11 color='#7C3AED'><b>{comp_rate:.1f}%</b></font>", styles['td_c']),
        ]
    ]
    card_widths = [doc_width / 6.0] * 6
    summary_table = Table(summary_data, colWidths=card_widths)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # Data Table
    story.append(Paragraph(f"Approval Records ({len(items)} items)", styles['section']))
    
    headers = [
        Paragraph("Appr ID", styles['th']),
        Paragraph("Decision ID", styles['th']),
        Paragraph("Decision Title", styles['th']),
        Paragraph("Reviewer", styles['th']),
        Paragraph("Level", styles['th']),
        Paragraph("Status", styles['th']),
        Paragraph("Assigned Date", styles['th']),
        Paragraph("Completed Date", styles['th']),
        Paragraph("Turnaround", styles['th']),
    ]
    table_data = [headers]

    for it in items:
        assigned_str = it['assigned_date'].strftime('%Y-%m-%d %H:%M') if isinstance(it.get('assigned_date'), datetime) else str(it.get('assigned_date', ''))[:16]
        completed_str = it['completed_date'].strftime('%Y-%m-%d %H:%M') if isinstance(it.get('completed_date'), datetime) else (str(it.get('completed_date', ''))[:16] if it.get('completed_date') else "-")
        tt = it.get('turnaround_time_hours')
        tt_str = f"{tt:.2f} hrs" if tt is not None else "-"

        table_data.append([
            Paragraph(str(it.get('approval_id', '')), styles['td_c']),
            Paragraph(str(it.get('decision_id', '')), styles['td_c']),
            Paragraph(it.get('decision_title', ''), styles['td']),
            Paragraph(str(it.get('reviewer_name') or it.get('reviewer_id', '')), styles['td']),
            Paragraph(str(it.get('approval_level', 1)), styles['td_c']),
            Paragraph(it.get('approval_status', ''), styles['td_c']),
            Paragraph(assigned_str, styles['td_c']),
            Paragraph(completed_str, styles['td_c']),
            Paragraph(tt_str, styles['td_c']),
        ])

    col_widths = [
        doc_width * 0.07,
        doc_width * 0.08,
        doc_width * 0.25,
        doc_width * 0.16,
        doc_width * 0.06,
        doc_width * 0.10,
        doc_width * 0.11,
        doc_width * 0.11,
        doc_width * 0.06,
    ]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t)

    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()


# =============================================================================
# 3. TEAMS REPORT PDF
# =============================================================================

def generate_team_report_pdf(
    items: List[dict],
    summary: dict,
    filters: Dict[str, Any],
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=40,
    )
    doc_width = landscape(letter)[0] - 72
    styles = _get_styles()
    story = []

    # Title & Metadata
    story.append(Paragraph("Team Activity & Approval Summary Report", styles['title']))
    story.append(Paragraph(f"Expert Decision Replay Platform • Generated: {datetime.utcnow().strftime('%B %d, %Y %H:%M UTC')}", styles['subtitle']))
    story.append(_build_metadata_box(filters, styles, doc_width))
    story.append(Spacer(1, 10))

    # Summary Statistics Cards
    story.append(Paragraph("Organization / Department Overview", styles['section']))
    summary_data = [
        [
            Paragraph("<b>Total Teams</b>", styles['meta_label']),
            Paragraph("<b>Total Members</b>", styles['meta_label']),
            Paragraph("<b>Total Decisions</b>", styles['meta_label']),
            Paragraph("<b>Total Approvals</b>", styles['meta_label']),
        ],
        [
            Paragraph(f"<font size=11 color='#1E293B'><b>{summary.get('total_teams', 0)}</b></font>", styles['td_c']),
            Paragraph(f"<font size=11 color='#2563EB'><b>{summary.get('total_members', 0)}</b></font>", styles['td_c']),
            Paragraph(f"<font size=11 color='#10B981'><b>{summary.get('total_decisions', 0)}</b></font>", styles['td_c']),
            Paragraph(f"<font size=11 color='#7C3AED'><b>{summary.get('total_approvals', 0)}</b></font>", styles['td_c']),
        ]
    ]
    card_widths = [doc_width / 4.0] * 4
    summary_table = Table(summary_data, colWidths=card_widths)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # Data Table
    story.append(Paragraph(f"Team Performance Breakdown ({len(items)} teams)", styles['section']))
    
    headers = [
        Paragraph("Team / Department", styles['th']),
        Paragraph("Members", styles['th']),
        Paragraph("Total Dec.", styles['th']),
        Paragraph("Approved Dec.", styles['th']),
        Paragraph("Rejected Dec.", styles['th']),
        Paragraph("Pending Dec.", styles['th']),
        Paragraph("Total Appr.", styles['th']),
        Paragraph("Appr. Approved", styles['th']),
        Paragraph("Appr. Rejected", styles['th']),
        Paragraph("Appr. Pending", styles['th']),
        Paragraph("Avg TT", styles['th']),
    ]
    table_data = [headers]

    for it in items:
        app_stats = it.get('team_approval_statistics', {})
        avg_tt = app_stats.get('average_turnaround_time_hours')
        avg_tt_str = f"{avg_tt:.2f}h" if avg_tt is not None else "-"

        table_data.append([
            Paragraph(it.get('team_name', 'General'), styles['td']),
            Paragraph(str(it.get('number_of_members', 0)), styles['td_c']),
            Paragraph(str(it.get('total_decisions', 0)), styles['td_c']),
            Paragraph(str(it.get('approved_decisions', 0)), styles['td_c']),
            Paragraph(str(it.get('rejected_decisions', 0)), styles['td_c']),
            Paragraph(str(it.get('pending_decisions', 0)), styles['td_c']),
            Paragraph(str(app_stats.get('total_approvals', 0)), styles['td_c']),
            Paragraph(str(app_stats.get('approved_approvals', 0)), styles['td_c']),
            Paragraph(str(app_stats.get('rejected_approvals', 0)), styles['td_c']),
            Paragraph(str(app_stats.get('pending_approvals', 0)), styles['td_c']),
            Paragraph(avg_tt_str, styles['td_c']),
        ])

    col_widths = [
        doc_width * 0.18,
        doc_width * 0.08,
        doc_width * 0.08,
        doc_width * 0.09,
        doc_width * 0.09,
        doc_width * 0.09,
        doc_width * 0.08,
        doc_width * 0.08,
        doc_width * 0.08,
        doc_width * 0.08,
        doc_width * 0.07,
    ]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t)

    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()


# =============================================================================
# 4. AUDIT REPORT PDF
# =============================================================================

def generate_audit_report_pdf(
    items: List[dict],
    summary: dict,
    filters: Dict[str, Any],
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=40,
    )
    doc_width = landscape(letter)[0] - 72
    styles = _get_styles()
    story = []

    # Title & Metadata
    story.append(Paragraph("System Audit & Compliance Activity Report", styles['title']))
    story.append(Paragraph(f"Expert Decision Replay Platform • Generated: {datetime.utcnow().strftime('%B %d, %Y %H:%M UTC')} • Administrator Confidential", styles['subtitle']))
    story.append(_build_metadata_box(filters, styles, doc_width))
    story.append(Spacer(1, 10))

    # Summary Statistics Cards
    story.append(Paragraph("Audit Event Summary", styles['section']))
    summary_data = [
        [
            Paragraph("<b>Total Events</b>", styles['meta_label']),
            Paragraph("<b>Top Actions</b>", styles['meta_label']),
            Paragraph("<b>Top Entities</b>", styles['meta_label']),
        ],
        [
            Paragraph(f"<font size=11 color='#1E293B'><b>{summary.get('total_events', 0)}</b></font>", styles['td_c']),
            Paragraph(", ".join([f"{k}: {v}" for k, v in list(summary.get('action_breakdown', {}).items())[:4]]) or "None", styles['td']),
            Paragraph(", ".join([f"{k}: {v}" for k, v in list(summary.get('entity_breakdown', {}).items())[:4]]) or "None", styles['td']),
        ]
    ]
    card_widths = [doc_width * 0.2, doc_width * 0.4, doc_width * 0.4]
    summary_table = Table(summary_data, colWidths=card_widths)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # Data Table
    story.append(Paragraph(f"Audit Trail Records ({len(items)} events)", styles['section']))
    
    headers = [
        Paragraph("ID", styles['th']),
        Paragraph("Timestamp", styles['th']),
        Paragraph("User", styles['th']),
        Paragraph("Action", styles['th']),
        Paragraph("Entity", styles['th']),
        Paragraph("Entity ID", styles['th']),
        Paragraph("Description", styles['th']),
        Paragraph("IP Address", styles['th']),
    ]
    table_data = [headers]

    for it in items:
        ts_str = it['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(it.get('timestamp'), datetime) else str(it.get('timestamp', ''))[:19]
        user_str = it.get('user_name') or it.get('user_email') or (f"User #{it['user_id']}" if it.get('user_id') else "System")

        table_data.append([
            Paragraph(str(it.get('id', '')), styles['td_c']),
            Paragraph(ts_str, styles['td_c']),
            Paragraph(user_str, styles['td']),
            Paragraph(it.get('action', ''), styles['td_c']),
            Paragraph(it.get('entity_type', ''), styles['td_c']),
            Paragraph(str(it.get('entity_id', '') or '-'), styles['td_c']),
            Paragraph(it.get('description', ''), styles['td']),
            Paragraph(str(it.get('ip_address', '') or '-'), styles['td_c']),
        ])

    col_widths = [
        doc_width * 0.05,
        doc_width * 0.13,
        doc_width * 0.14,
        doc_width * 0.09,
        doc_width * 0.09,
        doc_width * 0.06,
        doc_width * 0.32,
        doc_width * 0.12,
    ]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t)

    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()
