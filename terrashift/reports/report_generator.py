"""Small PDF field report."""
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def make_pdf(title: str, lines: list[str]) -> bytes:
    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=letter)
    width, height = letter
    y = height - 55
    pdf.setTitle(title)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(48, y, title[:90]); y -= 30
    pdf.setFont("Helvetica", 9)
    for line in lines:
        words = str(line).split()
        current = ""
        for word in words:
            if len(current) + len(word) > 105:
                pdf.drawString(48, y, current); y -= 14; current = ""
                if y < 55:
                    pdf.showPage(); y = height - 55; pdf.setFont("Helvetica", 9)
            current += word + " "
        if current:
            pdf.drawString(48, y, current); y -= 14
        if y < 55:
            pdf.showPage(); y = height - 55; pdf.setFont("Helvetica", 9)
    pdf.save()
    return output.getvalue()
