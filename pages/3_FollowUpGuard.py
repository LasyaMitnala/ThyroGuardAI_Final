import streamlit as st
import pandas as pd
from datetime import date
from utils.navigation import render_sidebar
from database.db import initialize_database, get_followups
from utils.ui import load_css, page_header
from utils.patient_context import patient_sidebar, selected_patient_id
st.set_page_config(page_title="FollowUpGuard | ThyroGuard", page_icon="🩺", layout="wide")
load_css(); initialize_database()

render_sidebar()


active_patient_id = selected_patient_id() or 1
page_header("FollowUpGuard", "Keep clinician-recommended monitoring dates visible.")
rows = get_followups(active_patient_id)
if rows:
    for item in rows:
        due = date.fromisoformat(item["next_review_date"])
        st.metric("Recorded next review date", due.strftime("%B %d, %Y"), f"{(due-date.today()).days} days from today")
        if due < date.today() and not item["completed"]:
            st.warning("The recorded review date has passed and no completion is recorded. Contact your healthcare provider to confirm your monitoring plan.")
        else:
            st.success("A future review date is recorded.")
        st.caption(item["clinician_note"])
st.info("Reminder logic is a scheduling aid, not a medical determination. Follow the schedule provided by the treating clinician.")
