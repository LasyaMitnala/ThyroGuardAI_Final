
import streamlit as st
from utils.patient_context import patient_sidebar


def render_sidebar():

    with st.sidebar:

        st.markdown("## 🩺 ThyroGuard")
        st.caption("AI-POWERED THYROID HEALTH")

        st.divider()

        st.markdown("**WORKSPACE**")

        st.page_link(
            "app.py",
            label="Overview",
            icon="🏠"
        )

        st.page_link(
            "pages/ThyroAI.py",
            label="ThyroAI",
            icon="🧠"
        )

        st.page_link(
            "pages/0_Patient_Management.py",
            label="Patient Management",
            icon="👤"
        )

        st.page_link(
            "pages/1_ThyroidTrend.py",
            label="ThyroidTrend",
            icon="📈"
        )

        st.page_link(
            "pages/2_SymptomWatch.py",
            label="SymptomWatch",
            icon="💗"
        )

        st.page_link(
            "pages/3_FollowUpGuard.py",
            label="FollowUpGuard",
            icon="📅"
        )

        st.page_link(
            "pages/5_Reports.py",
            label="Reports",
            icon="📋"
        )

        patient_sidebar()

        st.divider()

        st.caption("DEMO WORKSPACE · Fictional sample data only")
