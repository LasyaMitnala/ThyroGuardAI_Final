
from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "raw" / "uci_thyroid"
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(exist_ok=True)

FEATURES = [
    "age", "sex", "on_thyroxine", "query_on_thyroxine",
    "on_antithyroid_medication", "sick", "pregnant",
    "thyroid_surgery", "i131_treatment", "query_hypothyroid",
    "query_hyperthyroid", "lithium", "goitre", "tumor",
    "hypopituitary", "psych", "tsh_measured", "tsh",
    "t3_measured", "t3", "tt4_measured", "tt4",
    "t4u_measured", "t4u", "fti_measured", "fti",
    "tbg_measured", "tbg", "referral_source"
]

# TBG is entirely missing in the training data.
MODEL_FEATURES = [
    feature for feature in FEATURES if feature != "tbg"
]

NUMERIC = [
    "age", "tsh", "t3", "tt4", "t4u", "fti"
]

CATEGORICAL = [
    feature for feature in MODEL_FEATURES
    if feature not in NUMERIC
]


def load_data(filename):
    df = pd.read_csv(
        DATA_DIR / filename,
        header=None,
        names=FEATURES + ["diagnosis"],
        na_values=["?"]
    )

    diagnosis = (
        df["diagnosis"]
        .str.split("|", regex=False)
        .str[0]
        .str.rstrip(".")
        .str.strip()
    )

    valid = {
        "negative",
        "hypothyroid",
        "primary hypothyroid",
        "compensated hypothyroid",
        "secondary hypothyroid"
    }

    if not set(diagnosis).issubset(valid):
        raise ValueError(
            f"Unexpected labels: {set(diagnosis) - valid}"
        )

    df["target"] = (diagnosis != "negative").astype(int)

    for column in NUMERIC:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

    return df


def build_pipeline():
    numeric = Pipeline([
        ("imputer", SimpleImputer(strategy="median"))
    ])

    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer([
        ("numeric", numeric, NUMERIC),
        ("categorical", categorical, CATEGORICAL)
    ])

    classifier = RandomForestClassifier(
        n_estimators=300,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    return Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", classifier)
    ])


def evaluate(model, X, y):
    predictions = model.predict(X)

    return {
        "accuracy": float(accuracy_score(y, predictions)),
        "balanced_accuracy": float(
            balanced_accuracy_score(y, predictions)
        ),
        "precision": float(
            precision_score(y, predictions, zero_division=0)
        ),
        "recall": float(
            recall_score(y, predictions, zero_division=0)
        ),
        "f1": float(
            f1_score(y, predictions, zero_division=0)
        ),
        "confusion_matrix": confusion_matrix(
            y, predictions, labels=[0, 1]
        ).tolist()
    }


def main():
    train = load_data("allhypo.data")
    test = load_data("allhypo.test")

    X = train[MODEL_FEATURES]
    y = train["target"]

    X_test = test[MODEL_FEATURES]
    y_test = test["target"]

    X_fit, X_val, y_fit, y_val = train_test_split(
        X, y,
        test_size=0.2,
        stratify=y,
        random_state=42
    )

    model = build_pipeline()
    model.fit(X_fit, y_fit)

    validation = evaluate(model, X_val, y_val)

    print("\nVALIDATION RESULTS")
    print(json.dumps(validation, indent=2))

    # Refit on the full official training dataset.
    final_model = build_pipeline()
    final_model.fit(X, y)

    test_results = evaluate(
        final_model, X_test, y_test
    )

    print("\nOFFICIAL TEST RESULTS")
    print(json.dumps(test_results, indent=2))

    print("\nCLASSIFICATION REPORT")
    print(
        classification_report(
            y_test,
            final_model.predict(X_test),
            target_names=["Negative", "Hypothyroid"],
            zero_division=0
        )
    )

    model_path = (
        MODEL_DIR / "clinical_hypothyroid_binary.joblib"
    )

    report_path = (
        MODEL_DIR / "binary_hypothyroid_report.json"
    )

    joblib.dump(final_model, model_path)

    report = {
        "dataset": "UCI allhypo",
        "task": "Binary hypothyroid classification",
        "features": MODEL_FEATURES,
        "validation": validation,
        "test": test_results,
        "limitations": [
            "Historical research dataset",
            "Not clinically validated",
            "Not a medical diagnosis"
        ]
    }

    with open(report_path, "w") as f:
        json.dump(report, f, indent=4)

    print("\nMODEL SAVED:", model_path)
    print("REPORT SAVED:", report_path)


if __name__ == "__main__":
    main()
