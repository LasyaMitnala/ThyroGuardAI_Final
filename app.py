
from utils.navigation import render_sidebar

import streamlit as st

from database.db import initialize_database, get_dashboard_summary
from utils.ui import load_css, page_header
from utils.patient_context import patient_sidebar


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="ThyroGuard | AI Thyroid Health",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()
initialize_database()


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

render_sidebar()

# --------------------------------------------------
# MAIN DASHBOARD HEADER
# --------------------------------------------------

page_header(
    "Your thyroid health, decoded.",
    "Explore thyroid laboratory patterns with machine learning "
    "and manage your health information in one place.",
)


# --------------------------------------------------
# MEDICAL DISCLAIMER
# --------------------------------------------------

st.markdown(
    '<div class="notice">'
    '<strong>Demonstration environment</strong> · '
    'This prototype uses fictional sample data. '
    'AI classifications are for educational and research '
    'purposes only and do not replace clinical diagnosis.'
    '</div>',
    unsafe_allow_html=True,
)


# --------------------------------------------------
# PRIMARY FEATURE: THYROAI
# --------------------------------------------------

st.markdown("")


st.html("""
<div style="
    background: linear-gradient(120deg, #E7F7FA, #F4FBFD, #FFFFFF);
    border: 1px solid #B9E3EC;
    border-radius: 22px;
    padding: 36px;
    margin-bottom: 12px;
">
    <div style="color: #008DB4; font-size: 12px; font-weight: 800; letter-spacing: 2px;">
        INTRODUCING THYROAI
    </div>

    <h2 style="color: #17344A; font-size: 34px; font-weight: 800;">
        Meet your AI-powered thyroid analysis engine.
    </h2>

    <p style="color: #587084; font-size: 16px; line-height: 1.7;">
        ThyroAI uses a trained Random Forest model to analyze thyroid
        laboratory measurements and identify patterns learned from
        historical data.
    </p>

    <p style="color: #008DB4; font-weight: 600;">
        Machine Learning · Thyroid Classification · UCI Dataset
    </p>
</div>
""")


if st.button(
    "Launch ThyroAI Analysis →",
    type="primary",
    use_container_width=True,
):
    st.switch_page("pages/ThyroAI.py")


# --------------------------------------------------
# SECONDARY FEATURES
# --------------------------------------------------

st.markdown("")
st.markdown("")

st.markdown(
    '<div class="section-kicker">CONNECTED HEALTH TOOLS</div>'
    '<div class="section-title">Your health workspace</div>',
    unsafe_allow_html=True,
)

st.write(
    "Explore additional tools for tracking thyroid measurements, "
    "recording symptoms, and organizing health information."
)

tools = [
    (
        "01",
        "ThyroidTrend",
        "Visualize thyroid laboratory measurements and "
        "explore changes over time.",
        "pages/1_ThyroidTrend.py",
    ),
    (
        "02",
        "SymptomWatch",
        "Record daily symptoms and monitor patterns "
        "across your health history.",
        "pages/2_SymptomWatch.py",
    ),
    (
        "03",
        "FollowUpGuard",
        "Organize clinician-recommended monitoring "
        "dates and follow-up activities.",
        "pages/3_FollowUpGuard.py",
    ),
    (
        "04",
        "Reports",
        "Review your recorded health information "
        "and monitoring summaries.",
        "pages/5_Reports.py",
    ),
]

left, right = st.columns(2, gap="large")

for index, (number, title, description, path) in enumerate(tools):

    with (left if index % 2 == 0 else right):

        st.markdown(
            f'<div class="module-card">'
            f'<div class="module-number">{number}</div>'
            f'<div>'
            f'<div class="module-title">{title}</div>'
            f'<div class="module-desc">{description}</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.page_link(
            path,
            label=f"Explore {title} →",
        )

        st.markdown("")


# --------------------------------------------------
# PATIENT ACTIVITY
# --------------------------------------------------

st.markdown("")
st.markdown("")

st.markdown(
    '<div class="section-kicker">YOUR HEALTH DATA</div>'
    '<div class="section-title">Patient activity</div>',
    unsafe_allow_html=True,
)

active_patient_id = st.session_state.get("selected_patient_id")

summary = get_dashboard_summary(active_patient_id)

cols = st.columns(4)

metrics = [
    (
        "ACTIVE PATIENT",
        summary["patients"],
        "Selected patient profile",
    ),
    (
        "LAB ENTRIES",
        summary["labs"],
        "Recorded thyroid panels",
    ),
    (
        "SYMPTOM CHECK-INS",
        summary["symptoms"],
        "Patient-reported entries",
    ),
    (
        "FOLLOW-UPS",
        summary["followups"],
        "Monitoring dates on file",
    ),
]

for col, (label, value, help_text) in zip(cols, metrics):

    with col:

        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div>'
            f'<div class="metric-help">{help_text}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")

st.caption(
    "ThyroGuard · AI-powered thyroid health research "
    "and monitoring · Educational prototype only. "
    "Not intended for medical diagnosis or treatment."
)
