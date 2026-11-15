
import streamlit as st
import pandas as pd
from utils.navigation import render_sidebar
import plotly.express as px
import numpy as np

from datetime import date
from pathlib import Path

from database.db import (
    initialize_database,
    get_symptom_entries,
    add_symptom_entry,
    delete_symptom_entry,
    get_lab_entries
)

from utils.ui import load_css, page_header
from utils.patient_context import patient_sidebar, selected_patient_id


# ==========================================================
# 1. PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="SymptomWatch | ThyroGuard",
    page_icon="🩺",
    layout="wide"
)

load_css()
initialize_database()

render_sidebar()

patient_id = selected_patient_id()

page_header(
    "SymptomWatch",
    "Intelligent monitoring of patient-reported symptoms and changes over time."
)


# ==========================================================
# 2. SAFETY NOTICE
# ==========================================================

st.markdown(
    '<div class="notice"><strong>Prototype safety note</strong> · '
    'Use fictional demonstration data only. Symptom ratings are '
    'subjective tracking information, not a diagnosis or a substitute '
    'for clinical assessment.</div>',
    unsafe_allow_html=True
)

if patient_id is None:
    st.warning(
        "Create an active patient profile in Patient Management "
        "before recording check-ins."
    )
    st.stop()


# ==========================================================
# 3. CONFIGURATION
# ==========================================================

SYMPTOM_LABELS = {
    "fatigue": "Fatigue severity",
    "concentration": "Concentration difficulty",
    "memory": "Memory difficulty",
    "sleep": "Sleep difficulty",
    "energy": "Energy level"
}

DIFFICULTY_DIMENSIONS = [
    "fatigue",
    "concentration",
    "memory",
    "sleep"
]

ALL_DIMENSIONS = [
    "fatigue",
    "concentration",
    "memory",
    "sleep",
    "energy"
]

# Higher scores mean more difficulty for these dimensions.
# Energy is handled separately because higher is better.


# ==========================================================
# 4. ANALYTICS FUNCTIONS
# ==========================================================

def get_direction(current, previous, dimension):
    """
    Compare recent and previous averages.
    A positive change means more difficulty for symptoms,
    but higher energy is generally a favorable direction.
    """

    difference = current - previous

    if abs(difference) < 0.35:
        return "Stable"

    if dimension == "energy":
        return "Improving" if difference > 0 else "Declining"

    return "Worsening" if difference > 0 else "Improving"


def calculate_period_comparison(data):
    """
    Compare the latest three check-ins against the
    three check-ins immediately before them.

    This is based on entry count, not fixed calendar weeks.
    """

    if len(data) < 6:
        return None

    previous = data.iloc[-6:-3]
    recent = data.iloc[-3:]

    comparisons = {}

    for dimension in ALL_DIMENSIONS:

        previous_avg = float(previous[dimension].mean())
        recent_avg = float(recent[dimension].mean())

        comparisons[dimension] = {
            "previous_average": previous_avg,
            "recent_average": recent_avg,
            "change": recent_avg - previous_avg,
            "direction": get_direction(
                recent_avg,
                previous_avg,
                dimension
            )
        }

    return comparisons


def analyze_personal_baseline(data):
    """
    Compare the latest check-in against the patient's
    own historical average, excluding the latest entry.
    """

    if len(data) < 2:
        return None

    historical = data.iloc[:-1]
    latest = data.iloc[-1]

    baseline = {}

    for dimension in ALL_DIMENSIONS:

        average = float(historical[dimension].mean())
        current = float(latest[dimension])

        baseline[dimension] = {
            "historical_average": average,
            "latest": current,
            "difference": current - average
        }

    return baseline


