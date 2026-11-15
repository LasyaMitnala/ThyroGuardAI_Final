import streamlit as st
import pandas as pd
from utils.navigation import render_sidebar
from datetime import datetime, timezone


from utils.ui import load_css, page_header
from utils.patient_context import patient_sidebar
from ml.thyroai_engine import (
    predict_record,
    CLASS_DESCRIPTIONS,
    load_model,
)

st.set_page_config(
    page_title="ThyroAI | ThyroGuard",
    page_icon="🧠",
    layout="wide",
)

load_css()

render_sidebar()

page_header(
    "ThyroAI",
    "A research-oriented thyroid-function classification using your trained Random Forest model."
)

st.warning(
    "Research prototype only. This tool does not diagnose thyroid disease, "
    "recommend treatment, or replace a qualified clinician. "
    "This project is a prototype and is not medical advice."
)

st.markdown(
    """
    The existing Random Forest was trained on the UCI ANN Thyroid Disease
    dataset. It expects 21 features in the original dataset order. The model
    was trained on the dataset's scaled continuous values, so this form asks
    for values on that same dataset scale—not ordinary laboratory units.
    """
)

with st.expander("What is being classified?", expanded=True):
    st.markdown(
        """
        - **Class 1:** Normal / Not hypothyroid
        - **Class 2:** Hyperthyroid
        - **Class 3:** Hypothyroid

        These are the dataset's original categories. They are research labels,
        not a personal medical diagnosis.
        """
    )

try:
    model = load_model()
    st.success(
        f"Model loaded successfully · {type(model.named_steps['model']).__name__} · "
        f"{model.named_steps['model'].n_estimators} trees · 21 features"
    )
except Exception as exc:
    st.error(f"Could not load the trained model: {exc}")
    st.stop()

st.subheader("Enter a dataset-compatible record")
st.caption(
    "Use documented source values where available. Do not guess unknown "
    "medical history or enter ordinary lab units into scaled-value fields."
)

with st.form("thyroai_assessment_form"):
    st.markdown("#### 1. Demographic features")
    c1, c2 = st.columns(2)
    with c1:
        age_scaled = st.number_input(
            "Age (Divide your age by 100, e.g., 30 years = 0.30)", min_value=0.0, max_value=1.0,
            value=0.50, step=0.01,
            help="The ANN dataset stores age on a scaled 0–1-like range. Do not enter age in years here."
        )
    with c2:
        sex = st.selectbox(
            "Sex/Gender",
            options=[0, 1],
            format_func=lambda x: "0 — Male" if x == 0 else "1 — Female",
        )

st.markdown("#### 2. Your medical history")
st.caption(
    "Answer the following questions based on your medical history. "
    "Your responses help ThyroAI analyze patterns in your health information."
)
    
binary_labels = [
    ("on_thyroxine", "Are you currently taking thyroid hormone medication?"),
    ("query_on_thyroxine", "Has a healthcare provider discussed starting thyroid hormone medication with you?"),
    ("on_antithyroid_medication", "Are you currently taking medication to reduce thyroid hormone production?"),
    ("sick", "Were you experiencing an illness when your laboratory tests were taken?"),
    ("pregnant", "Are you currently pregnant?"),
    ("thyroid_surgery", "Have you previously had thyroid surgery?"),
    ("i131_treatment", "Have you received radioactive iodine treatment for a thyroid condition?"),
    ("query_hypothyroid", "Has a healthcare provider raised concerns about an underactive thyroid?"),
    ("query_hyperthyroid", "Has a healthcare provider raised concerns about an overactive thyroid?"),
    ("lithium", "Are you currently taking lithium medication?"),
    ("goitre", "Have you been diagnosed with an enlarged thyroid (goiter)?"),
    ("tumor", "Have you been diagnosed with a thyroid tumor?"),
    ("hypopituitary", "Have you been diagnosed with reduced pituitary gland function?"),
    ("psych", "Do you have a history of a mental health condition?")
]

