
"""Research-only three-class thyroid classifier using paired UCI allhypo/allhyper files.

Run from project root: python -m ml.train_multiclass_thyroid
This model is not validated for clinical diagnosis or treatment decisions.
"""
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, classification_report,
    confusion_matrix, f1_score,
)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raw" / "uci_thyroid"
OUT = ROOT / "models"

FEATURES = [
    "age", "sex", "on_thyroxine", "query_on_thyroxine",
    "on_antithyroid_medication", "sick", "pregnant", "thyroid_surgery",
    "i131_treatment", "query_hypothyroid", "query_hyperthyroid", "lithium",
    "goitre", "tumor", "hypopituitary", "psych", "tsh_measured", "tsh",
    "t3_measured", "t3", "tt4_measured", "tt4", "t4u_measured", "t4u",
    "fti_measured", "fti", "tbg_measured", "tbg", "referral_source",
]

NUMERIC = ["age", "tsh", "t3", "tt4", "t4u", "fti"]
MODEL_FEATURES = [feature for feature in FEATURES if feature != "tbg"]
CATEGORICAL = [feature for feature in MODEL_FEATURES if feature not in NUMERIC]

LABELS = ["negative", "hypothyroid", "hyperthyroid"]

VALID_LABELS = {
    "hypo": {
        "negative", "hypothyroid", "primary hypothyroid",
        "compensated hypothyroid", "secondary hypothyroid",
    },
    "hyper": {
        "negative", "hyperthyroid", "t3 toxic", "toxic goitre",
        "secondary toxic", "goitre", "primary hyperthyroid",
    },
}


def read_file(filename, family):
    path = DATA / filename

    if not path.is_file():
        raise FileNotFoundError(f"Missing dataset: {path}")

    df = pd.read_csv(
        path,
        header=None,
        names=FEATURES + ["diagnosis"],
        na_values=["?"],
        dtype=str,
        skipinitialspace=True,
    )

    if df.shape[1] != len(FEATURES) + 1:
        raise ValueError(
            f"Unexpected number of columns in {filename}"
        )

    parts = (
        df["diagnosis"]
        .str.strip()
        .str.rsplit("|", n=1, expand=True)
    )

    if (
        parts.shape[1] != 2
        or parts[1].isna().any()
        or parts[1].str.strip().eq("").any()
    ):
        raise ValueError(f"Missing record IDs in {filename}")

    df["record_id"] = parts[1].str.strip()

    if df["record_id"].duplicated().any():
        raise ValueError(f"Duplicate record IDs in {filename}")

    df["raw_label"] = (
        parts[0].str.strip().str.rstrip(".").str.lower()
    )

    unexpected = (
        set(df["raw_label"].dropna()) - VALID_LABELS[family]
    )

    if unexpected or df["raw_label"].isna().any():
        raise ValueError(
            f"Unexpected {family} labels in {filename}: "
            f"{unexpected}. Verify dataset documentation."
        )

    for col in NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in CATEGORICAL:
        df[col] = df[col].map(
            lambda v: v.strip()
            if isinstance(v, str)
            else np.nan
        )

    df["family_label"] = np.where(
        df["raw_label"].eq("negative"),
        "negative",
        family,
    )

    return df


