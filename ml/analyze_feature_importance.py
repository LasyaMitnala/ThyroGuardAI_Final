
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.inspection import permutation_importance
from sklearn.metrics import f1_score

ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "data" / "raw" / "uci_thyroid"
MODEL_PATH = ROOT / "models" / "thyroid_classifier.joblib"
OUTPUT = ROOT / "models" / "feature_importance.csv"

# Load the saved original model.
model = joblib.load(MODEL_PATH)

# Use a held-out validation subset of the official
# training file, rather than repeatedly analyzing
# the official test dataset.
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

# IMPORTANT:
# The saved model was trained on all official training
# records, including these rows.
# This is an exploratory TRAINING-set analysis,
# not an independent validation estimate.

print("Calculating exploratory feature importance...")

result = permutation_importance(
    model,
    X,
    y,
    scoring="f1_macro",
    n_repeats=5,
    random_state=42,
    n_jobs=-1
)

importance = pd.DataFrame({
    "feature": X.columns,
    "importance_mean": result.importances_mean,
    "importance_std": result.importances_std
})

importance = importance.sort_values(
    "importance_mean",
    ascending=False
)

importance.to_csv(OUTPUT, index=False)

print("\nTOP 10 IMPORTANT FEATURES")
print(importance.head(10).to_string(index=False))

print("\nResults saved to:")
print(OUTPUT)
