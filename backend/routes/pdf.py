from email.message import EmailMessage
import smtplib
from io import BytesIO
from datetime import datetime

import requests
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, EmailStr
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ..config import config

router = APIRouter()


class PDFRequest(BaseModel):
    title: str = "Trip Itinerary"
    itinerary_text: str | None = None
    itinerary_days: list[dict] = []
    destination: str | None = None
    cover_image: str | None = None
    summary: str | None = None
    overall_tips: list[str] = []


class EmailShareRequest(PDFRequest):
    email: EmailStr
    subject: str
    message: str


def _build_highlight(label, value, width, label_style, value_style):
    if not value:
        return None
    tbl = Table(
        [[Paragraph(label, label_style), Paragraph(value, value_style)]],
        colWidths=[width * 0.28, width * 0.72],
    )
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF2FF")),
                ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#C7D2FE")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C7D2FE")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return tbl


def _cover_image_story(url, width):
    if not url:
        return None
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        image = Image(BytesIO(resp.content), width=width, height=2.6 * inch)
        image.hAlign = "CENTER"
        return image
    except Exception:
        return None


def build_pdf_bytes(req: PDFRequest) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=30,
        textColor=colors.HexColor("#1F2937"),
        spaceAfter=4,
        alignment=0,
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=12,
        textColor=colors.HexColor("#6B7280"),
        spaceAfter=18,
        fontName="Helvetica",
    )
    day_heading_style = ParagraphStyle(
        "DayHeading",
        parent=styles["Heading2"],
        fontSize=18,
        textColor=colors.HexColor("#111827"),
        spaceAfter=10,
        spaceBefore=12,
        fontName="Helvetica-Bold",
    )
    segment_period = ParagraphStyle(
        "SegmentPeriod",
        parent=styles["Heading4"],
        fontSize=11,
        textColor=colors.HexColor("#6366F1"),
        fontName="Helvetica-Bold",
        spaceAfter=2,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#1F2937"),
        leading=16,
    )
    highlight_label = ParagraphStyle(
        "HighlightLabel",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#4338CA"),
        fontName="Helvetica-Bold",
    )
    highlight_value = ParagraphStyle(
        "HighlightValue",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#1F2937"),
    )

    story.append(Paragraph(req.title, title_style))
    summary_line = req.summary or f"Generated on {datetime.now().strftime('%B %d, %Y')}"
    story.append(Paragraph(summary_line, subtitle_style))

    hero = _cover_image_story(req.cover_image, doc.width)
    if hero:
        story.append(hero)
        story.append(Spacer(1, 0.2 * inch))

    if req.destination:
        story.append(Paragraph(f"Destination • <b>{req.destination}</b>", body_style))
        story.append(Spacer(1, 0.08 * inch))

    if not req.itinerary_days:
        # fallback to text-only rendering
        text = req.itinerary_text or ""
        for paragraph in text.split("\n"):
            if not paragraph.strip():
                continue
            story.append(Paragraph(paragraph.strip(), body_style))
            story.append(Spacer(1, 0.08 * inch))
    else:
        for idx, day in enumerate(req.itinerary_days, start=1):
            heading = day.get("headline") or day.get("date") or f"Day {idx}"
            story.append(Paragraph(f"Day {day.get('day', idx)} • {heading}", day_heading_style))
            if day.get("highlights"):
                story.append(Paragraph(day["highlights"], body_style))
                story.append(Spacer(1, 0.08 * inch))

            segments = []
            for seg in day.get("segments", []):
                period_para = Paragraph(seg.get("period", "Schedule"), segment_period)
                detail = Paragraph(seg.get("activity", ""), body_style)
                segments.append([period_para, detail])
            if segments:
                seg_table = Table(segments, colWidths=[doc.width * 0.25, doc.width * 0.72])
                seg_table.setStyle(
                    TableStyle(
                        [
                            ("BOX", (0, 0), (-1, -1), 0.3, colors.HexColor("#E5E7EB")),
                            ("LINEBEFORE", (1, 0), (1, -1), 0.3, colors.HexColor("#E5E7EB")),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 6),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ]
                    )
                )
                story.append(seg_table)
                story.append(Spacer(1, 0.12 * inch))

            highlight_items = [
                ("🍽 Local Bite", day.get("local_food")),
                ("🧭 Travel Sync", day.get("travel_time")),
                ("🌤 Weather", day.get("weather_note")),
                ("🛡 Safety", day.get("safety_tip")),
                ("💰 Budget", day.get("budget_tip")),
            ]
            for label, val in highlight_items:
                block = _build_highlight(label, val, doc.width, highlight_label, highlight_value)
                if block:
                    story.append(block)
                    story.append(Spacer(1, 0.08 * inch))

            if idx != len(req.itinerary_days):
                story.append(Spacer(1, 0.2 * inch))
                story.append(PageBreak())

    if req.overall_tips:
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("Pro tips", day_heading_style))
        for tip in req.overall_tips:
            story.append(Paragraph(f"• {tip}", body_style))

    story.append(Spacer(1, 0.3 * inch))
    footer = Paragraph("Safe travels! Generated by AI Travel Planner ✈️", highlight_value)
    story.append(footer)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def _send_pdf_email(req: EmailShareRequest, pdf_bytes: bytes):
    if not config.SMTP_HOST or not config.EMAIL_SENDER:
        raise HTTPException(status_code=500, detail="Email service is not configured on the server.")
    msg = EmailMessage()
    msg["Subject"] = req.subject
    msg["From"] = config.EMAIL_SENDER
    msg["To"] = req.email
    msg.set_content(req.message)
    msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename="travel-itinerary.pdf")
    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            if config.SMTP_USE_TLS:
                server.starttls()
            if config.SMTP_USERNAME:
                server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {exc}") from exc


@router.post("/generate")
def generate_pdf(req: PDFRequest):
    try:
        pdf_bytes = build_pdf_bytes(req)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=trip-itinerary.pdf"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.post("/email")
def email_pdf(req: EmailShareRequest):
    try:
        pdf_bytes = build_pdf_bytes(req)
        _send_pdf_email(req, pdf_bytes)
        return {"status": "sent"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email send failed: {str(e)}")