def combine_split(split):
    suffix = ".data" if split == "train" else ".test"

    hypo = read_file(
        "allhypo" + suffix, "hypo"
    ).set_index("record_id", drop=False)

    hyper = read_file(
        "allhyper" + suffix, "hyper"
    ).set_index("record_id", drop=False)

    if set(hypo.index) != set(hyper.index):
        raise ValueError(
            f"{split}: allhypo and allhyper record IDs do not match"
        )

    a = hypo.loc[
        sorted(hypo.index), MODEL_FEATURES
    ].reset_index(drop=True)

    b = hyper.loc[
        sorted(hyper.index), MODEL_FEATURES
    ].reset_index(drop=True)

    mismatch = ~(a.eq(b) | (a.isna() & b.isna()))

    if mismatch.to_numpy().any():
        raise ValueError(
            f"{split}: {int(mismatch.any(axis=1).sum())} "
            "paired records have different input features"
        )

    paired = pd.DataFrame({
        "hypo": hypo["family_label"],
        "hyper": hyper["family_label"],
    })

    conflicts = paired[
        paired["hypo"].eq("hypo")
        & paired["hyper"].eq("hyper")
    ]

    if not conflicts.empty:
        raise ValueError(
            f"{split}: {len(conflicts)} records "
            "have conflicting positive labels"
        )

    labels = np.select(
        [
            paired["hypo"].eq("hypo"),
            paired["hyper"].eq("hyper"),
        ],
        ["hypothyroid", "hyperthyroid"],
        default="negative",
    )

    result = hypo.copy()

    result["target"] = pd.Series(
        labels, index=paired.index
    ).loc[result.index]

    print(f"\n{split.upper()} paired IDs: {len(result)}")
    print(result["target"].value_counts().to_string())

    return result


def feature_keys(frame):
    # Missing-aware fingerprints for identical feature patterns.
    return (
        frame[MODEL_FEATURES]
        .astype("string")
        .fillna("<MISSING>")
        .agg("\x1f".join, axis=1)
    )


def make_pipeline():
    preprocessor = ColumnTransformer([
        (
            "numeric",
            SimpleImputer(strategy="median"),
            NUMERIC,
        ),
        (
            "categorical",
            Pipeline([
                (
                    "imputer",
                    SimpleImputer(strategy="most_frequent"),
                ),
                (
                    "onehot",
                    OneHotEncoder(handle_unknown="ignore"),
                ),
            ]),
            CATEGORICAL,
        ),
    ])

    return Pipeline([
        ("preprocessor", preprocessor),
        (
            "classifier",
            RandomForestClassifier(
                n_estimators=300,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            ),
        ),
    ])


def evaluate(model, X, y):
    predictions = model.predict(X)

    return {
        "records": int(len(y)),
        "class_counts": {
            k: int(v)
            for k, v in y.value_counts().items()
        },
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
                labels=LABELS,
                average="macro",
                zero_division=0,
            )
        ),
        "labels": LABELS,
        "confusion_matrix": confusion_matrix(
            y,
            predictions,
            labels=LABELS,
        ).tolist(),
        "classification_report": classification_report(
            y,
            predictions,
            labels=LABELS,
            output_dict=True,
            zero_division=0,
        ),
    }


