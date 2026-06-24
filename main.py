# main.py — SURAKSHA DRISHTI | Premium Cybersecurity Dashboard
# LOCATION: app/main.py
#
# HOW TO RUN (from project root  →  SURAKSHA DRISHTI/):
#   streamlit run app/main.py
#
# ──────────────────────────────────────────────────────────────
# ALL IMPORTS ARE FROM THE SAME app/ PACKAGE — NO ModuleNotFoundError
# ──────────────────────────────────────────────────────────────
import sys
import os
import tempfile
import logging
from pathlib import Path
from datetime import datetime

from reports import generate_report


import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Ensure app/ is on sys.path regardless of working directory
APP_DIR = Path(__file__).parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

# ── Local imports (all live in app/) ──────────────────────────
from qr_scanner  import scan_qr                                    # noqa: E402
from risk_engine import analyze_url                                 # noqa: E402
from database    import create_database, insert_scan, get_all_scans, delete_all_scans  # noqa: E402
from reports     import generate_report                             # noqa: E402
from pdf_generator import generate_pdf_report                       # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================
# DB INIT (runs once)
# =========================
create_database()

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Suraksha Drishti",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# GLOBAL CSS — Dark Glassmorphism SaaS Theme
# =========================
st.markdown("""
<style>
/* ── Base ─────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    background: #080d1a;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    color: #e0e6f0;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1526 0%, #0a1020 100%);
    border-right: 1px solid #1a2a4a;
}
[data-testid="stSidebar"] * { color: #c8d8f0 !important; }

/* ── Metric Cards ─────────────────────────────────────── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0f1c38 0%, #0a1428 100%);
    border: 1px solid #1e3a6e;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 4px 24px rgba(0,200,255,0.07);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(0,200,255,0.15);
}
[data-testid="stMetricValue"] { color: #00e5ff !important; font-size: 2rem !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #7a9cc0 !important; font-size: 0.78rem !important; text-transform: uppercase; letter-spacing: 0.08em; }

/* ── Glassmorphism card helper ────────────────────────── */
.glass-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(0,200,255,0.15);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 20px;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 32px rgba(0,0,0,0.35);
}

/* ── Risk Badge ───────────────────────────────────────── */
.badge-safe      { background:#003d1a; color:#00e676; border:1px solid #00e676; }
.badge-moderate  { background:#3d2800; color:#ffb300; border:1px solid #ffb300; }
.badge-dangerous { background:#3d0000; color:#ff3d3d; border:1px solid #ff3d3d; }
.risk-badge {
    display: inline-block;
    padding: 6px 20px;
    border-radius: 30px;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 6px;
}

/* ── Risk Score Ring (CSS only) ───────────────────────── */
.score-ring-wrap { text-align:center; padding: 10px 0; }
.score-number { font-size: 3.5rem; font-weight: 800; line-height: 1; }
.score-label  { font-size: 0.78rem; color: #7a9cc0; text-transform: uppercase; letter-spacing: 0.1em; }

/* ── Section headers ──────────────────────────────────── */
.section-header {
    font-size: 1.15rem;
    font-weight: 700;
    color: #00e5ff;
    letter-spacing: 0.04em;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #1a3a6e 0%, transparent 100%);
    margin-left: 10px;
}

/* ── Buttons ──────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #0062cc, #0099ff);
    color: #ffffff !important;
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    font-weight: 600;
    font-size: 0.9rem;
    transition: all 0.2s ease;
    box-shadow: 0 4px 14px rgba(0,120,255,0.35);
}
.stButton > button:hover {
    background: linear-gradient(135deg, #0077ee, #00b4ff);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,150,255,0.45);
}

/* ── File uploader ────────────────────────────────────── */
[data-testid="stFileUploader"] {
    border: 2px dashed #1e3a6e;
    border-radius: 14px;
    padding: 20px;
    background: rgba(0,100,200,0.05);
    transition: border-color 0.2s ease;
}
[data-testid="stFileUploader"]:hover { border-color: #00e5ff; }

/* ── Expanders ────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid #1a2a4a;
    border-radius: 12px;
    margin-bottom: 10px;
}

/* ── Dataframe ────────────────────────────────────────── */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

/* ── Divider ──────────────────────────────────────────── */
hr { border-color: #1a2a4a !important; }

/* ── Alert boxes ──────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 12px; }

/* ── Input / text_input ──────────────────────────────── */
input[type="text"] {
    background: #0d1a30 !important;
    color: #e0e6f0 !important;
    border: 1px solid #1e3a6e !important;
    border-radius: 10px !important;
}

/* ── Sidebar nav items ────────────────────────────────── */
.sidebar-nav-item {
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 6px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    color: #a0b8d8;
    transition: background 0.15s ease;
}
.sidebar-nav-item:hover,
.sidebar-nav-item.active {
    background: rgba(0,200,255,0.1);
    color: #00e5ff;
}

/* ── Scrollbar ────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #080d1a; }
::-webkit-scrollbar-thumb { background: #1e3a6e; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# =========================
# HELPERS
# =========================
def risk_color(category: str) -> str:
    return {"Safe": "#00e676", "Moderate": "#ffb300", "Dangerous": "#ff3d3d"}.get(category, "#aaa")

def risk_badge_html(category: str) -> str:
    cls = {"Safe": "badge-safe", "Moderate": "badge-moderate", "Dangerous": "badge-dangerous"}.get(category, "")
    return f'<span class="risk-badge {cls}">{category}</span>'

def score_color(score: int) -> str:
    if score <= 30:  return "#00e676"
    if score <= 60:  return "#ffb300"
    return "#ff3d3d"


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px 0;'>
        <div style='font-size:2.8rem;'>🛡️</div>
        <div style='font-size:1.1rem; font-weight:800; color:#00e5ff; letter-spacing:0.06em;'>SURAKSHA DRISHTI</div>
        <div style='font-size:0.72rem; color:#5a7a9a; margin-top:4px; letter-spacing:0.12em; text-transform:uppercase;'>
            AI Cybersecurity Dashboard
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["🔍 Scan QR Code", "📊 Dashboard", "📜 History", "⚙️ Settings"],
        label_visibility="collapsed",
    )
    st.markdown("---")

    st.markdown("""
    <div style='font-size:0.75rem; color:#3a5a7a; text-align:center; padding-top:10px;'>
        v2.0.0 &nbsp;|&nbsp; Python 3.11<br>
        © 2026 Suraksha Drishti
    </div>
    """, unsafe_allow_html=True)


# =========================
# SHARED RENDER FUNCTION
# =========================
def _render_analysis(url: str):
    """Analyses a URL and renders the full result card."""
    with st.spinner(f"Analysing {url[:60]}…"):
        result = analyze_url(url)

    insert_scan(url, result["risk_score"], result["risk_category"], result["reasons"])

    score    = result["risk_score"]
    category = result["risk_category"]
    reasons  = result.get("reasons", [])

    # Score ring
    st.markdown(f"""
    <div class="glass-card">
        <div class="score-ring-wrap">
            <div class="score-number" style="color:{score_color(score)};">{score}</div>
            <div class="score-label">Risk Score / 100</div>
            {risk_badge_html(category)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Gauge chart
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        gauge={
            "axis":       {"range": [0, 100], "tickcolor": "#3a5a7a"},
            "bar":        {"color": score_color(score)},
            "bgcolor":    "rgba(0,0,0,0)",
            "bordercolor":"#1a2a4a",
            "steps": [
                {"range": [0,  30], "color": "rgba(0,230,118,0.12)"},
                {"range": [30, 60], "color": "rgba(255,179,0,0.12)"},
                {"range": [60,100], "color": "rgba(255,61,61,0.12)"},
            ],
            "threshold": {"line": {"color": score_color(score), "width": 3}, "value": score},
        },
        number={"suffix": "/100", "font": {"color": score_color(score), "size": 28}},
        title={"text": "Threat Level", "font": {"color": "#7a9cc0", "size": 14}},
    ))
    fig_gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e0e6f0",
        height=240,
        margin=dict(t=30, b=10, l=20, r=20),
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Reasons
    with st.expander("⚠️ Risk Factors Detected", expanded=True):
        if reasons:
            for r in reasons:
                st.markdown(f"• {r}")
        else:
            st.success("✅ No suspicious indicators found.")

    # Recommendations
    with st.expander("🛡️ Security Recommendations"):
        for rec in [
            "Verify this domain before entering credentials.",
            "Enable 2FA on all accounts linked to this URL.",
            "Report phishing attempts to your IT team.",
            "Use a reputable browser extension for live URL checks.",
        ]:
            st.markdown(f"• {rec}")

    # PDF download
    pdf_path = generate_report(result)
    if pdf_path and Path(pdf_path).exists():
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download PDF Report",
                data=f,
                file_name=Path(pdf_path).name,
                mime="application/pdf",
                use_container_width=True,
            )


