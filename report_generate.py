import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO
import pandas as pd
from db_utils import fetch_data  # Your DB function


def generate_report(report_type="last_24h", output_path="report.pdf"):
    """
    Generate a PDF report for SafeRideAI detections.
    Supports standard reports (last 24h, weekly, monthly, accident, helmet).
    """

    # -----------------------
    # Title mapping
    # -----------------------
    title_mapping = {
        "last_24h": "📊 SafeRideAI Report - Last 24 Hours",
        "weekly": "📊 SafeRideAI Report - Weekly Summary",
        "monthly": "📊 SafeRideAI Report - Monthly Summary",
        "accident": "🚨 Accident Report",
        "helmet": "🪖 Helmet Violation Report"
    }
    title = title_mapping.get(report_type, "📝 SafeRideAI Report")

    # -----------------------
    # Build PDF
    # -----------------------
    doc = SimpleDocTemplate(output_path, title=title)
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles['Title']), Spacer(1, 20)]

    # -----------------------
    # Fetch data
    # -----------------------
    query_dict = {
        "last_24h": "SELECT * FROM detections WHERE created_at >= NOW() - INTERVAL '24 HOURS'",
        "weekly": "SELECT * FROM detections WHERE created_at >= NOW() - INTERVAL '7 DAYS'",
        "monthly": "SELECT * FROM detections WHERE created_at >= NOW() - INTERVAL '30 DAYS'",
        "accident": "SELECT * FROM detections WHERE class ILIKE '%Accident%'",
        "helmet": "SELECT * FROM detections WHERE class ILIKE '%Without Helmet%'"
    }
    query = query_dict.get(report_type)
    df = fetch_data(query)

    # -----------------------
    # Build report content
    # -----------------------
    if df.empty:
        story.append(Paragraph("✅ No records found for this report.", styles['Normal']))
    else:
        # Summary
        total = len(df)
        accident_count = df['class'].str.contains("Accident", case=False).sum()
        helmet_count = df['class'].str.contains("Without Helmet", case=False).sum()
        summary = f"""
        In the selected period, a total of <b>{total}</b> detections were recorded.<br/>
        Out of these, <b>{accident_count}</b> were accidents and <b>{helmet_count}</b> were helmet violations.<br/>
        """
        story.append(Paragraph(summary, styles['Normal']))
        story.append(Spacer(1, 20))

        # Table
        class_counts = df['class'].value_counts().reset_index()
        class_counts.columns = ["Class", "Count"]
        table_data = [["Class", "Count"]] + class_counts.values.tolist()
        table = Table(table_data, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(table)
        story.append(Spacer(1, 20))

        # Chart
        fig, ax = plt.subplots()
        class_counts.set_index("Class")["Count"].plot(kind="bar", ax=ax)
        plt.title("Detections by Class")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        img_buf = BytesIO()
        plt.savefig(img_buf, format="png")
        plt.close(fig)
        img_buf.seek(0)
        story.append(Image(img_buf, width=400, height=200))
        story.append(Spacer(1, 20))

    doc.build(story)
    return output_path
