
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raw" / "uci_thyroid"
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42

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

NUMERIC = [
    "age", "tsh", "t3", "tt4", "t4u", "fti", "tbg"
]

CATEGORICAL = [
    feature for feature in FEATURES
    if feature not in NUMERIC
]


def load_data(filename):
    df = pd.read_csv(
        DATA / filename,
        header=None,
        names=FEATURES + ["diagnosis"],
        na_values=["?"],
        keep_default_na=True
    )

    # The final field looks like "negative.|3733".
    # Separate the classification from the record ID.
    diagnosis_parts = df["diagnosis"].str.rsplit(
        "|", n=1, expand=True
    )

    df["target"] = (
        diagnosis_parts[0]
        .str.strip()
        .str.rstrip(".")
        .str.strip()
    )

    df["record_id"] = diagnosis_parts[1].str.strip()

    for column in NUMERIC:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


def build_preprocessor():
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_pipeline = Pipeline([
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            )
        ),
        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ])

    return ColumnTransformer([
        ("numeric", numeric_pipeline, NUMERIC),
        ("categorical", categorical_pipeline, CATEGORICAL)
    ])


def evaluate(model, X, y):
    predictions = model.predict(X)

    return {
        "accuracy": float(
            accuracy_score(y, predictions)
        ),
        "balanced_accuracy": float(
            balanced_accuracy_score(y, predictions)
        ),
        "macro_f1": float(
            f1_score(
                y,
                predictions,
                average="macro",
                zero_division=0
            )
        ),
        "classification_report": classification_report(
            y,
            predictions,
            output_dict=True,
            zero_division=0
        ),
        "confusion_matrix": confusion_matrix(
            y,
            predictions,
            labels=model.classes_
        ).tolist()
    }


def main():
    print("=" * 55)
    print("THYROAI CLINICAL MODEL TRAINING")
    print("=" * 55)

    train = load_data("allhypo.data")
    test = load_data("allhypo.test")

    print("\nTraining records:", len(train))
    print("Test records:", len(test))

    print("\nTraining class distribution:")
    print(train["target"].value_counts())

    print("\nTest class distribution:")
    print(test["target"].value_counts())

    print("\nTraining/test record ID overlap:")
    print(
        len(
            set(train["record_id"])
            & set(test["record_id"])
        )
    )

    # Exclude the record identifier and diagnosis
    # from all model inputs.
    X = train[FEATURES]
    y = train["target"]

    X_test = test[FEATURES]
    y_test = test["target"]

    X_fit, X_val, y_fit, y_val = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y
    )

    models = {
        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1
        ),
        "Logistic Regression": LogisticRegression(
            max_iter=3000,
            class_weight="balanced",
            random_state=RANDOM_STATE
        )
    }

    validation_results = {}

    for name, classifier in models.items():
        print(f"\nTraining {name}...")

        model = Pipeline([
            ("preprocessor", build_preprocessor()),
            ("classifier", classifier)
        ])

        model.fit(X_fit, y_fit)

        results = evaluate(model, X_val, y_val)
        validation_results[name] = results

        print(
            "Validation macro F1:",
            round(results["macro_f1"], 4)
        )

        print(
            "Validation balanced accuracy:",
            round(results["balanced_accuracy"], 4)
        )

    best_name = max(
        validation_results,
        key=lambda name: validation_results[name]["macro_f1"]
    )

    print("\nSelected model:", best_name)

    best_model = Pipeline([
        ("preprocessor", build_preprocessor()),
        ("classifier", models[best_name])
    ])

    best_model.fit(X, y)

    test_results = evaluate(
        best_model,
        X_test,
        y_test
    )

    print("\nOFFICIAL TEST RESULTS")
    print("Accuracy:", round(test_results["accuracy"], 4))
    print(
        "Balanced accuracy:",
        round(test_results["balanced_accuracy"], 4)
    )
    print("Macro F1:", round(test_results["macro_f1"], 4))

    print("\nPer-class performance:")
    print(
        classification_report(
            y_test,
            best_model.predict(X_test),
            zero_division=0
        )
    )

    model_path = (
        MODEL_DIR / "clinical_thyroid_classifier.joblib"
    )

    report_path = (
        MODEL_DIR / "clinical_evaluation_report.json"
    )

    joblib.dump(best_model, model_path)

    report = {
        "dataset": "UCI allhypo",
        "selected_model": best_name,
        "features": FEATURES,
        "classes": list(best_model.classes_),
        "validation_results": validation_results,
        "test_results": test_results,
        "limitations": [
            "Historical research dataset",
            "Not clinically validated",
            "Not a medical diagnosis"
        ]
    }

    with open(report_path, "w") as f:
        json.dump(report, f, indent=4)

    print("\nSaved model:", model_path)
    print("Saved evaluation:", report_path)


if __name__ == "__main__":
    main()