def detect_patterns(data):
    """
    Detect descriptive patterns using correlations.
    Correlation does not establish causation.
    """

    if len(data) < 5:
        return []

    correlation = data[ALL_DIMENSIONS].corr()
    findings = []

    for i, first in enumerate(ALL_DIMENSIONS):

        for second in ALL_DIMENSIONS[i + 1:]:

            value = correlation.loc[first, second]

            if pd.isna(value):
                continue

            if abs(value) >= 0.70:

                findings.append({
                    "first": SYMPTOM_LABELS[first],
                    "second": SYMPTOM_LABELS[second],
                    "correlation": float(value),
                    "direction": (
                        "positive" if value > 0 else "negative"
                    )
                })

    findings.sort(
        key=lambda item: abs(item["correlation"]),
        reverse=True
    )

    return findings


def generate_insight_summary(data, comparisons, baseline, patterns):
    """
    Transparent, rule-based observation summary.
    This is not a generative AI diagnosis or prediction.
    """

    latest = data.iloc[-1]

    lines = []

    lines.append(
        f"The record contains {len(data)} symptom check-ins."
    )

    lines.append(
        "The most recent check-in was recorded on "
        f"{latest['entry_date'].date().isoformat()}."
    )

    high_difficulty = [
        SYMPTOM_LABELS[key]
        for key in DIFFICULTY_DIMENSIONS
        if int(latest[key]) >= 4
    ]

    if high_difficulty:
        lines.append(
            "The latest check-in contains ratings of 4 or 5 "
            "for: " + ", ".join(high_difficulty) + "."
        )
    else:
        lines.append(
            "No difficulty dimension was rated 4 or 5 "
            "in the latest check-in."
        )

    if comparisons:

        worsening = [
            SYMPTOM_LABELS[key]
            for key, value in comparisons.items()
            if value["direction"] == "Worsening"
        ]

        improving = [
            SYMPTOM_LABELS[key]
            for key, value in comparisons.items()
            if value["direction"] == "Improving"
        ]

        declining_energy = (
            comparisons["energy"]["direction"] == "Declining"
        )

        if worsening:
            lines.append(
                "Compared with the preceding three check-ins, "
                "higher difficulty averages were observed for: "
                + ", ".join(worsening) + "."
            )

        if improving:
            lines.append(
                "Lower difficulty averages or higher energy "
                "were observed for: "
                + ", ".join(improving) + "."
            )

        if declining_energy:
            lines.append(
                "Average energy ratings were lower in the "
                "most recent three check-ins."
            )

        if not worsening and not improving and not declining_energy:
            lines.append(
                "Recent average ratings were relatively stable "
                "compared with the preceding three check-ins."
            )

    if baseline:
        unusual = []

        for key, values in baseline.items():

            if key == "energy":
                continue

            if values["difference"] >= 1:
                unusual.append(SYMPTOM_LABELS[key])

        if unusual:
            lines.append(
                "The latest ratings were at least one point "
                "above the patient's historical average for: "
                + ", ".join(unusual) + "."
            )

    if patterns:
        lines.append(
            "Some dimensions showed a strong descriptive "
            "correlation across recorded check-ins. "
            "See the pattern analysis below."
        )

    lines.append(
        "These observations describe recorded ratings only. "
        "They do not establish a medical cause, predict disease, "
        "or recommend treatment."
    )

    return lines


# ==========================================================
# 5. DAILY SYMPTOM CHECK-IN
# ==========================================================

st.markdown("## Daily symptom check-in")

st.caption(
    "Symptom severity: 1 = minimal and 5 = severe. "
    "Energy: 1 = very low and 5 = very high."
)

with st.expander("＋ Record a symptom check-in", expanded=True):

    with st.form("symptom_checkin_form", clear_on_submit=True):

        entry_date = st.date_input(
            "Check-in date",
            value=date.today(),
            max_value=date.today()
        )

        st.markdown("#### Rate today's experience")

        col1, col2 = st.columns(2)

        with col1:

            fatigue = st.slider(
                "Fatigue severity",
                1, 5, 3
            )

            concentration = st.slider(
                "Concentration difficulty",
                1, 5, 3
            )

            memory = st.slider(
                "Memory difficulty",
                1, 5, 3
            )

        with col2:

            sleep = st.slider(
                "Sleep difficulty",
                1, 5, 3
            )

            energy = st.slider(
                "Energy level",
                1, 5, 3
            )

        notes = st.text_area(
            "Optional notes",
            placeholder="Add brief context about today's experience.",
            max_chars=1000
        )

        submitted = st.form_submit_button(
            "Save symptom check-in",
            type="primary",
            use_container_width=True
        )

        if submitted:

            add_symptom_entry(
                patient_id,
                entry_date.isoformat(),
                energy,
                fatigue,
                concentration,
                memory,
                sleep,
                notes
            )

            st.success("Symptom check-in saved.")
            st.rerun()


