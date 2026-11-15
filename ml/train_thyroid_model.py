
from pathlib import Path
import json

import numpy as np
import pandas as pd
import joblib

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
    f1_score
)

# --------------------------------------------------
# 1. PROJECT PATHS AND CONFIGURATION
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raw" / "uci_thyroid"
MODEL_DIR = ROOT / "models"

MODEL_DIR.mkdir(parents=True, exist_ok=True)

FEATURE_COUNT = 21
LABELS = [1, 2, 3]
RANDOM_STATE = 42


# --------------------------------------------------
# 2. LOAD DATASET
# --------------------------------------------------

def load_data(filename):
    path = DATA / filename

    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")

    df = pd.read_csv(path, sep=r"\s+", header=None)

    if df.shape[1] != 22:
        raise ValueError(
            f"{filename}: expected 22 columns, "
            f"but found {df.shape[1]}"
        )

    X = df.iloc[:, :FEATURE_COUNT].copy()
    y = df.iloc[:, FEATURE_COUNT].astype(int)

    X.columns = [
        f"attribute_{i}" for i in range(1, 22)
    ]

    if not set(y.unique()).issubset(set(LABELS)):
        raise ValueError("Unexpected target class labels found.")

    return X, y


# --------------------------------------------------
# 3. BUILD MACHINE LEARNING MODELS
# --------------------------------------------------

def build_models():

    return {
        "Random Forest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", RandomForestClassifier(
                n_estimators=400,
                class_weight="balanced",
                random_state=RANDOM_STATE,
                n_jobs=-1
            ))
        ]),

        "Logistic Regression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(
                max_iter=3000,
                class_weight="balanced",
                random_state=RANDOM_STATE
            ))
        ])
    }


# --------------------------------------------------
# 4. MODEL EVALUATION
# --------------------------------------------------

def evaluate_model(model, X_test, y_test):

    predictions = model.predict(X_test)

    cm = confusion_matrix(
        y_test,
        predictions,
        labels=LABELS
    )

    precision, recall, f1, support = (
        precision_recall_fscore_support(
            y_test,
            predictions,
            labels=LABELS,
            zero_division=0
        )
    )

    per_class = {}

    for i, label in enumerate(LABELS):

        tp = int(cm[i, i])
        fn = int(cm[i, :].sum() - tp)
        fp = int(cm[:, i].sum() - tp)
        tn = int(cm.sum() - tp - fn - fp)

        specificity = (
            tn / (tn + fp) if (tn + fp) else 0
        )

        per_class[str(label)] = {
            "true_positives": tp,
            "false_negatives": fn,
            "false_positives": fp,
            "true_negatives": tn,
            "precision": float(precision[i]),
            "sensitivity_recall": float(recall[i]),
            "specificity": float(specificity),
            "f1": float(f1[i]),
            "support": int(support[i])
        }

    return {
        "accuracy": float(
            accuracy_score(y_test, predictions)
        ),

        "balanced_accuracy": float(
            balanced_accuracy_score(y_test, predictions)
        ),

        "macro_f1": float(
            f1_score(
                y_test,
                predictions,
                average="macro"
            )
        ),

        "confusion_matrix": cm.tolist(),

        "class_metrics": per_class,

        "classification_report": classification_report(
            y_test,
            predictions,
            labels=LABELS,
            zero_division=0,
            output_dict=True
        )
    }


# --------------------------------------------------
# 5. MAIN TRAINING PIPELINE
# --------------------------------------------------

