
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raw" / "uci_thyroid"

df = pd.read_csv(
    DATA / "ann-train.data",
    sep=r"\s+",
    header=None
)

df.columns = [
    f"attribute_{i}" for i in range(1, 22)
] + ["target"]

features = [
    "attribute_17",
    "attribute_21",
    "attribute_3"
]

print("=" * 55)
print("THYROAI TOP FEATURE INSPECTION")
print("=" * 55)

print("\nFEATURE STATISTICS")
print(df[features].describe().to_string())

print("\nFEATURE STATISTICS BY TARGET CLASS")

for feature in features:
    print(f"\n{feature}")
    print(
        df.groupby("target")[feature]
        .agg(["count", "mean", "std", "min", "max"])
        .round(4)
        .to_string()
    )

print("\nCORRELATION BETWEEN TOP FEATURES")
print(df[features].corr().round(4).to_string())

print("\nINSPECTION COMPLETE")
