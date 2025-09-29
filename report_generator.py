import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import sys
import os

def generate_pdf(csv_file):
    df = pd.read_csv(csv_file)

    # -------------------
    # Compute stats
    # -------------------
    avg_angle = df["angle_deg"].mean()
    max_angle = df["angle_deg"].max()
    min_angle = df["angle_deg"].min()

    overextension = (df["risk"] == "Overextension risk").sum()
    highflexion = (df["risk"] == "High flexion risk").sum()

    # Phase summary
    phase_summary = df.groupby("phase")["angle_deg"].agg(["mean", "max", "min"]).round(1)

    # -------------------
    # Plot
    # -------------------
    plt.figure(figsize=(10, 4))
    plt.plot(df["timestamp"], df["angle_deg"], label="Knee Angle", color="blue")
    plt.xlabel("Time (s)")
    plt.ylabel("Angle (deg)")
    plt.title("Knee Angle Over Time")
    plt.legend()
    plot_file = csv_file.replace(".csv", "_angle.png")
    plt.savefig(plot_file)
    plt.close()

    # -------------------
    # PDF setup
    # -------------------
    pdf_file = csv_file.replace(".csv", "_report.pdf")
    doc = SimpleDocTemplate(pdf_file)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SectionHeader", fontSize=14, spaceAfter=10, textColor=colors.darkblue, leading=16))

    story = []

    # Title
    story.append(Paragraph("🚴 Cycling Biomechanics Report", styles["Title"]))
    story.append(Spacer(1, 20))

    # Session Info
    story.append(Paragraph("<b>Session Information</b>", styles["SectionHeader"]))
    story.append(Paragraph(f"File: {os.path.basename(csv_file)}", styles["Normal"]))
    story.append(Paragraph(f"Total records: {len(df)}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Key Stats Table
    story.append(Paragraph("<b>Key Knee Angle Statistics</b>", styles["SectionHeader"]))
    table_data = [
        ["Metric", "Value"],
        ["Average Knee Angle", f"{avg_angle:.1f}°"],
        ["Maximum Knee Angle", f"{max_angle:.1f}°"],
        ["Minimum Knee Angle", f"{min_angle:.1f}°"],
        ["Overextension Risk Events", overextension],
        ["High Flexion Risk Events", highflexion],
    ]
    table = Table(table_data, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))

    # Phase Summary
    story.append(Paragraph("<b>Phase-wise Statistics</b>", styles["SectionHeader"]))
    phase_data = [["Phase", "Mean", "Max", "Min"]]
    for phase, row in phase_summary.iterrows():
        phase_data.append([phase, row["mean"], row["max"], row["min"]])
    phase_table = Table(phase_data, hAlign="LEFT")
    phase_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    story.append(phase_table)
    story.append(Spacer(1, 20))

    # Add Plot
    story.append(Paragraph("<b>Knee Angle Over Time</b>", styles["SectionHeader"]))
    story.append(Image(plot_file, width=500, height=200))

    # Save PDF
    doc.build(story)
    print(f"✅ Structured PDF generated: {pdf_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python report_generator.py <session.csv>")
    else:
        generate_pdf(sys.argv[1])