# ==========================================================
# 6. LOAD PATIENT DATA
# ==========================================================

records = get_symptom_entries(patient_id)
df = pd.DataFrame(records)

st.markdown("---")
st.markdown("## Symptom overview")

if df.empty:

    st.info(
        "No check-ins have been recorded for this patient yet. "
        "Add a check-in to activate the analytics."
    )

    st.stop()

df["entry_date"] = pd.to_datetime(df["entry_date"])

df = (
    df.sort_values(["entry_date", "id"])
    .reset_index(drop=True)
)

for dimension in ALL_DIMENSIONS:
    df[dimension] = pd.to_numeric(
        df[dimension],
        errors="coerce"
    )

df = df.dropna(subset=ALL_DIMENSIONS).reset_index(drop=True)

if df.empty:
    st.warning("No valid symptom measurements are available.")
    st.stop()

latest = df.iloc[-1]


# ==========================================================
# 7. LATEST SYMPTOM SNAPSHOT
# ==========================================================

st.markdown("### Latest recorded ratings")

metrics = st.columns(5)

for col, dimension in zip(metrics, ALL_DIMENSIONS):

    col.metric(
        SYMPTOM_LABELS[dimension],
        f"{int(latest[dimension])}/5"
    )

st.caption(
    f"Latest check-in: {latest['entry_date'].date().isoformat()} "
    f"· {len(df)} recorded check-in(s)"
)


# ==========================================================
# 8. PERSONAL BASELINE
# ==========================================================

st.markdown("---")
st.markdown("## Personal symptom baseline")

st.caption(
    "The baseline compares the latest check-in with the "
    "patient's previous recorded check-ins."
)

baseline = analyze_personal_baseline(df)

if baseline is None:

    st.info(
        "At least two check-ins are needed to establish "
        "a personal comparison baseline."
    )

else:

    baseline_cols = st.columns(5)

    for col, dimension in zip(baseline_cols, ALL_DIMENSIONS):

        values = baseline[dimension]

        col.metric(
            SYMPTOM_LABELS[dimension],
            f"{values['latest']:.1f}/5",
            delta=(
                f"{values['difference']:+.2f} vs baseline"
            )
        )

    st.caption(
        "For difficulty ratings, a positive difference means "
        "a higher reported difficulty. For energy, a positive "
        "difference means higher reported energy."
    )


# ==========================================================
# 9. SYMPTOM TREND VISUALIZATION
# ==========================================================

st.markdown("---")
st.markdown("## Longitudinal symptom trends")

selected_dimensions = st.multiselect(
    "Choose dimensions to compare",
    options=ALL_DIMENSIONS,
    default=["fatigue", "concentration"],
    format_func=lambda value: SYMPTOM_LABELS[value]
)

