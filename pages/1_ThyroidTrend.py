import json
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.navigation import render_sidebar
from datetime import date
from database.db import (
    initialize_database, get_lab_entries, add_lab_entry, delete_lab_entry
)
from utils.ui import load_css, page_header
from utils.patient_context import patient_sidebar, selected_patient_id

st.set_page_config(page_title="ThyroidTrend | ThyroGuard", page_icon="🩺", layout="wide")
load_css()
initialize_database()

render_sidebar()

patient_id = selected_patient_id()
page_header(
    "ThyroidTrend",
    "Record thyroid laboratory panels, review longitudinal patterns, and prepare clearer summaries for clinician discussions."
)

st.markdown(
    '<div class="notice"><strong>Prototype safety note</strong> · '
    'Use fictional demonstration data only. Reference intervals vary by laboratory, '
    'assay, age, pregnancy status and clinical context. This tool does not diagnose '
    'thyroid disease or recommend treatment changes.</div>',
    unsafe_allow_html=True
)

if patient_id is None:
    st.warning("Create a patient profile in Patient Management before entering laboratory results.")
    st.stop()

# Entry workflow
with st.expander("＋ Add a laboratory panel", expanded=False):
    st.caption("Enter values exactly as shown on the laboratory report, including the units and that report's reference intervals.")
    with st.form("thyroid_lab_entry", clear_on_submit=True):
        dcol, unitcol = st.columns([1, 1])
        test_date = dcol.date_input("Test date", value=date.today(), max_value=date.today())
        units = unitcol.selectbox("Units / reporting convention", ["Use units printed on report"])
        st.markdown("#### Laboratory values")
        a, b, c = st.columns(3)
        tsh = a.number_input("TSH", min_value=0.0, max_value=1000.0, value=2.5, step=0.01, format="%.2f")
        ft4 = b.number_input("Free T4 (FT4)", min_value=0.0, max_value=100.0, value=1.2, step=0.01, format="%.2f")
        ft3 = c.number_input("Free T3 (FT3)", min_value=0.0, max_value=100.0, value=3.2, step=0.01, format="%.2f")
        st.markdown("#### Reference intervals from this report")
        st.caption("The example values are placeholders only. Replace them with the reference intervals printed on the actual report.")
        x1, x2, x3 = st.columns(3)
        with x1:
            st.markdown("**TSH interval**")
            tsh_low = st.number_input("TSH lower", min_value=0.0, max_value=1000.0, value=0.4, step=0.01, key="tsh_low")
            tsh_high = st.number_input("TSH upper", min_value=0.0, max_value=1000.0, value=4.0, step=0.01, key="tsh_high")
        with x2:
            st.markdown("**FT4 interval**")
            ft4_low = st.number_input("FT4 lower", min_value=0.0, max_value=100.0, value=0.8, step=0.01, key="ft4_low")
            ft4_high = st.number_input("FT4 upper", min_value=0.0, max_value=100.0, value=1.8, step=0.01, key="ft4_high")
        with x3:
            st.markdown("**FT3 interval**")
            ft3_low = st.number_input("FT3 lower", min_value=0.0, max_value=100.0, value=2.3, step=0.01, key="ft3_low")
            ft3_high = st.number_input("FT3 upper", min_value=0.0, max_value=100.0, value=4.2, step=0.01, key="ft3_high")
        submitted = st.form_submit_button("Save laboratory panel", type="primary", use_container_width=True)
        if submitted:
            intervals = [(tsh_low,tsh_high,"TSH"),(ft4_low,ft4_high,"FT4"),(ft3_low,ft3_high,"FT3")]
            invalid = [name for low,high,name in intervals if low >= high]
            if invalid:
                st.error("Each lower reference limit must be less than its upper limit: " + ", ".join(invalid))
            else:
                add_lab_entry(
                    patient_id, test_date.isoformat(), tsh, ft4, ft3,
                    tsh_low, tsh_high, ft4_low, ft4_high, ft3_low, ft3_high
                )
                st.success("Laboratory panel saved to this patient's record.")
                st.rerun()

records = get_lab_entries(patient_id)
df = pd.DataFrame(records)

st.markdown("### Laboratory snapshot")
if df.empty:
    st.info("No laboratory panels have been recorded for this patient yet. Use 'Add a laboratory panel' above to begin.")
    st.stop()

df["test_date"] = pd.to_datetime(df["test_date"])
df = df.sort_values("test_date").reset_index(drop=True)
latest = df.iloc[-1]

m1, m2, m3 = st.columns(3)
m1.metric("Latest TSH", f'{latest["tsh"]:.2f}')
m2.metric("Latest FT4", f'{latest["ft4"]:.2f}')
m3.metric("Latest FT3", f'{latest["ft3"]:.2f}')
st.caption(f'Latest recorded panel: {latest["test_date"].date().isoformat()} · {len(df)} panel(s) on file')

# Reference interval flags are descriptive comparisons, not diagnoses.
def interval_status(value, low, high):
    if pd.isna(value) or pd.isna(low) or pd.isna(high):
        return "Reference interval unavailable"
    if value < low:
        return "Below entered interval"
    if value > high:
        return "Above entered interval"
    return "Within entered interval"

st.markdown("### Latest panel: comparison with entered reference intervals")
status_rows = []
for label, key, low_key, high_key in [
    ("TSH","tsh","tsh_low","tsh_high"),
    ("Free T4","ft4","ft4_low","ft4_high"),
    ("Free T3","ft3","ft3_low","ft3_high")
]:
    status_rows.append({
        "Measurement": label,
        "Result": latest[key],
        "Entered reference interval": f'{latest[low_key]} – {latest[high_key]}',
        "Comparison": interval_status(latest[key], latest[low_key], latest[high_key])
    })
