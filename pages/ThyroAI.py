
"""ThyroAI — three-class thyroid research interface.

Run from project root:
    streamlit run app.py

Uses:
    models/clinical_thyroid_three_class.joblib

Research only. Not a clinical diagnostic system.
"""

from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

from utils.navigation import render_sidebar
from utils.ui import load_css, page_header


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="ThyroAI | ThyroGuard",
    page_icon="🧠",
    layout="wide",
)

load_css()
render_sidebar()

page_header(
    "ThyroAI",
    "Explore thyroid laboratory patterns using our "
    "experimental three-class research model.",
)

ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = (
    ROOT / "models" / "clinical_thyroid_three_class.joblib"
)

MODEL_FEATURES = [
    "age", "sex", "on_thyroxine", "query_on_thyroxine",
    "on_antithyroid_medication", "sick", "pregnant",
    "thyroid_surgery", "i131_treatment",
    "query_hypothyroid", "query_hyperthyroid",
    "lithium", "goitre", "tumor", "hypopituitary",
    "psych", "tsh_measured", "tsh", "t3_measured",
    "t3", "tt4_measured", "tt4", "t4u_measured",
    "t4u", "fti_measured", "fti", "tbg_measured",
    "referral_source",
]

CLASS_LABELS = {
    "negative": "Negative dataset category",
    "hypothyroid": "Hypothyroid dataset category",
    "hyperthyroid": "Hyperthyroid dataset category",
}

HISTORY = [
    (
        "on_thyroxine",
        "Taking thyroid hormone replacement medication",
    ),
    (
        "query_on_thyroxine",
        "Thyroid hormone treatment under consideration",
    ),
    (
        "on_antithyroid_medication",
        "Taking antithyroid medication",
    ),
    ("sick", "Ill at the time of testing"),
    ("pregnant", "Pregnant at the time of testing"),
    ("thyroid_surgery", "History of thyroid surgery"),
    ("i131_treatment", "History of radioactive iodine treatment"),
    (
        "query_hypothyroid",
        "Hypothyroidism under clinical consideration",
    ),
    (
        "query_hyperthyroid",
        "Hyperthyroidism under clinical consideration",
    ),
    ("lithium", "Taking lithium at the time of testing"),
    ("goitre", "History of enlarged thyroid (goiter)"),
    ("tumor", "History of tumor"),
    ("hypopituitary", "History of reduced pituitary function"),
    ("psych", "Psychiatric condition recorded in history"),
]

LABS = [
    ("tsh", "TSH", "Thyroid-stimulating hormone"),
    ("t3", "T3", "Triiodothyronine"),
    ("tt4", "TT4", "Total thyroxine"),
    ("t4u", "T4U", "Thyroxine uptake"),
    ("fti", "FTI", "Free thyroxine index"),
]

REFERRAL_SOURCES = [
    "Unknown / not recorded",
    "SVHC",
    "SVI",
    "SVHD",
    "STMW",
    "other",
]


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def categorical_answer(answer):
    return {
        "Yes": "t",
        "No": "f",
        "Not sure": np.nan,
    }[answer]


def parse_optional_number(value, field_name):
    value = value.strip()

    if not value:
        return np.nan

    try:
        result = float(value)
    except ValueError:
        raise ValueError(
            f"{field_name} must be a number or left blank."
        )

    if not np.isfinite(result):
        raise ValueError(
            f"{field_name} must be a finite number."
        )

    if result < 0:
        raise ValueError(
            f"{field_name} cannot be negative."
        )

    return result


@st.cache_resource(show_spinner=False)
def get_model():
    return joblib.load(MODEL_PATH)


def prepare_record(age, sex, history, labs, referral):
    record = {
        feature: np.nan
        for feature in MODEL_FEATURES
    }

    record["age"] = age
    record["sex"] = sex

    for key, value in history.items():
        record[key] = value

    for key, value in labs.items():
        record[key] = value
        record[f"{key}_measured"] = (
            "f" if pd.isna(value) else "t"
        )

    record["tbg_measured"] = "f"
    record["referral_source"] = referral

    return pd.DataFrame(
        [record],
        columns=MODEL_FEATURES,
    )


def format_score(value):
    return f"{value * 100:.1f}%"


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "thyroai_history" not in st.session_state:
    st.session_state.thyroai_history = []

