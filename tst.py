import pandas as pd


df = pd.read_csv(
    "output/processed/migr_asydcfsta_processed.csv",
    dtype={"value_raw": str, "flag": str},
    low_memory=False
)

rows_with_b = df[df["value_raw"].str.contains(r"\bb\b", na=False)]

print("Rows with b in value_raw:", len(rows_with_b))
print("Rows with flag b:", (df["flag"] == "b").sum())

print(rows_with_b[["value_raw", "metric_value", "flag"]].head(20))