import streamlit as st
from database.db import initialize_database, get_lab_entries, get_symptom_entries, get_followups
from utils.ui import load_css, page_header
from utils.patient_context import patient_sidebar, selected_patient_id
st.set_page_config(page_title="Reports | ThyroGuard", page_icon="🩺", layout="wide")
load_css(); initialize_database()
with st.sidebar:
    st.markdown("### ThyroGuard")
    st.page_link("app.py", label="Overview")
    st.page_link("pages/0_Patient_Management.py", label="Patient Management")
    st.page_link("pages/1_ThyroidTrend.py", label="ThyroidTrend")
    st.page_link("pages/2_SymptomWatch.py", label="SymptomWatch")
    st.page_link("pages/3_FollowUpGuard.py", label="FollowUpGuard")
    st.page_link("pages/5_Reports.py", label="Reports")
patient_sidebar()
active_patient_id = selected_patient_id() or 1
page_header("Appointment reports", "A structured snapshot of recorded information for discussion with a healthcare professional.")
labs, symptoms, followups = get_lab_entries(active_patient_id), get_symptom_entries(active_patient_id), get_followups(active_patient_id)
st.write("**Demonstration patient:** Demo Patient A")
st.write("**Laboratory entries:**", len(labs))
st.write("**Symptom check-ins:**", len(symptoms))
st.write("**Recorded follow-up plans:**", len(followups))
st.warning("Report export will be implemented in a later phase. This preview contains fictional demonstration data only.")
