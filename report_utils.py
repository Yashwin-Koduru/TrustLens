
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime

def build_pdf(path, title="TrustLens Demo Report", summary=None):
    c = canvas.Canvas(path, pagesize=LETTER)
    width, height = LETTER
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1*inch, height-1*inch, title)
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, height-1.3*inch, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y = height-1.7*inch
    if summary:
        c.setFont("Helvetica", 11)
        for line in summary.splitlines():
            c.drawString(1*inch, y, line[:95])
            y -= 14
            if y < 1*inch:
                c.showPage(); y = height-1*inch
    c.showPage()
    c.save()
