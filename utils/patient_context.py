import streamlit as st
from database.db import get_patients

def selected_patient_id():
    patients = get_patients()
    if not patients:
        return None
    ids = [p["id"] for p in patients]
    current = st.session_state.get("selected_patient_id")
    if current not in ids:
        st.session_state["selected_patient_id"] = ids[0]
    return st.session_state["selected_patient_id"]

def patient_sidebar():
    patients = get_patients()
    if not patients:
        st.sidebar.warning("No active patient profiles. Create one in Patient Management.")
        return None
    labels = {p["id"]: p["display_name"] for p in patients}
    current_id = selected_patient_id()
    st.sidebar.markdown("**ACTIVE PATIENT**")
    chosen = st.sidebar.selectbox(
        "Select patient",
        options=list(labels.keys()),
        format_func=lambda pid: labels[pid],
        index=list(labels.keys()).index(current_id),
        key="patient_context_selector",
        label_visibility="collapsed",
    )
    st.session_state["selected_patient_id"] = chosen
    return chosen