def main():
    train = combine_split("train")
    test = combine_split("test")

    id_overlap = (
        set(train["record_id"]) & set(test["record_id"])
    )

    if id_overlap:
        raise ValueError(
            f"{len(id_overlap)} record IDs appear "
            "in both train and test"
        )

    train_keys = feature_keys(train)
    test_keys = feature_keys(test)

    cross = set(train_keys) & set(test_keys)

    overlap_train = train_keys.isin(cross)
    overlap_test = test_keys.isin(cross)

    print(
        f"\nIdentical feature patterns across train/test: "
        f"{len(cross)}"
    )

    print(
        "Records involved: "
        f"train={int(overlap_train.sum())}, "
        f"test={int(overlap_test.sum())}"
    )

    if cross:
        overlap_rows = pd.concat([
            pd.DataFrame({
                "feature_key": train_keys[
                    overlap_train
                ].to_numpy(),
                "target": train.loc[
                    overlap_train, "target"
                ].to_numpy(),
                "partition": "train",
            }),
            pd.DataFrame({
                "feature_key": test_keys[
                    overlap_test
                ].to_numpy(),
                "target": test.loc[
                    overlap_test, "target"
                ].to_numpy(),
                "partition": "test",
            }),
        ], ignore_index=True)

        conflicts = (
            overlap_rows
            .groupby("feature_key")["target"]
            .nunique()
        )

        conflict_count = int(
            (conflicts > 1).sum()
        )

        print("Overlap labels by partition:")

        print(
            overlap_rows.groupby(
                ["partition", "target"]
            ).size().to_string()
        )

        print(
            f"Patterns with conflicting labels: "
            f"{conflict_count}"
        )

        if conflict_count:
            raise ValueError(
                "Identical input patterns have conflicting "
                "diagnoses across partitions"
            )

    # Group identical inputs together for validation.
    X = train[MODEL_FEATURES]
    y = train["target"]

    X_test = test[MODEL_FEATURES]
    y_test = test["target"]

    if set(LABELS) - set(y):
        raise ValueError(
            "Training set does not contain all three classes"
        )

    splitter = StratifiedGroupKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    fit_idx, val_idx = next(
        splitter.split(
            X,
            y,
            groups=train_keys.to_numpy(),
        )
    )

    X_fit = X.iloc[fit_idx]
    X_val = X.iloc[val_idx]

    y_fit = y.iloc[fit_idx]
    y_val = y.iloc[val_idx]

    if (
        set(y_fit) != set(LABELS)
        or set(y_val) != set(LABELS)
    ):
        raise ValueError(
            "Grouped validation split is missing a class; "
            "change the split seed"
        )

    print(
        f"\nGrouped validation: "
        f"train={len(X_fit)}, "
        f"validation={len(X_val)}"
    )

    validation_model = make_pipeline()
    validation_model.fit(X_fit, y_fit)

    validation = evaluate(
        validation_model,
        X_val,
        y_val,
    )

    # Fit final model on full official training partition.
    final_model = make_pipeline()
    final_model.fit(X, y)

    official_test = evaluate(
        final_model,
        X_test,
        y_test,
    )

    # Sensitivity analysis: exclude test records with
    # identical feature patterns in the training set.
    clean_mask = ~overlap_test.to_numpy()

    X_test_clean = X_test.iloc[
        np.flatnonzero(clean_mask)
    ]

    y_test_clean = y_test.iloc[
        np.flatnonzero(clean_mask)
    ]

    if (
        X_test_clean.empty
        or set(y_test_clean) != set(LABELS)
    ):
        raise ValueError(
            "Overlap-free test set is empty "
            "or missing a class"
        )

    overlap_free_test = evaluate(
        final_model,
        X_test_clean,
        y_test_clean,
    )

    report = {
        "dataset": "Paired UCI allhypo and allhyper",
        "task": (
            "Three-category historical thyroid "
            "record classification"
        ),
        "features": MODEL_FEATURES,
        "train_counts": {
            k: int(v)
            for k, v in y.value_counts().items()
        },
        "test_counts": {
            k: int(v)
            for k, v in y_test.value_counts().items()
        },
        "shared_feature_patterns": len(cross),
        "overlapping_train_records": int(
            overlap_train.sum()
        ),
        "overlapping_test_records": int(
            overlap_test.sum()
        ),
        "validation": validation,
        "test": official_test,
        "overlap_free_test": overlap_free_test,
        "limitations": [
            "Historical research dataset; not clinically validated",
            "Negative label is not proof of normal thyroid function",
            "Overlap-free test excludes exact feature matches, "
            "not all possible patient-level leakage",
            "No independent external cohort",
            "Clinical input units and feature definitions "
            "must be verified before patient-facing inference",
        ],
    }

    OUT.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_path = (
        OUT / "clinical_thyroid_three_class.joblib"
    )

    report_path = (
        OUT / "three_class_evaluation_report.json"
    )

    joblib.dump(
        final_model,
        model_path,
    )

    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    for name, metrics in [
        ("GROUPED VALIDATION", validation),
        ("OFFICIAL TEST", official_test),
        ("OVERLAP-FREE TEST", overlap_free_test),
    ]:
        print(f"\n{name}")

        print(
            json.dumps(
                {
                    k: v
                    for k, v in metrics.items()
                    if k != "classification_report"
                },
                indent=2,
            )
        )

    print(f"\nSaved model: {model_path}")
    print(f"Saved report: {report_path}")


if __name__ == "__main__":
    main()