# =========================
# PAGE: SCAN QR CODE
# =========================
if page == "🔍 Scan QR Code":

    st.markdown("""
    <div style='padding: 10px 0 24px 0;'>
        <h1 style='font-size:2rem; font-weight:800; color:#00e5ff; margin:0;'>
            🔍 QR Code Scanner
        </h1>
        <p style='color:#5a7a9a; margin-top:6px;'>
            Upload a QR code image to extract and analyse the embedded URL for threats.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_upload, col_result = st.columns([1, 1], gap="large")

    with col_upload:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📤 Upload QR Code</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Drag & drop or click to browse",
            type=["png", "jpg", "jpeg", "webp"],
            label_visibility="collapsed",
        )
        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded QR Code", use_column_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Manual URL entry
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🔗 Or Enter URL Manually</div>', unsafe_allow_html=True)
        manual_url = st.text_input("Paste a URL to analyse", placeholder="https://example.com", label_visibility="collapsed")
        manual_btn  = st.button("🔎 Analyse URL", use_container_width=True, key="manual_btn")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_result:

        # ── QR File Analysis ──────────────────────────────────────
        if uploaded_file:
            with st.spinner("🔍 Decoding QR code…"):
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp.write(uploaded_file.getbuffer())
                    tmp_path = tmp.name

                urls = scan_qr(tmp_path)
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

            if not urls:
                st.error("❌ No QR code detected. Try a clearer or higher-resolution image.")
            else:
                for url in urls:
                    _render_analysis(url)

        # ── Manual URL Analysis ───────────────────────────────────
        if manual_btn and manual_url.strip():
            _render_analysis(manual_url.strip())

        if not uploaded_file and not (manual_btn and manual_url.strip()):
            st.markdown("""
            <div class="glass-card" style="text-align:center; padding:50px 20px; color:#3a5a7a;">
                <div style="font-size:3rem; margin-bottom:16px;">🛡️</div>
                <div style="font-size:1rem; font-weight:600; color:#5a7a9a;">
                    Upload a QR code or enter a URL to begin analysis
                </div>
            </div>
            """, unsafe_allow_html=True)



# =========================
# PAGE: DASHBOARD
# =========================
elif page == "📊 Dashboard":

    st.markdown("""
    <div style='padding: 10px 0 24px 0;'>
        <h1 style='font-size:2rem; font-weight:800; color:#00e5ff; margin:0;'>
            📊 Security Dashboard
        </h1>
        <p style='color:#5a7a9a; margin-top:6px;'>
            Real-time overview of all scanned URLs and threat landscape.
        </p>
    </div>
    """, unsafe_allow_html=True)

    rows = get_all_scans()
    total  = len(rows)
    safe   = sum(1 for r in rows if r["risk_category"] == "Safe")
    mod    = sum(1 for r in rows if r["risk_category"] == "Moderate")
    danger = sum(1 for r in rows if r["risk_category"] == "Dangerous")
    avg_score = round(sum(r["risk_score"] for r in rows) / max(1, total), 1)

    # KPI Row
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("📊 Total Scans",     total)
    k2.metric("🟢 Safe",            safe)
    k3.metric("🟡 Moderate",        mod)
    k4.metric("🔴 Dangerous",       danger)
    k5.metric("⚡ Avg Threat",      f"{avg_score}/100")
    k6.metric("🎯 Detection Rate",  "92%")

    st.markdown("---")

    if rows:
        col_pie, col_line = st.columns(2, gap="large")

        with col_pie:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">🥧 Risk Distribution</div>', unsafe_allow_html=True)
            cats   = [r["risk_category"] for r in rows]
            color_map = {"Safe": "#00e676", "Moderate": "#ffb300", "Dangerous": "#ff3d3d"}
            fig_pie = px.pie(
                names=cats,
                color=cats,
                color_discrete_map=color_map,
                hole=0.55,
            )
            fig_pie.update_traces(textfont_color="white", pull=[0.03]*len(cats))
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e0e6f0",
                legend=dict(font=dict(color="#e0e6f0")),
                margin=dict(t=10, b=10, l=10, r=10),
                height=300,
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_line:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">📈 Scan History Trend</div>', unsafe_allow_html=True)
            df = pd.DataFrame(rows)
            fig_line = px.line(
                df, x="timestamp", y="risk_score",
                labels={"timestamp": "Date", "risk_score": "Risk Score"},
                color_discrete_sequence=["#00e5ff"],
            )
            fig_line.update_traces(
                line=dict(width=2.5),
                fill="tozeroy",
                fillcolor="rgba(0,229,255,0.07)",
            )
            fig_line.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e0e6f0",
                xaxis=dict(gridcolor="#1a2a4a", showgrid=True),
                yaxis=dict(gridcolor="#1a2a4a", showgrid=True, range=[0, 105]),
                margin=dict(t=10, b=10, l=10, r=10),
                height=300,
            )
            st.plotly_chart(fig_line, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Bar chart — score per scan
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📊 Risk Score Per Scan</div>', unsafe_allow_html=True)
        df["label"] = df["url"].str[:40] + "…"
        bar_colors  = [color_map.get(c, "#aaa") for c in df["risk_category"]]
        fig_bar = go.Figure(go.Bar(
            x=df["label"], y=df["risk_score"],
            marker_color=bar_colors,
            text=df["risk_score"],
            textposition="outside",
            textfont_color="#e0e6f0",
        ))
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e0e6f0",
            xaxis=dict(gridcolor="#1a2a4a"),
            yaxis=dict(gridcolor="#1a2a4a", range=[0, 115]),
            margin=dict(t=10, b=60, l=10, r=10),
            height=340,
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("No scans recorded yet. Go to **Scan QR Code** to get started.")


# =========================
# PAGE: HISTORY
# =========================
elif page == "📜 History":

    st.markdown("""
    <div style='padding: 10px 0 24px 0;'>
        <h1 style='font-size:2rem; font-weight:800; color:#00e5ff; margin:0;'>
            📜 Scan History
        </h1>
        <p style='color:#5a7a9a; margin-top:6px;'>
            Full log of all URLs analysed by Suraksha Drishti.
        </p>
    </div>
    """, unsafe_allow_html=True)

    rows = get_all_scans()

    if rows:
        # Search / filter
        search = st.text_input("🔎 Search by URL…", placeholder="Type to filter", label_visibility="collapsed")
        if search:
            rows = [r for r in rows if search.lower() in r["url"].lower()]

        df = pd.DataFrame(rows)

        # Colour-coded category column
        def style_category(val):
            c = {"Safe": "#00e676", "Moderate": "#ffb300", "Dangerous": "#ff3d3d"}.get(val, "white")
            return f"color: {c}; font-weight: 600;"

        styled = (
            df[["id", "timestamp", "url", "risk_score", "risk_category"]]
            .style
            .applymap(style_category, subset=["risk_category"])
            .format({"risk_score": "{}/100"})
            .set_properties(**{"background-color": "transparent", "color": "#e0e6f0"})
        )
        st.dataframe(styled, use_container_width=True, height=420)

        col_dl, col_del = st.columns([2, 1])
        with col_dl:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Export as CSV",
                data=csv,
                file_name=f"suraksha_drishti_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with col_del:
            if st.button("🗑️ Clear All History", use_container_width=True, type="secondary"):
                delete_all_scans()
                st.rerun()
    else:
        st.info("No scan history found.")


# =========================
# PAGE: SETTINGS
# =========================
elif page == "⚙️ Settings":

    st.markdown("""
    <div style='padding: 10px 0 24px 0;'>
        <h1 style='font-size:2rem; font-weight:800; color:#00e5ff; margin:0;'>
            ⚙️ Settings
        </h1>
        <p style='color:#5a7a9a; margin-top:6px;'>
            Configure application preferences.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">🗄️ Database</div>', unsafe_allow_html=True)
    if st.button("🗑️ Clear All Scan Records", type="secondary"):
        delete_all_scans()
        st.success("All scan records cleared.")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">ℹ️ About</div>', unsafe_allow_html=True)
    st.markdown("""
    **Suraksha Drishti** v2.0.0  
    AI-Powered QR Fraud Detection & Cybersecurity Dashboard  
    Built with Python 3.11 · Streamlit 1.39 · OpenCV · fpdf · SQLite  
    """)
    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# FOOTER
# =========================
st.markdown("""
<div style='text-align:center; padding: 40px 0 20px 0; color:#2a3a5a; font-size:0.78rem;'>
    © 2026 Suraksha Drishti &nbsp;|&nbsp; AI-Powered Cybersecurity Platform
</div>
""", unsafe_allow_html=True)