def main():

    print("\nTHYROGUARD THYROIDTREND ML PIPELINE")
    print("=" * 50)

    # Load official training and test files.
    X_train, y_train = load_data("ann-train.data")
    X_test, y_test = load_data("ann-test.data")

    print(f"Total training records: {len(X_train)}")
    print(f"Official test records: {len(X_test)}")
    print(f"Features: {X_train.shape[1]}")

    print("\nTraining class distribution:")
    print(y_train.value_counts().sort_index())

    print("\nOfficial test class distribution:")
    print(y_test.value_counts().sort_index())

    # --------------------------------------------------
    # 6. CREATE VALIDATION SPLIT
    # --------------------------------------------------

    X_fit, X_val, y_fit, y_val = train_test_split(
        X_train,
        y_train,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y_train
    )

    print("\nTraining split:", len(X_fit))
    print("Validation split:", len(X_val))

    models = build_models()
    validation_results = {}

    # --------------------------------------------------
    # 7. TRAIN AND SELECT MODEL
    # --------------------------------------------------

    for name, model in models.items():

        print(f"\nTraining {name}...")

        model.fit(X_fit, y_fit)

        validation_results[name] = evaluate_model(
            model,
            X_val,
            y_val
        )

        print(
            "Validation accuracy:",
            round(validation_results[name]["accuracy"], 4)
        )

        print(
            "Validation balanced accuracy:",
            round(
                validation_results[name]["balanced_accuracy"],
                4
            )
        )

        print(
            "Validation macro F1:",
            round(validation_results[name]["macro_f1"], 4)
        )

    # Select using validation macro F1 only.
    best_name = max(
        validation_results,
        key=lambda name: validation_results[name]["macro_f1"]
    )

    print("\nSelected model:", best_name)

    # --------------------------------------------------
    # 8. RETRAIN ON ALL OFFICIAL TRAINING DATA
    # --------------------------------------------------

    best_model = build_models()[best_name]

    best_model.fit(X_train, y_train)

    # --------------------------------------------------
    # 9. FINAL EVALUATION ON UNTOUCHED TEST DATA
    # --------------------------------------------------

    print("\nEvaluating on official test dataset...")

    test_results = evaluate_model(
        best_model,
        X_test,
        y_test
    )

    # --------------------------------------------------
    # 10. SAVE TRAINED MODEL
    # --------------------------------------------------

    model_path = MODEL_DIR / "thyroid_classifier.joblib"

    joblib.dump(best_model, model_path)

    # --------------------------------------------------
    # 11. SAVE EVALUATION REPORT
    # --------------------------------------------------

    report = {
        "dataset": "UCI ANN Thyroid Disease",
        "training_file": "ann-train.data",
        "test_file": "ann-test.data",

        "training_rows": len(X_train),
        "validation_rows": len(X_val),
        "official_test_rows": len(X_test),

        "feature_count": FEATURE_COUNT,
        "class_labels": LABELS,

        "class_label_interpretation": (
            "Original numeric labels retained. "
            "Clinical mapping requires verification."
        ),

        "selected_model": best_name,
        "selection_metric": "validation_macro_f1",

        "validation_comparison": validation_results,

        "official_test_evaluation": test_results,

        "limitations": [
            "Historical dataset collected in 1992.",
            "Not evidence of present-day clinical validity.",
            "Class labels require clinical interpretation verification.",
            "Not interchangeable with the app's TSH, FT4 and FT3 form.",
            "Research classification only; not a diagnosis."
        ]
    }

    report_path = MODEL_DIR / "evaluation_report.json"

    with open(report_path, "w") as f:
        json.dump(report, f, indent=4)

    # --------------------------------------------------
    # 12. PRINT FINAL RESULTS
    # --------------------------------------------------

    print("\n" + "=" * 50)
    print("FINAL OFFICIAL TEST RESULTS")
    print("=" * 50)

    print("Selected model:", best_name)

    print(
        "Accuracy:",
        round(test_results["accuracy"], 4)
    )

    print(
        "Balanced accuracy:",
        round(test_results["balanced_accuracy"], 4)
    )

    print(
        "Macro F1:",
        round(test_results["macro_f1"], 4)
    )

    print("\nCONFUSION MATRIX")

    print(
        np.array(test_results["confusion_matrix"])
    )

    print("\nPER-CLASS ERROR ANALYSIS")

    for label, metrics in (
        test_results["class_metrics"].items()
    ):

        print(f"\nClass {label}")

        print(
            "False negatives:",
            metrics["false_negatives"]
        )

        print(
            "False positives:",
            metrics["false_positives"]
        )

        print(
            "Sensitivity:",
            round(metrics["sensitivity_recall"], 4)
        )

        print(
            "Specificity:",
            round(metrics["specificity"], 4)
        )

    print("\nFILES SAVED SUCCESSFULLY")
    print("Model:", model_path)
    print("Evaluation:", report_path)


if __name__ == "__main__":
    main()
