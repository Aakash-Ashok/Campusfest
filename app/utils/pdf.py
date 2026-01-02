from reportlab.lib import colors
from django.utils.timezone import now

PRIMARY = colors.HexColor("#1f2937")
ACCENT = colors.HexColor("#2563eb")
MUTED = colors.HexColor("#6b7280")


def draw_header(p, width, title, subtitle=None):
    p.setFont("Times-Bold", 18)
    p.setFillColor(PRIMARY)
    p.drawCentredString(width / 2, 800, title)

    if subtitle:
        p.setFont("Times-Italic", 11)
        p.setFillColor(MUTED)
        p.drawCentredString(width / 2, 780, subtitle)

    p.setStrokeColor(MUTED)
    p.line(60, 760, width - 60, 760)


def draw_footer(p, width):
    p.setFont("Times-Italic", 9)
    p.setFillColor(MUTED)
    p.drawCentredString(
        width / 2, 40,
        f"Generated on {now().strftime('%d %B %Y')} | Campus Fest Management System"
    )
