from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont

# NOTE: Standard ReportLab fonts do NOT support Burmese characters.
# For a production Myanmar version, you would register a .ttf font like 'Pyidaungsu' here.
# For this prototype, we assume English text to avoid complex font setup.


def generate_lecture_pdf(lecture):
    """
    Generates a PDF buffer containing the lecture summary and transcript.
    """
    buffer = BytesIO()

    # Setup the Document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
        title=f"Notes: {lecture.title}",
    )

    Story = []
    styles = getSampleStyleSheet()

    # --- Styles ---
    # Title Style (Emerald Green)
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.HexColor("#059669"),
        alignment=1,  # Center
    )

    # Heading Style
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=20,
        spaceAfter=12,
        textColor=colors.HexColor("#1e293b"),
        borderPadding=5,
        borderColor=colors.HexColor("#e2e8f0"),
        borderWidth=0,
        borderBottomWidth=1,
    )

    # Body Text
    body_style = styles["Normal"]
    body_style.fontSize = 10
    body_style.leading = 14
    body_style.spaceAfter = 10

    # --- Content Construction ---

    # 1. Title
    Story.append(Paragraph(lecture.title, title_style))

    # 2. Metadata / Savings
    meta_text = f"<b>Data Saved:</b> {lecture.data_saved_percentage}% | <b>Original:</b> {lecture.original_size_mb}MB"
    Story.append(
        Paragraph(
            meta_text,
            ParagraphStyle(
                "Meta", parent=body_style, alignment=1, textColor=colors.gray
            ),
        )
    )
    Story.append(Spacer(1, 20))

    # 3. AI Summary Section
    Story.append(Paragraph("AI Study Guide", heading_style))

    # Clean up text for PDF (ReportLab uses <br/> for newlines)
    clean_summary = lecture.summary.replace("\n", "<br/>")
    Story.append(Paragraph(clean_summary, body_style))

    Story.append(Spacer(1, 20))

    # 4. Transcript Section
    Story.append(Paragraph("Full Transcript", heading_style))

    clean_transcript = lecture.transcript.replace("\n", "<br/>")
    Story.append(Paragraph(clean_transcript, body_style))

    # Build
    doc.build(Story)
    buffer.seek(0)
    return buffer
