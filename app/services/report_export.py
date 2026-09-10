from io import BytesIO
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)


# ============================================================
# COMMON HELPERS
# ============================================================

def format_value(value):
    """Convert values into export-friendly text."""
    if value is None:
        return ""

    if hasattr(value, "value"):
        return str(value.value)

    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")

    return str(value)


def create_excel_workbook(title, headers, rows):
    """
    Create an Excel workbook containing report data.
    Returns BytesIO containing the .xlsx file.
    """

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = title[:31]

    # Title
    worksheet.append([title])

    title_cell = worksheet.cell(row=1, column=1)
    title_cell.font = Font(
        bold=True,
        size=14,
    )

    # Generated date
    worksheet.append(
        [
            "Generated Date",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ]
    )

    worksheet.append([])

    # Headers
    worksheet.append(headers)

    header_row = worksheet.max_row

    for cell in worksheet[header_row]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(
            horizontal="center"
        )

    # Data
    for row in rows:
        worksheet.append(
            [
                format_value(value)
                for value in row
            ]
        )

    # Column widths
    for column_cells in worksheet.columns:
        max_length = 0

        for cell in column_cells:
            value = format_value(cell.value)

            if len(value) > max_length:
                max_length = len(value)

        column_letter = column_cells[0].column_letter

        worksheet.column_dimensions[
            column_letter
        ].width = min(
            max(max_length + 2, 12),
            40,
        )

    worksheet.freeze_panes = f"A{header_row + 1}"

    output = BytesIO()

    workbook.save(output)

    output.seek(0)

    return output


def create_pdf_document(title):
    """
    Create a landscape A4 PDF document.
    Returns document and BytesIO output.
    """

    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )

    styles = getSampleStyleSheet()

    return output, document, styles


def build_pdf(
    title,
    headers,
    rows,
    summary=None,
    filters=None,
):
    """
    Generate a professional PDF report.
    Returns BytesIO containing the PDF.
    """

    output, document, styles = create_pdf_document(
        title
    )

    story = []

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    story.append(
        Paragraph(
            title,
            styles["Title"],
        )
    )

    story.append(
        Paragraph(
            "Generated: "
            + datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 8))

    # --------------------------------------------------------
    # Filters
    # --------------------------------------------------------

    if filters:
        story.append(
            Paragraph(
                "<b>Filters</b>",
                styles["Heading3"],
            )
        )

        filter_rows = []

        for key, value in filters.items():
            if value is not None:
                filter_rows.append(
                    [
                        str(key),
                        format_value(value),
                    ]
                )

        if filter_rows:
            filter_table = Table(
                filter_rows,
                colWidths=[
                    45 * mm,
                    90 * mm,
                ],
            )

            filter_table.setStyle(
                TableStyle(
                    [
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
                            (0, -1),
                            "Helvetica-Bold",
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP",
                        ),
                    ]
                )
            )

            story.append(filter_table)
            story.append(Spacer(1, 8))

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    if summary:
        story.append(
            Paragraph(
                "<b>Summary</b>",
                styles["Heading3"],
            )
        )

        summary_rows = []

        for key, value in summary.items():
            summary_rows.append(
                [
                    str(key),
                    format_value(value),
                ]
            )

        summary_table = Table(
            summary_rows,
            colWidths=[
                60 * mm,
                40 * mm,
            ],
        )

        summary_table.setStyle(
            TableStyle(
                [
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
                        (0, -1),
                        "Helvetica-Bold",
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                ]
            )
        )

        story.append(summary_table)
        story.append(Spacer(1, 10))

    # --------------------------------------------------------
    # Data
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "<b>Report Data</b>",
            styles["Heading3"],
        )
    )

    pdf_rows = [
        [
            Paragraph(
                f"<b>{format_value(header)}</b>",
                styles["Normal"],
            )
            for header in headers
        ]
    ]

    for row in rows:
        pdf_rows.append(
            [
                Paragraph(
                    format_value(value),
                    styles["Normal"],
                )
                for value in row
            ]
        )

    table = Table(
        pdf_rows,
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, 0),
                    "CENTER",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7,
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

    # --------------------------------------------------------
    # Build PDF
    # --------------------------------------------------------

    document.build(story)

    output.seek(0)

    return output