if "thyroai_result" not in st.session_state:
    st.session_state.thyroai_result = None


# --------------------------------------------------
# INTRODUCTION
# --------------------------------------------------

st.warning(
    "Research prototype only. This tool does not "
    "diagnose, screen for, or rule out thyroid disease. "
    "Do not use its results to make medical decisions."
)

st.markdown(
    """
    ThyroAI explores patterns in historical thyroid records
    using a machine-learning model trained on paired
    **UCI allhypo and allhyper datasets**.

    The model predicts one of three historical dataset labels:

    - Negative
    - Hypothyroid
    - Hyperthyroid

    **Negative does not mean medically confirmed normal.**
    Model scores are not calibrated probabilities of disease.
    """
)

with st.expander("About this research model"):
    st.markdown(
        """
        **Algorithm:** Random Forest classifier

        **Training records:** 2,800

        **Official test records:** 972

        **Reported test accuracy:** 98.66%

        **Reported balanced accuracy:** 91.73%

        **Reported macro F1:** 92.12%

        These figures describe performance on historical
        records, not clinical performance on new patients.

        The model requires the original dataset's feature
        definitions, categorical codes, and measurement
        conventions. These have not yet been fully verified
        for use with modern patient laboratory reports.
        """
    )


# --------------------------------------------------
# MODEL LOADING
# --------------------------------------------------

if not MODEL_PATH.is_file():
    st.error(
        "The three-class model was not found at:\n\n"
        f"{MODEL_PATH}"
    )
    st.stop()

try:
    model = get_model()

    if not hasattr(model, "predict_proba"):
        raise TypeError(
            "The saved model does not support predict_proba."
        )

except Exception as exc:
    st.error(
        "The research model could not be loaded. "
        f"Details: {exc}"
    )
    st.stop()


# --------------------------------------------------
# ASSESSMENT FORM
# --------------------------------------------------

st.divider()

st.subheader("New research assessment")

st.caption(
    "Use de-identified research records only. "
    "Do not enter names, addresses, or other identifiers."
)

with st.form("thyroai_assessment_form"):

    st.markdown("#### 1. Record information")

    col1, col2 = st.columns(2)

    with col1:
        age_input = st.text_input(
            "Age in years",
            placeholder="Example: 35",
        )

    with col2:
        sex_input = st.selectbox(
            "Sex as coded in the UCI dataset",
            ["Not recorded", "Female (F)", "Male (M)"],
        )

    st.divider()

    st.markdown("#### 2. Medical history")

    st.caption(
        "Select Not sure when the information is "
        "missing or not recorded."
    )

    history_answers = {}

    left, right = st.columns(2)

    for index, (key, question) in enumerate(HISTORY):
        column = left if index % 2 == 0 else right

        with column:
            answer = st.selectbox(
                question,
                ["Not sure", "No", "Yes"],
                key=f"history_{key}",
            )

            history_answers[key] = categorical_answer(
                answer
            )

    st.divider()

    st.markdown("#### 3. Thyroid laboratory measurements")

    st.info(
        "**Research Model — Important Information**\n\n"
        "ThyroAI is an experimental machine-learning tool and is not "
        "intended for medical diagnosis. Laboratory measurements must "
        "match the model's original dataset conventions. Compatibility "
        "with standard clinical lab reports has not yet been verified."
    )

    lab_inputs = {}

    for key, short_name, description in LABS:
        col1, col2 = st.columns([1, 2])

        with col1:
            value = st.text_input(
                short_name,
                placeholder="Leave blank if unavailable",
                key=f"lab_{key}",
            )

            lab_inputs[key] = value

        with col2:
            st.caption(description)

    st.divider()

    acknowledged = st.checkbox(
        "I understand that this is an experimental "
        "research classifier, not a medical assessment, "
        "and that my input values must follow the "
        "original dataset's coding conventions."
    )

    submitted = st.form_submit_button(
        "Run research classification",
        type="primary",
        use_container_width=True,
    )


# --------------------------------------------------
# RUN PREDICTION
# --------------------------------------------------