st.dataframe(pd.DataFrame(status_rows), use_container_width=True, hide_index=True)

st.markdown("### Longitudinal trends")
metric_key = st.selectbox(
    "Choose measurement",
    ["tsh","ft4","ft3"],
    format_func=lambda v: {"tsh":"TSH","ft4":"Free T4 (FT4)","ft3":"Free T3 (FT3)"}[v]
)
metric_label = {"tsh":"TSH","ft4":"Free T4 (FT4)","ft3":"Free T3 (FT3)"}[metric_key]
fig = px.line(df, x="test_date", y=metric_key, markers=True, title=f"{metric_label} over time")
fig.update_traces(line=dict(width=3), marker=dict(size=9))
fig.update_layout(
    plot_bgcolor="white", paper_bgcolor="white", font_color="#294454",
    xaxis_title="Test date", yaxis_title=metric_label,
    margin=dict(l=15,r=15,t=55,b=15)
)
st.plotly_chart(fig, use_container_width=True)

# Transparent trend summaries: deterministic calculations, not a trained ML model.
st.markdown("### ThyroidTrend analytical summary")
if len(df) >= 2:
    previous = df.iloc[-2]
    cols = st.columns(3)
    for col, key, label in [
        (cols[0],"tsh","TSH"),(cols[1],"ft4","FT4"),(cols[2],"ft3","FT3")
    ]:
        old = float(previous[key])
        new = float(latest[key])
        delta = new - old
        pct = (delta / abs(old) * 100) if old != 0 else None
        pct_text = f"{pct:+.1f}%" if pct is not None else "N/A (prior value was zero)"
        col.metric(f"{label}: change since previous panel", f"{delta:+.2f}", pct_text)
    st.info(
        "The latest panel is compared with the immediately preceding recorded panel. "
        "Changes alone do not establish clinical significance; interpretation depends on "
        "the laboratory, timing, medication context and clinician assessment."
    )
else:
    st.info("Add at least one more dated panel to calculate changes between consecutive tests.")

with st.expander("View complete laboratory history"):
    display = df[["test_date","tsh","ft4","ft3","tsh_low","tsh_high","ft4_low","ft4_high","ft3_low","ft3_high"]].copy()
    display["test_date"] = display["test_date"].dt.date.astype(str)
    st.dataframe(display, use_container_width=True, hide_index=True)

with st.expander("Remove an incorrectly entered panel"):
    st.warning("This permanently deletes the selected laboratory entry from this local prototype database.")
    options = {int(row["id"]): f'{row["test_date"].date().isoformat()} · TSH {row["tsh"]:.2f}, FT4 {row["ft4"]:.2f}, FT3 {row["ft3"]:.2f}' for _,row in df.iterrows()}
    selected_entry = st.selectbox("Select entry", list(options.keys()), format_func=lambda x: options[x])
    confirm_delete = st.checkbox("I understand this laboratory entry will be permanently deleted.")
    if st.button("Delete selected panel", disabled=not confirm_delete):
        delete_lab_entry(selected_entry, patient_id)
        st.success("Laboratory panel deleted.")
        st.rerun()

st.markdown("---")
st.caption(
    "Current implementation: validated data entry, patient-specific persistence, reference-interval comparison, "
    "historical visualization and transparent change calculations. A separately validated machine-learning model "
    "and AI-generated interpretation are planned for the AI integration stage."
)



# ==========================================
# THYROGUARD ML RESEARCH MODEL RESULTS
# ==========================================

st.markdown("---")
st.markdown("## Machine Learning Research Results")

report_path = (
    Path(__file__).resolve().parents[1]
    / "models"
    / "evaluation_report.json"
)

if report_path.exists():

    with open(report_path, "r") as file:
        report = json.load(file)

    results = report["official_test_evaluation"]

    st.markdown(
        '<div class="notice"><strong>Research model only</strong> · '
        'These results describe performance on a historical public '
        'dataset. They are not individual patient predictions, '
        'a diagnosis, or medical advice.</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"**Selected model:** {report['selected_model']}"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Test accuracy",
        f"{results['accuracy'] * 100:.2f}%"
    )

    col2.metric(
        "Balanced accuracy",
        f"{results['balanced_accuracy'] * 100:.2f}%"
    )

    col3.metric(
        "Macro F1",
        f"{results['macro_f1'] * 100:.2f}%"
    )

    st.markdown("### Confusion matrix")

    matrix = pd.DataFrame(
        results["confusion_matrix"],
        index=["Actual 1", "Actual 2", "Actual 3"],
        columns=["Predicted 1", "Predicted 2", "Predicted 3"]
    )

    st.dataframe(matrix, use_container_width=True)

    st.markdown("### False-positive and false-negative analysis")

    class_metrics = results["class_metrics"]

    error_data = []

    for label, metrics in class_metrics.items():
        error_data.append({
            "Class": label,
            "False positives": metrics["false_positives"],
            "False negatives": metrics["false_negatives"],
            "Sensitivity": round(
                metrics["sensitivity_recall"] * 100, 2
            ),
            "Specificity": round(
                metrics["specificity"] * 100, 2
            )
        })

    st.dataframe(
        pd.DataFrame(error_data),
        use_container_width=True,
        hide_index=True
    )

    with st.expander("Model limitations and dataset information"):
        st.write("Dataset:", report["dataset"])
        st.write("Training records:", report["training_rows"])
        st.write("Validation records:", report["validation_rows"])
        st.write("Official test records:", report["official_test_rows"])
        st.write("Features:", report["feature_count"])

        for limitation in report["limitations"]:
            st.write("•", limitation)

else:
    st.info(
        "Train the ThyroidTrend research model to display "
        "its evaluation results here."
    )

st.caption(
    "This project is a prototype and is not medical advice."
)
