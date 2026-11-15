
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raw" / "uci_thyroid"

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

def load(filename):
    df = pd.read_csv(
        DATA / filename,
        header=None,
        names=FEATURES + ["diagnosis"],
        na_values=["?"]
    )

    df["target"] = (
        df["diagnosis"]
        .str.split("|", regex=False)
        .str[0]
        .str.rstrip(".")
    )

    return df

train = load("allhypo.data")
test = load("allhypo.test")

print("\nMISSING VALUES BY FEATURE")
print(train[FEATURES].isna().sum().to_string())

print("\nDUPLICATE FEATURE ROWS")
print("Training:", train[FEATURES].duplicated().sum())
print("Testing:", test[FEATURES].duplicated().sum())

train_rows = set(
    map(tuple, train[FEATURES].fillna("__MISSING__").to_numpy())
)

test_rows = set(
    map(tuple, test[FEATURES].fillna("__MISSING__").to_numpy())
)

print("\nTRAIN/TEST FEATURE OVERLAP")
print("Identical feature patterns:", len(train_rows & test_rows))

print("\nBINARY CLASS DISTRIBUTION")
for name, df in [("Training", train), ("Testing", test)]:
    binary = (df["target"] != "negative").astype(int)
    print(name)
    print(binary.value_counts().sort_index().to_string())
