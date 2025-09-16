from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from io import BytesIO
from datetime import datetime
import re

# -----------------------------
# Markdown table parser
# -----------------------------
def parse_markdown_table(md_table):
    """
    Converts Markdown table text into a 2D list suitable for ReportLab Table.
    """
    lines = [line.strip() for line in md_table.split("\n") if line.strip()]
    # Remove separator line containing '---'
    lines = [line for line in lines if not re.match(r"^\|?\s*-{3,}\s*\|", line)]
    table_data = []
    for line in lines:
        row = [cell.strip() for cell in line.split("|") if cell.strip() != ""]
        if row:
            table_data.append(row)
    return table_data

# -----------------------------
# Build styled table
# -----------------------------
def build_table(table_data):
    """
    Builds a ReportLab Table with proper styling and alignment.
    Wraps text using Paragraph for multi-line cells.
    """
    num_cols = len(table_data[0])
    
    # Convert all table cells to Paragraph for proper text wrapping
    styles = getSampleStyleSheet()
    cell_style = ParagraphStyle(
        "CellStyle",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        alignment=0  # 0=left, 1=center, 2=right
    )
    table_data_paragraphs = []
    for i, row in enumerate(table_data):
        new_row = []
        for cell in row:
            new_row.append(Paragraph(cell, cell_style))
        table_data_paragraphs.append(new_row)
    
    col_widths = [max(3*cm, 12*cm//num_cols)] * num_cols  # flexible width
    tbl = Table(table_data_paragraphs, hAlign="LEFT", colWidths=col_widths)
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),  # header center
        ('ALIGN', (0,1), (-1,-1), 'LEFT'),   # body left
        ('ROWBACKGROUNDS', (1,1), (-1,-1), [colors.whitesmoke, colors.lightcyan])
    ]))
    return tbl

# -----------------------------
# Save chat report to PDF
# -----------------------------
def save_chat_report(chat_history, output_path="chat_report.pdf"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=(600, 800))
    styles = getSampleStyleSheet()
    user_style = ParagraphStyle(
        "UserStyle",
        parent=styles["Normal"],
        alignment=0,
        textColor=colors.darkblue,
        spaceAfter=6
    )
    assistant_style = ParagraphStyle(
        "AssistantStyle",
        parent=styles["Normal"],
        alignment=0,
        textColor=colors.black,
        spaceAfter=6
    )

    story = []

    # Title
    story.append(Paragraph("🛡️ SafeRideAI - Chat Report", styles['Title']))
    story.append(Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), styles['Normal']))
    story.append(Spacer(1, 12))

    for msg in chat_history:
        content = msg["content"]
        if msg["role"] == "user":
            story.append(Paragraph(f"🧑 {content}", user_style))
            story.append(Spacer(1, 6))
        else:
            # Detect Markdown tables
            table_matches = re.findall(r"\|.*\|", content)
            if table_matches:
                lines = content.split("\n")
                buffer_lines = []
                for line in lines:
                    if "|" in line:
                        buffer_lines.append(line)
                    else:
                        if buffer_lines:
                            md_table = "\n".join(buffer_lines)
                            table_data = parse_markdown_table(md_table)
                            if table_data:
                                tbl = build_table(table_data)
                                story.append(tbl)
                                story.append(Spacer(1, 12))
                            buffer_lines = []

                        if line.strip():  # normal text
                            story.append(Paragraph(f"🤖 {line.strip()}", assistant_style))
                            story.append(Spacer(1, 6))
                # Remaining buffered table
                if buffer_lines:
                    md_table = "\n".join(buffer_lines)
                    table_data = parse_markdown_table(md_table)
                    if table_data:
                        tbl = build_table(table_data)
                        story.append(tbl)
                        story.append(Spacer(1, 12))
            else:
                # No table, normal assistant text
                text = content.replace("\n", "<br/>")
                story.append(Paragraph(f"🤖 {text}", assistant_style))
                story.append(Spacer(1, 6))

    doc.build(story)
    buffer.seek(0)
    return buffer
