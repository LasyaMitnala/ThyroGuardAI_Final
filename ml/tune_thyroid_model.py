
from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import (
    StratifiedKFold,
    RandomizedSearchCV
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raw" / "uci_thyroid"

RANDOM_STATE = 42

# Load official training data only.
# Keep the official test set untouched.
df = pd.read_csv(
    DATA / "ann-train.data",
    sep=r"\s+",
    header=None
)

X = df.iloc[:, :21].copy()
y = df.iloc[:, 21].astype(int)

X.columns = [
    f"attribute_{i}" for i in range(1, 22)
]

# Define the Random Forest pipeline.
pipeline = Pipeline([
    (
        "model",
        RandomForestClassifier(
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=1
        )
    )
])

# Hyperparameters to investigate.
param_distributions = {
    "model__n_estimators": [200, 300, 400, 500],
    "model__max_depth": [None, 10, 20, 30],
    "model__min_samples_split": [2, 5, 10],
    "model__min_samples_leaf": [1, 2, 4],
    "model__max_features": ["sqrt", "log2"]
}

# Stratified cross-validation preserves class proportions.
cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=RANDOM_STATE
)

search = RandomizedSearchCV(
    estimator=pipeline,
    param_distributions=param_distributions,
    n_iter=20,
    scoring="f1_macro",
    cv=cv,
    random_state=RANDOM_STATE,
    n_jobs=-1,
    verbose=1,
    refit=True
)

print("Starting ThyroAI hyperparameter tuning...")

search.fit(X, y)

print("\n" + "=" * 55)
print("THYROAI TUNING RESULTS")
print("=" * 55)

print("\nBest cross-validation macro F1:")
print(round(search.best_score_, 4))

print("\nBest hyperparameters:")
for key, value in search.best_params_.items():
    print(f"{key}: {value}")

results = pd.DataFrame(search.cv_results_)

results = results.sort_values(
    "rank_test_score"
)

output = ROOT / "models" / "tuning_results.csv"

results.to_csv(output, index=False)

print("\nTuning results saved to:")
print(output)

print("\nExisting trained model has NOT been overwritten.")
