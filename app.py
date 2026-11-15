
import streamlit as st
from database.db import initialize_database, get_dashboard_summary
from utils.ui import load_css, page_header
from utils.patient_context import patient_sidebar

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="ThyroGuard | Thyroid Monitoring",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()
initialize_database()

# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-mark">T</div>'
        '<div><div class="brand-name">ThyroGuard</div>'
        '<div class="brand-sub">THYROID HEALTH PLATFORM</div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("**WORKSPACE**")

    st.page_link("app.py", label="Overview")
    st.page_link("pages/0_Patient_Management.py", label="Patient Management")
    st.page_link("pages/1_ThyroidTrend.py", label="ThyroidTrend")
    st.page_link("pages/2_SymptomWatch.py", label="SymptomWatch")
    st.page_link("pages/3_FollowUpGuard.py", label="FollowUpGuard")
    st.page_link("pages/5_Reports.py", label="Reports")

    patient_sidebar()

    st.markdown("---")
    st.markdown(
        '<div class="sidebar-note">DEMO WORKSPACE<br>'
        '<span>Fictional sample data only</span></div>',
        unsafe_allow_html=True
    )

# --------------------------------------------------
# DASHBOARD HEADER
# --------------------------------------------------

page_header(
    "Patient overview",
    "A clearer picture of thyroid measurements, symptoms, and follow-up activity."
)

active_patient_id = st.session_state.get("selected_patient_id")
summary = get_dashboard_summary(active_patient_id)

st.markdown(
    '<div class="notice"><strong>Demonstration environment</strong> '
    '· This prototype uses fictional sample data. It is not a medical device '
    'and does not diagnose, recommend treatment, or replace a clinician.</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# DASHBOARD METRICS
# --------------------------------------------------

cols = st.columns(4)

metrics = [
    ("ACTIVE PATIENT", summary["patients"], "Selected patient profile"),
    ("LAB ENTRIES", summary["labs"], "Recorded thyroid panels"),
    ("SYMPTOM CHECK-INS", summary["symptoms"], "Patient-reported entries"),
    ("FOLLOW-UPS", summary["followups"], "Monitoring dates on file"),
]

for col, (label, value, help_text) in zip(cols, metrics):
    with col:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div>'
            f'<div class="metric-help">{help_text}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

# --------------------------------------------------
# THREE CORE MONITORING MODULES
# --------------------------------------------------

left, right = st.columns([1.35, 1])

with left:

    st.markdown(
        '<div class="section-kicker">YOUR WORKSPACE</div>'
        '<div class="section-title">Three connected monitoring modules</div>',
        unsafe_allow_html=True
    )

    cards = [
        (
            "01",
            "ThyroidTrend",
            "Explore lab history, reference intervals, and changes over time.",
            "pages/1_ThyroidTrend.py"
        ),
        (
            "02",
            "SymptomWatch",
            "Record daily experiences and understand symptom patterns.",
            "pages/2_SymptomWatch.py"
        ),
        (
            "03",
            "FollowUpGuard",
            "Keep clinician-recommended monitoring dates visible.",
            "pages/3_FollowUpGuard.py"
        ),
    ]

    for number, title, desc, path in cards:

        st.markdown(
            f'<div class="module-card">'
            f'<div class="module-number">{number}</div>'
            f'<div><div class="module-title">{title}</div>'
            f'<div class="module-desc">{desc}</div></div></div>',
            unsafe_allow_html=True
        )

        st.page_link(path, label=f"Open {title}")

# --------------------------------------------------
# DEVELOPMENT CHECKLIST
# --------------------------------------------------

with right:

    st.markdown(
        '<div class="section-kicker">GETTING STARTED</div>'
        '<div class="section-title">Development progress</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="panel">
      <div class="panel-title">Foundation checklist</div>
      <div class="check-row">✓ Streamlit application shell</div>
      <div class="check-row">✓ Clinical visual system</div>
      <div class="check-row">✓ Local SQLite database</div>
      <div class="check-row">✓ Patient management</div>
      <div class="check-row">✓ Three monitoring modules</div>
      <div class="check-row">○ Validated machine-learning pipelines</div>
      <div class="check-row">○ AI-assisted analysis</div>
      <div class="check-row">○ Report generation and export</div>
    </div>

    <div class="panel subtle-panel">
      <div class="panel-title">Our AI approach</div>
      <p>ThyroGuard will distinguish validated machine-learning
      predictions from transparent trend calculations, symptom
      pattern analysis, and clinician-directed reminder rules.</p>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.caption(
    "ThyroGuard prototype · Three-module architecture · Local demo only"
)