if selected_dimensions:

    long_df = df[
        ["entry_date"] + selected_dimensions
    ].melt(
        id_vars="entry_date",
        var_name="dimension",
        value_name="rating"
    )

    long_df["dimension"] = long_df["dimension"].map(
        SYMPTOM_LABELS
    )

    fig = px.line(
        long_df,
        x="entry_date",
        y="rating",
        color="dimension",
        markers=True,
        title="Patient-reported symptom ratings over time"
    )

    fig.update_yaxes(
        range=[0.5, 5.5],
        dtick=1,
        title="Rating (1–5)"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_color="#294454",
        xaxis_title="Check-in date",
        margin=dict(l=15, r=15, t=55, b=15),
        legend_title_text="Dimension"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.info("Choose at least one dimension.")


# ==========================================================
# 10. RECENT PERIOD COMPARISON
# ==========================================================

st.markdown("---")
st.markdown("## Recent change detection")

st.caption(
    "Compares the latest three recorded check-ins with the "
    "three check-ins immediately before them. These are entry "
    "windows, not fixed calendar weeks."
)

comparisons = calculate_period_comparison(df)

if comparisons is None:

    st.info(
        "At least six check-ins are needed for this comparison."
    )

else:

    comparison_data = []

    for dimension, values in comparisons.items():

        comparison_data.append({
            "Dimension": SYMPTOM_LABELS[dimension],
            "Previous average": round(
                values["previous_average"], 2
            ),
            "Recent average": round(
                values["recent_average"], 2
            ),
            "Change": round(values["change"], 2),
            "Direction": values["direction"]
        })

    st.dataframe(
        pd.DataFrame(comparison_data),
        use_container_width=True,
        hide_index=True
    )


# ==========================================================
# 11. PATTERN DETECTION
# ==========================================================

st.markdown("---")
st.markdown("## Symptom relationship analysis")

st.caption(
    "Explores whether two recorded dimensions tend to vary "
    "together across check-ins. Correlation does not demonstrate "
    "cause, clinical significance, or a thyroid-related mechanism."
)

patterns = detect_patterns(df)

if len(df) < 5:

    st.info(
        "At least five check-ins are needed to explore "
        "descriptive relationships."
    )

elif patterns:

    for pattern in patterns:

        direction_text = (
            "positive relationship"
            if pattern["direction"] == "positive"
            else "negative relationship"
        )

        st.write(
            f"**{pattern['first']} and {pattern['second']}**"
        )

        st.write(
            f"Correlation: {pattern['correlation']:.2f} "
            f"({direction_text})"
        )

else:

    st.info(
        "No strong pairwise correlations (absolute correlation "
        "of 0.70 or higher) were detected in the available records."
    )


# ==========================================================
# 12. AUTOMATED INSIGHT ENGINE
# ==========================================================

st.markdown("---")
st.markdown("## Automated symptom insight summary")

st.caption(
    "This observation engine uses transparent statistical "
    "calculations and predefined rules. It does not use a "
    "trained diagnostic model or make medical predictions."
)

insight_lines = generate_insight_summary(
    df,
    comparisons,
    baseline,
    patterns
)

with st.container(border=True):

    st.markdown("### Patient observation summary")

    for line in insight_lines:
        st.markdown(f"- {line}")

    st.caption(
        "Generated from the currently selected patient's "
        "recorded check-ins."
    )


# ==========================================================
# 13. LABORATORY HISTORY CONTEXT
# ==========================================================

st.markdown("---")
st.markdown("## Relationship to laboratory history")

lab_df = pd.DataFrame(
    get_lab_entries(patient_id)
)

if lab_df.empty:

    st.info(
        "No thyroid laboratory panels are recorded for this "
        "patient yet. Add results in ThyroidTrend to review "
        "both histories together."
    )

else:

    lab_df["test_date"] = pd.to_datetime(
        lab_df["test_date"]
    )

    symptom_dates = set(
        df["entry_date"].dt.date
    )

    lab_dates = set(
        lab_df["test_date"].dt.date
    )

    shared_dates = sorted(
        symptom_dates.intersection(lab_dates)
    )

    st.write(
        f"This patient has {len(lab_df)} laboratory panels "
        f"and {len(df)} symptom check-ins."
    )

    if shared_dates:

        st.write(
            f"{len(shared_dates)} date(s) contain both a "
            "symptom check-in and laboratory panel: "
            + ", ".join(
                d.isoformat() for d in shared_dates
            )
        )

    else:

        st.caption(
            "No exact same-date matches are currently recorded."
        )

    st.caption(
        "Co-occurring changes do not demonstrate that thyroid "
        "measurements caused symptoms."
    )


# ==========================================================
# 14. DOWNLOADABLE CLINICIAN DISCUSSION REPORT
# ==========================================================

st.markdown("---")
st.markdown("## Clinician discussion report")

report_lines = [
    "THYROGUARD - SYMPTOMWATCH OBSERVATION REPORT",
    "=" * 48,
    f"Report generated: {date.today().isoformat()}",
    f"Patient profile ID: {patient_id}",
    f"Number of check-ins: {len(df)}",
    (
        "Observation period: "
        f"{df['entry_date'].min().date()} to "
        f"{df['entry_date'].max().date()}"
    ),
    "",
    "LATEST RECORDED RATINGS",
]

for dimension in ALL_DIMENSIONS:

    report_lines.append(
        f"{SYMPTOM_LABELS[dimension]}: "
        f"{int(latest[dimension])}/5"
    )

report_lines.extend([
    "",
    "AUTOMATED OBSERVATIONS",
])

for line in insight_lines:
    report_lines.append(f"- {line}")

report_lines.extend([
    "",
    "CHECK-IN HISTORY",
    "Date | Energy | Fatigue | Concentration | Memory | Sleep"
])

for _, row in df.iterrows():

    report_lines.append(
        f"{row['entry_date'].date()} | "
        f"{int(row['energy'])} | "
        f"{int(row['fatigue'])} | "
        f"{int(row['concentration'])} | "
        f"{int(row['memory'])} | "
        f"{int(row['sleep'])}"
    )

report_lines.extend([
    "",
    "DISCLAIMER",
    "This project is a prototype and is not medical advice.",
    "This report summarizes subjective recorded ratings.",
    "It does not diagnose or recommend treatment."
])

report_text = "\n".join(report_lines)

st.download_button(
    label="Download symptom discussion report",
    data=report_text,
    file_name="thyroguard_symptom_report.txt",
    mime="text/plain",
    use_container_width=True
)

csv_data = df[
    [
        "entry_date",
        "energy",
        "fatigue",
        "concentration",
        "memory",
        "sleep"
    ]
].copy()

csv_data["entry_date"] = (
    csv_data["entry_date"].dt.date.astype(str)
)

st.download_button(
    label="Download symptom history (CSV)",
    data=csv_data.to_csv(index=False),
    file_name="thyroguard_symptom_history.csv",
    mime="text/csv",
    use_container_width=True
)


# ==========================================================
# 15. COMPLETE HISTORY AND RECORD MANAGEMENT
# ==========================================================

with st.expander("View complete symptom history"):

    display = df[
        [
            "entry_date",
            "energy",
            "fatigue",
            "concentration",
            "memory",
            "sleep",
            "notes"
        ]
    ].copy()

    display["entry_date"] = (
        display["entry_date"].dt.date.astype(str)
    )

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True
    )


