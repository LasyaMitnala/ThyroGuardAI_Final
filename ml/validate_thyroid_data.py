
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raw" / "uci_thyroid"


def load_dataset(filename):
    path = DATA / filename

    if not path.exists():
        raise FileNotFoundError(f"Missing dataset: {path}")

    df = pd.read_csv(
        path,
        sep=r"\s+",
        header=None
    )

    if df.shape[1] != 22:
        raise ValueError(
            f"{filename}: expected 22 columns, "
            f"found {df.shape[1]}"
        )

    return df


train = load_dataset("ann-train.data")
test = load_dataset("ann-test.data")

print("=" * 55)
print("THYROAI DATASET VALIDATION")
print("=" * 55)

print("\nDATASET DIMENSIONS")
print("Training:", train.shape)
print("Testing:", test.shape)

print("\nDUPLICATE RECORDS")
print("Training duplicates:", train.duplicated().sum())
print("Testing duplicates:", test.duplicated().sum())

train_rows = set(map(tuple, train.to_numpy()))
test_rows = set(map(tuple, test.to_numpy()))

overlap = train_rows.intersection(test_rows)

print("\nTRAIN / TEST OVERLAP")
print("Identical records across datasets:", len(overlap))

print("\nMISSING VALUES")
print("Training missing values:", train.isna().sum().sum())
print("Testing missing values:", test.isna().sum().sum())

print("\nFEATURE TYPES")
print(train.dtypes.to_string())

print("\nCLASS DISTRIBUTION")
print("Training:")
print(train.iloc[:, -1].value_counts().sort_index())

print("\nTesting:")
print(test.iloc[:, -1].value_counts().sort_index())

print("\nVALIDATION CHECK COMPLETE")
