
from pathlib import Path
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import (
    StratifiedKFold,
    cross_validate
)

ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "data" / "raw" / "uci_thyroid"

df = pd.read_csv(
    DATA / "ann-train.data",
    sep=r"\s+",
    header=None
)

X = df.iloc[:, :21].copy()
y = df.iloc[:, 21].astype(int)

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

models = {
    "Original Random Forest": RandomForestClassifier(
        n_estimators=400,
        class_weight="balanced",
        random_state=42,
        n_jobs=1
    ),

    "Optimized Random Forest": RandomForestClassifier(
        n_estimators=300,
        max_depth=20,
        min_samples_split=2,
        min_samples_leaf=1,
        max_features="log2",
        class_weight="balanced",
        random_state=42,
        n_jobs=1
    )
}

for name, model in models.items():

    print(f"\nEvaluating {name}...")

    scores = cross_validate(
        model,
        X,
        y,
        cv=cv,
        scoring={
            "macro_f1": "f1_macro",
            "balanced_accuracy": "balanced_accuracy",
            "accuracy": "accuracy"
        },
        n_jobs=-1
    )

    print("Mean macro F1:",
          round(np.mean(scores["test_macro_f1"]), 4))

    print("Macro F1 standard deviation:",
          round(np.std(scores["test_macro_f1"]), 4))

    print("Mean balanced accuracy:",
          round(np.mean(scores["test_balanced_accuracy"]), 4))

    print("Mean accuracy:",
          round(np.mean(scores["test_accuracy"]), 4))

print("\nComparison complete.")

