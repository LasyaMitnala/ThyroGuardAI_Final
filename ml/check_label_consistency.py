
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
        .str.strip()
    )

    df["binary_target"] = (
        df["target"] != "negative"
    ).astype(int)

    return df


def make_keys(df):
    normalized = df[FEATURES].copy()

    normalized = normalized.astype("string")

    normalized = normalized.fillna(
        "__MISSING_VALUE__"
    )

    return pd.util.hash_pandas_object(
        normalized,
        index=False
    )


train = load("allhypo.data")
test = load("allhypo.test")

train["feature_key"] = make_keys(train)
test["feature_key"] = make_keys(test)

combined = pd.concat(
    [train, test],
    ignore_index=True
)

label_counts = combined.groupby(
    "feature_key"
)["binary_target"].nunique()

conflicting_keys = set(
    label_counts[label_counts > 1].index
)

overlap_keys = (
    set(train["feature_key"])
    & set(test["feature_key"])
)

overlap_test = test[
    test["feature_key"].isin(overlap_keys)
]

print("=" * 55)
print("THYROAI LABEL CONSISTENCY CHECK")
print("=" * 55)

print("\nConflicting feature patterns:")
print(len(conflicting_keys))

print("\nShared train/test feature patterns:")
print(len(overlap_keys))

print("\nTest records sharing a training feature pattern:")
print(len(overlap_test))

print("\nShared test records by binary class:")
print(
    overlap_test["binary_target"]
    .value_counts()
    .sort_index()
    .to_string()
)

print("\nConflicting shared feature patterns:")
print(
    len(overlap_keys & conflicting_keys)
)

print("\nUnique train/test record IDs:")

train_ids = (
    train["diagnosis"]
    .str.split("|", regex=False)
    .str[-1]
)

test_ids = (
    test["diagnosis"]
    .str.split("|", regex=False)
    .str[-1]
)

print("Training:", train_ids.nunique())
print("Testing:", test_ids.nunique())

print("\nCHECK COMPLETE")