if submitted:

    if not acknowledged:
        st.error(
            "Please acknowledge the research limitations "
            "before running the model."
        )

    else:
        try:
            age = parse_optional_number(
                age_input,
                "Age",
            )

            labs = {}

            for key, short_name, _ in LABS:
                labs[key] = parse_optional_number(
                    lab_inputs[key],
                    short_name,
                )

            sex = {
                "Not recorded": np.nan,
                "Female (F)": "F",
                "Male (M)": "M",
            }[sex_input]

            referral = np.nan

            input_df = prepare_record(
                age=age,
                sex=sex,
                history=history_answers,
                labs=labs,
                referral=referral,
            )

            predicted = str(
                model.predict(input_df)[0]
            )

            probabilities = model.predict_proba(
                input_df
            )[0]

            classes = [
                str(value)
                for value in model.classes_
            ]

            scores = {
                label: float(probability)
                for label, probability in zip(
                    classes,
                    probabilities,
                )
            }

            timestamp = datetime.now(
                timezone.utc
            ).strftime("%Y-%m-%d %H:%M UTC")

            result = {
                "timestamp": timestamp,
                "prediction": predicted,
                "scores": scores,
                "input": input_df.iloc[0].to_dict(),
            }

            st.session_state.thyroai_result = result

            # Store results in session only.
            st.session_state.thyroai_history.append({
                "Timestamp": timestamp,
                "Dataset classification": predicted,
                "Negative score": scores.get(
                    "negative", 0.0
                ),
                "Hypothyroid score": scores.get(
                    "hypothyroid", 0.0
                ),
                "Hyperthyroid score": scores.get(
                    "hyperthyroid", 0.0
                ),
            })

        except ValueError as exc:
            st.error(str(exc))

        except Exception as exc:
            st.error(
                "The research classification could "
                f"not be completed: {exc}"
            )


# --------------------------------------------------
# RESULTS DASHBOARD
# --------------------------------------------------

result = st.session_state.thyroai_result

if result is not None:

    st.divider()

    st.subheader("Research classification results")

    predicted = result["prediction"]
    scores = result["scores"]

    st.caption(
        f"Assessment completed: {result['timestamp']}"
    )

    st.info(
        "Predicted historical dataset category: "
        f"**{CLASS_LABELS.get(predicted, predicted)}**"
    )

    st.markdown("#### Model classification scores")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Negative",
            format_score(
                scores.get("negative", 0.0)
            ),
        )

    with col2:
        st.metric(
            "Hypothyroid",
            format_score(
                scores.get("hypothyroid", 0.0)
            ),
        )

    with col3:
        st.metric(
            "Hyperthyroid",
            format_score(
                scores.get("hyperthyroid", 0.0)
            ),
        )

    score_df = pd.DataFrame({
        "Category": [
            "Negative",
            "Hypothyroid",
            "Hyperthyroid",
        ],
        "Model score": [
            scores.get("negative", 0.0),
            scores.get("hypothyroid", 0.0),
            scores.get("hyperthyroid", 0.0),
        ],
    })

    st.bar_chart(
        score_df.set_index("Category"),
        y="Model score",
    )

    st.caption(
        "These are Random Forest classification scores, "
        "not calibrated medical probabilities."
    )

    st.markdown("#### Laboratory values supplied")

    lab_rows = []

    for key, short_name, description in LABS:
        value = result["input"].get(key)

        lab_rows.append({
            "Test": short_name,
            "Description": description,
            "Value": (
                "Not recorded"
                if pd.isna(value)
                else str(value)
            ),
        })

    st.dataframe(
        pd.DataFrame(lab_rows),
        hide_index=True,
        use_container_width=True,
    )

    st.warning(
        "This result cannot establish whether thyroid "
        "function is normal or abnormal. Clinical "
        "interpretation requires appropriate laboratory "
        "reference ranges, medical history, and "
        "professional evaluation."
    )


# --------------------------------------------------
# ASSESSMENT HISTORY
# --------------------------------------------------

st.divider()

st.subheader("Assessment history")

history = st.session_state.thyroai_history

if history:

    history_df = pd.DataFrame(history)

    st.dataframe(
        history_df,
        hide_index=True,
        use_container_width=True,
    )

    csv_data = history_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "Export session history as CSV",
        data=csv_data,
        file_name="thyroai_research_history.csv",
        mime="text/csv",
    )

    if st.button("Clear assessment history"):
        st.session_state.thyroai_history = []
        st.session_state.thyroai_result = None
        st.rerun()

else:
    st.caption(
        "No assessments have been completed "
        "in this session."
    )

st.caption(
    "Session history is temporary and is not "
    "saved to a patient database."
)
