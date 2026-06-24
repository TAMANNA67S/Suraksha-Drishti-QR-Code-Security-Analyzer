# reports.py — Professional PDF Report Generator
# LOCATION: app/reports.py  ← must be in same folder as main.py

import logging
from pathlib import Path
from datetime import datetime
from fpdf import FPDF

logger = logging.getLogger(__name__)

# =========================
# REPORT DIRECTORY (resolves to project_root/reports/)
# =========================
REPORT_DIR = Path(__file__).parent.parent / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# CUSTOM PDF CLASS
# =========================
class PDFReport(FPDF):
    """Branded PDF with dark-navy header and cyber-blue accents."""

    def header(self):
        self.set_fill_color(10, 15, 31)       # Dark Navy
        self.set_text_color(0, 255, 255)      # Cyber Blue
        self.set_font("Arial", "B", 14)
        self.cell(0, 12, "SURAKSHA DRISHTI — Security Analysis Report",
                  ln=True, align="C", fill=True)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10,
                  f"Page {self.page_no()}  |  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                  align="C")

    def section_title(self, title: str):
        self.set_fill_color(20, 30, 60)
        self.set_text_color(0, 220, 220)
        self.set_font("Arial", "B", 11)
        self.cell(0, 9, title, ln=True, fill=True)
        self.set_text_color(30, 30, 30)
        self.set_font("Arial", "", 11)
        self.ln(2)

    def body_line(self, text: str):
        self.set_font("Arial", "", 11)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 8, text)

    def colored_score(self, risk_score: int, risk_category: str):
        if risk_score <= 30:
            self.set_text_color(0, 180, 0)       # Green
        elif risk_score <= 60:
            self.set_text_color(220, 150, 0)     # Amber
        else:
            self.set_text_color(200, 0, 0)       # Red
        self.set_font("Arial", "B", 13)
        self.cell(0, 10,
                  f"Risk Score: {risk_score}/100  |  Category: {risk_category}",
                  ln=True)
        self.set_text_color(30, 30, 30)
        self.set_font("Arial", "", 11)
        self.ln(3)


# =========================
# PUBLIC API — called from main.py
# =========================
def generate_report(scan_data: dict, filename: str = None) -> str:
    """
    Generates a PDF security report from scan_data dict.
    """
    try:
        if filename is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Report_{ts}.pdf"

        file_path = REPORT_DIR / Path(filename).name

        pdf = PDFReport()
        pdf.add_page()

        # ── Scan Overview ──────────────────────────────────────────────
        pdf.section_title("  Scan Overview")
        pdf.body_line(f"Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        pdf.body_line(f"URL       : {scan_data.get('url', 'N/A')}")
        pdf.ln(3)

        # ── Risk Score ────────────────────────────────────────────────
        pdf.section_title("  Risk Assessment")
        pdf.colored_score(
            scan_data.get("risk_score", 0),
            scan_data.get("risk_category", "Unknown")
        )

        # ── Risk Reasons ─────────────────────────────────────────────
        pdf.section_title("  Identified Risk Factors")
        reasons = scan_data.get("reasons", [])
        if reasons:
            for reason in reasons:
                pdf.body_line(f"  •  {reason}")
        else:
            pdf.body_line("  No suspicious indicators detected.")
        pdf.ln(4)

        # ── Recommendations ───────────────────────────────────────────
        pdf.section_title("  Security Recommendations")
        recommendations = [
            "Avoid clicking URLs from unknown or untrusted QR codes.",
            "Verify the domain carefully before entering credentials.",
            "Enable two-factor authentication (2FA) on all accounts.",
            "Report phishing URLs to your IT / security team.",
            "Use a reputable URL scanner before visiting flagged links.",
        ]
        for rec in recommendations:
            pdf.body_line(f"  •  {rec}")

        pdf.output(str(file_path))
        logger.info(f"PDF report saved: {file_path}")
        return str(file_path)

    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        return None