with st.expander("Remove an incorrectly entered check-in"):

    st.warning(
        "Deleting a check-in permanently removes it "
        "from this local prototype database."
    )

    options = {
        int(row["id"]): (
            f"{row['entry_date'].date().isoformat()} "
            f"· fatigue {int(row['fatigue'])}/5 "
            f"· energy {int(row['energy'])}/5 "
            f"· record #{int(row['id'])}"
        )
        for _, row in df.iterrows()
    }

    selected_entry = st.selectbox(
        "Select check-in to delete",
        list(options.keys()),
        format_func=lambda key: options[key]
    )

    confirm_delete = st.checkbox(
        "I understand this check-in will be permanently deleted."
    )

    if st.button(
        "Delete selected check-in",
        disabled=not confirm_delete
    ):

        delete_symptom_entry(
            selected_entry,
            patient_id
        )

        st.success("Symptom check-in deleted.")
        st.rerun()


# ==========================================================
# 16. FINAL SAFETY NOTICE
# ==========================================================

st.markdown("---")

st.caption(
    "SymptomWatch implementation: patient-specific storage, "
    "longitudinal visualization, personal baseline comparison, "
    "recent-period change detection, descriptive correlation "
    "analysis, automated rule-based summaries and downloadable "
    "reports. No diagnostic prediction is made."
)

st.caption(
    "This project is a prototype and is not medical advice."
)
