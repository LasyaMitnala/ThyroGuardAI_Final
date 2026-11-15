
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = ROOT / "models" / "thyroid_classifier.joblib"


# --------------------------------------------------
# MODEL FEATURE CONFIGURATION
# --------------------------------------------------

FEATURES = [
    f"attribute_{i}" for i in range(1, 22)
]


CLASS_DESCRIPTIONS = {
    1: "Normal / not hypothyroid",
    2: "Hyperfunction",
    3: "Subnormal functioning",
}


# --------------------------------------------------
# LOAD TRAINED MODEL
# --------------------------------------------------

@st.cache_resource
def load_model():

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_PATH}"
        )

    model = joblib.load(MODEL_PATH)

    expected_features = getattr(
        model,
        "n_features_in_",
        None
    )

    if expected_features != 21:
        raise ValueError(
            f"Expected 21 model features, "
            f"but found {expected_features}."
        )

    return model


# --------------------------------------------------
# RUN RANDOM FOREST PREDICTION
# --------------------------------------------------

def predict_record(values):

    if len(values) != 21:
        raise ValueError(
            "ThyroAI requires exactly 21 input features."
        )

    values = np.asarray(
        values,
        dtype=float
    )

    if not np.isfinite(values).all():
        raise ValueError(
            "All input values must be finite numbers."
        )

    model = load_model()

    input_data = pd.DataFrame(
        [values],
        columns=FEATURES
    )

    prediction = int(
        model.predict(input_data)[0]
    )

    probabilities = None

    if hasattr(model, "predict_proba"):

        raw_probabilities = model.predict_proba(
            input_data
        )[0]

        probabilities = {
            int(label): float(probability)
            for label, probability in zip(
                model.classes_,
                raw_probabilities
            )
        }

    return prediction, probabilities