binary_values = []
cols = st.columns(2)

for i, (key, label) in enumerate(binary_labels):
    with cols[i % 2]:
        val = st.selectbox(
            label,
            options=[0, 1],
            format_func=lambda x: "No" if x == 0 else "Yes",
            key=f"thyroai_{key}",
        )
        binary_values.append(int(val))
         


    st.markdown("#### 3. Laboratory features")
    st.info(
        "These are normalized dataset values, not standard clinical units. "
        "Only enter values that have been converted to the exact ANN dataset scale."
    )
    lab_specs = [
        ("TSH", 0.0, 0.53, 0.05, "attribute_17"),
        ("T3", 0.0005, 0.18, 0.02, "attribute_18"),
        ("TT4", 0.002, 0.60, 0.10, "attribute_19"),
        ("T4U", 0.017, 0.233, 0.10, "attribute_20"),
        ("FTI", 0.002, 0.642, 0.10, "attribute_21"),
    ]
    lab_values = []
    cols = st.columns(2)
    for i, (name, low, high, default, key) in enumerate(lab_specs):
        with cols[i % 2]:
            value = st.number_input(
                f"{name} (dataset scale)",
                min_value=float(low),
                max_value=float(high),
                value=float(default),
                format="%.6f",
                key=f"thyroai_{key}",
                help="Enter the dataset-scaled value, not a value copied directly from a clinical lab report."
            )
            lab_values.append(float(value))

    submitted = st.form_submit_button(
        "Run research classification",
        type="primary",
        use_container_width=True,
    )

if submitted:
    # Training feature order:
    # age, sex, 14 binary indicators, then TSH, T3, TT4, T4U, FTI.
    record = [float(age_scaled), float(sex)] + [float(v) for v in binary_values] + lab_values
    try:
        predicted_class, probabilities = predict_record(record)
        result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "patient_id": active_patient_id,
            "predicted_class": predicted_class,
            "label": CLASS_DESCRIPTIONS.get(predicted_class, f"Dataset class {predicted_class}"),
        }
        st.session_state.setdefault("thyroai_history", [])
        st.session_state["thyroai_history"].insert(0, result)

        st.divider()
        st.subheader("Research classification output")
        st.metric("Predicted dataset category", result["label"])
        st.caption(
            f"Original target label: {predicted_class}. "
            "This is a model classification of the supplied dataset-style record, not a diagnosis."
        )

        if probabilities is not None:
            probability_rows = [
                {
                    "Dataset category": CLASS_DESCRIPTIONS.get(k, str(k)),
                    "Model probability": v,
                }
                for k, v in probabilities.items()
            ]
            probability_df = pd.DataFrame(probability_rows)
            st.markdown("#### Model probability output")
            st.bar_chart(
                probability_df.set_index("Dataset category")["Model probability"]
            )
            st.caption(
                "These are model probability outputs, not calibrated clinical confidence "
                "or an individual's probability of having a disease."
            )

        st.info(
            "Interpret this result only as an experimental classification within "
            "the historical UCI dataset's label system. Discuss health concerns "
            "and laboratory results with a qualified clinician."
        )
    except Exception as exc:
        st.error(f"Prediction could not be completed: {exc}")

st.divider()
st.subheader("Recent ThyroAI session history")
history = st.session_state.get("thyroai_history", [])
if history:
    history_df = pd.DataFrame(history)
    st.dataframe(
        history_df[["timestamp", "patient_id", "predicted_class", "label"]],
        use_container_width=True,
        hide_index=True,
    )
    st.caption(
        "This history is stored only in the current browser session. "
        "It is not yet saved to the SQLite database."
    )
else:
    st.caption("No assessments have been run in this session.")

st.caption(
    "Dataset: UCI ANN Thyroid Disease · Historical data (1992) · "
    "Research classification only · This project is a prototype and is not medical advice."
)
