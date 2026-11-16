
import streamlit as st
from utils.patient_context import patient_sidebar


def render_sidebar():
    with st.sidebar:

        # APP HEADER
        st.markdown("## 🩺 ThyroGuard")
        st.caption("AI-POWERED THYROID HEALTH")

        st.divider()

        # MAIN WORKSPACE
        st.markdown("**WORKSPACE**")

        st.page_link(
            "app.py",
            label="Overview",
        )

        st.page_link(
            "pages/ThyroAI.py",
            label="ThyroAI",
        )

        st.page_link(
            "pages/0_Patient_Management.py",
            label="Patient Management",
        )

        st.page_link(
            "pages/1_ThyroidTrend.py",
            label="ThyroidTrend",
        )

        st.page_link(
            "pages/2_SymptomWatch.py",
            label="SymptomWatch",
        )

        st.page_link(
            "pages/3_FollowUpGuard.py",
            label="FollowUpGuard",
        )

        st.page_link(
            "pages/5_Reports.py",
            label="Reports",
        )

        st.divider()

        # MACHINE LEARNING RESEARCH
        st.markdown("**RESEARCH & TRANSPARENCY**")

        st.page_link(
            "pages/Model_Insights.py",
            label="Model Insights",
        )

        st.divider()

        # PATIENT SELECTION
        patient_sidebar()

        st.divider()

        # DISCLAIMER
        st.caption(
            "Educational research prototype. "
            "Use fictional sample data only. "
            "Not intended for clinical decision-making."
        )
