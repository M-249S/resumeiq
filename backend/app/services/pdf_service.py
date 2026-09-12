from io import BytesIO

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate


def generate_resume_pdf(resume_text: str) -> BytesIO:
    """
    Generate a PDF from the improved resume text.
    """

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )

    styles = getSampleStyleSheet()

    story = []

    for line in resume_text.splitlines():

        line = line.strip()

        if not line:
            story.append(Paragraph("<br/>", styles["Normal"]))
            continue

        if line.startswith("# "):
            story.append(
                Paragraph(
                    f"<b><font size=18>{line[2:]}</font></b>",
                    styles["Heading1"],
                )
            )
            continue

        if line.startswith("## "):
            story.append(
                Paragraph(
                    f"<b><font size=14>{line[3:]}</font></b>",
                    styles["Heading2"],
                )
            )
            continue

        if line.startswith("### "):
            story.append(
                Paragraph(
                    f"<b>{line[4:]}</b>",
                    styles["Heading3"],
                )
            )
            continue

        if line.startswith("* "):
            story.append(
                Paragraph(
                    f"• {line[2:]}",
                    styles["Normal"],
                )
            )
            continue

        story.append(
            Paragraph(
                line,
                styles["Normal"],
            )
        )

    doc.build(story)

    buffer.seek(0)

    return buffer
