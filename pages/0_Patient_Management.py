import streamlit as st
from datetime import date
from database.db import initialize_database, get_patients, create_patient, update_patient, archive_patient, get_patient
from utils.ui import load_css, page_header
from utils.patient_context import patient_sidebar

st.set_page_config(page_title="Patient Management | ThyroGuard", page_icon="🩺", layout="wide")
load_css()
initialize_database()
with st.sidebar:
    st.markdown("### ThyroGuard")
    st.page_link("app.py", label="Overview")
    st.page_link("pages/0_Patient_Management.py", label="Patient Management")
    st.page_link("pages/1_ThyroidTrend.py", label="ThyroidTrend")
    st.page_link("pages/2_SymptomWatch.py", label="SymptomWatch")
    st.page_link("pages/3_FollowUpGuard.py", label="FollowUpGuard")
    st.page_link("pages/5_Reports.py", label="Reports")
patient_sidebar()

page_header("Patient management", "Create and maintain the patient profile shared across all ThyroGuard modules.")
st.markdown('<div class="notice"><strong>Privacy note</strong> · Use fictional demonstration profiles only in this prototype. Do not enter real patient identifiers or sensitive health information.</div>', unsafe_allow_html=True)

tab_create, tab_manage = st.tabs(["＋ Create profile", "Manage profiles"])
with tab_create:
    st.markdown("#### New patient profile")
    with st.form("create_patient_form", clear_on_submit=True):
        name = st.text_input("Display name *", placeholder="e.g., Demo Patient B")
        diagnosis = st.selectbox("Recorded diagnosis", ["Hypothyroidism", "Hyperthyroidism", "Other / not specified"])
        medication = st.text_input("Medication (optional)", placeholder="Only enter clinician-recorded information")
        dob = st.date_input("Date of birth (optional)", value=None, min_value=date(1900,1,1), max_value=date.today())
        notes = st.text_area("Clinician notes (optional)", placeholder="Brief notes for demonstration; avoid identifiable information.")
        submitted = st.form_submit_button("Create patient profile", type="primary")
        if submitted:
            if not name.strip():
                st.error("Please enter a display name.")
            else:
                pid = create_patient(name, diagnosis, medication, dob.isoformat() if dob else None, notes)
                st.session_state["selected_patient_id"] = pid
                st.success(f"Profile created for {name.strip()}. It is now the active patient.")
                st.rerun()

with tab_manage:
    patients = get_patients()
    if not patients:
        st.info("No active patient profiles.")
    else:
        labels = {p["id"]: f'{p["display_name"]} · #{p["id"]}' for p in patients}
        chosen_id = st.selectbox("Choose a profile to edit", list(labels.keys()), format_func=lambda x: labels[x])
        patient = get_patient(chosen_id)
        with st.form("edit_patient_form"):
            edit_name = st.text_input("Display name *", value=patient["display_name"])
            diagnoses = ["Hypothyroidism", "Hyperthyroidism", "Other / not specified"]
            diagnosis_index = diagnoses.index(patient["diagnosis"]) if patient["diagnosis"] in diagnoses else 2
            edit_diagnosis = st.selectbox("Recorded diagnosis", diagnoses, index=diagnosis_index)
            edit_medication = st.text_input("Medication", value=patient.get("medication") or "")
            dob_value = date.fromisoformat(patient["date_of_birth"]) if patient.get("date_of_birth") else None
            edit_dob = st.date_input("Date of birth (optional)", value=dob_value, min_value=date(1900,1,1), max_value=date.today())
            edit_notes = st.text_area("Clinician notes", value=patient.get("clinician_notes") or "")
            save = st.form_submit_button("Save profile changes", type="primary")
            if save:
                if not edit_name.strip():
                    st.error("Display name cannot be empty.")
                else:
                    update_patient(chosen_id, edit_name, edit_diagnosis, edit_medication,
                                   edit_dob.isoformat() if edit_dob else None, edit_notes)
                    st.success("Patient profile updated.")
                    st.rerun()
        st.markdown("---")
        st.markdown("#### Archive profile")
        st.caption("Archiving hides a profile from active patient selectors. Its records remain in the local database.")
        if len(patients) == 1:
            st.info("At least one active patient profile must remain.")
        else:
            confirm = st.checkbox(f"I want to archive {patient['display_name']}.")
            if st.button("Archive selected profile", disabled=not confirm):
                archive_patient(chosen_id)
                if st.session_state.get("selected_patient_id") == chosen_id:
                    remaining = [p for p in get_patients()]
                    if remaining:
                        st.session_state["selected_patient_id"] = remaining[0]["id"]
                st.success("Profile archived.")
                st.rerun()
