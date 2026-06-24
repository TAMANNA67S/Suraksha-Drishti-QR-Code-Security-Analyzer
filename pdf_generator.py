
import logging
from pathlib import Path
from datetime import datetime
from fpdf import FPDF

logger = logging.getLogger(__name__)

REPORT_DIR = Path(__file__).parent.parent / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


class SecurityReport(FPDF):
    """Extended branded PDF with full header, footer, and section helpers."""

    def header(self):
        self.set_fill_color(10, 15, 31)
        self.set_text_color(0, 255, 255)
        self.set_font("Arial", "B", 16)
        self.cell(0, 14, "SURAKSHA DRISHTI | Security Analysis", ln=True, align="C", fill=True)
        self.set_draw_color(0, 220, 220)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}  |  Confidential Security Report", align="C")

    def chapter_title(self, title: str):
        self.set_fill_color(15, 25, 55)
        self.set_text_color(0, 210, 210)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, f"  {title}", ln=True, fill=True)
        self.ln(2)

    def body_text(self, text: str, indent: int = 4):
        self.set_font("Arial", "", 11)
        self.set_text_color(30, 30, 30)
        self.set_x(self.get_x() + indent)
        self.multi_cell(0, 8, text)

    def risk_badge(self, score: int, category: str):
        color_map = {
            "Safe":      (0, 160, 0),
            "Moderate":  (200, 130, 0),
            "Dangerous": (200, 0, 0),
        }
        r, g, b = color_map.get(category, (80, 80, 80))
        self.set_fill_color(r, g, b)
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 13)
        self.cell(0, 12, f"  Risk Score: {score}/100   |   {category.upper()}",
                  ln=True, fill=True, align="C")
        self.ln(4)
        self.set_text_color(30, 30, 30)


def generate_pdf_report(
    url: str,
    risk_score: int,
    risk_category: str,
    reasons: list,
    recommendations: list = None,
) -> str:
    """
    Generates a full-featured branded PDF report.
    Returns absolute path of saved file, or None on failure.
    """
    if recommendations is None:
        recommendations = [
            "Do not enter personal or financial credentials on this URL.",
            "Verify the domain with your IT or security team.",
            "Enable two-factor authentication on all accounts.",
            "Report phishing links to your organisation's helpdesk.",
            "Use a reputable URL scanner for further verification.",
        ]

    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = REPORT_DIR / f"FullReport_{ts}.pdf"

        pdf = SecurityReport()
        pdf.add_page()


        pdf.chapter_title("Scan Overview")
        pdf.body_text(f"Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        pdf.body_text(f"URL       : {url}")
        pdf.ln(4)

        
        pdf.chapter_title("Risk Assessment")
        pdf.risk_badge(risk_score, risk_category)

        
        pdf.chapter_title("Identified Risk Factors")
        if reasons:
            for r in reasons:
                pdf.body_text(f"• {r}")
        else:
            pdf.body_text("No suspicious indicators detected.")
        pdf.ln(4)

        pdf.chapter_title("Security Recommendations")
        for rec in recommendations:
            pdf.body_text(f"• {rec}")

        pdf.output(str(file_path))
        logger.info(f"Full PDF report saved: {file_path}")
        return str(file_path)

    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        return None
