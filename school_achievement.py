import pandas as pd
import os

# Load your SEDA data (adjust path as needed)
seda_df = pd.read_csv("data/seda_county_long_cs_5.0.csv")

# Filter to 2019 (latest year)
seda_2019 = seda_df[seda_df["year"] == 2019]

# Select relevant columns: fips and cs_mn_all (mean achievement score for all students)
seda_2019 = seda_2019[["sedacounty", "cs_mn_all"]]

# Aggregate by fips, averaging cs_mn_all across subjects (math and reading)
seda_county = (
    seda_2019
    .groupby("sedacounty")
    .agg({"cs_mn_all": "mean"})  # Mean across mth and rla
    .reset_index()
    .rename(columns={"cs_mn_all": "school_achievement_score"})
)

# Ensure fips is a 5-digit string (e.g., "01001" for Autauga County)
seda_county["sedacounty"] = seda_county["sedacounty"].astype(str).str.zfill(5)

seda_county.rename(columns={"sedacounty": "fips"}, inplace=True)
# Display sample
print("\nPreprocessed SEDA County Data (2019 Sample):")
print(seda_county.head())

# Save to CSV
seda_county.to_csv("data/seda_county_2019.csv", index=False)
print("Data saved to 'seda_county_2019.csv'")

# Optional: Merge with your master dataset (assuming you have it loaded)
# master_df = master_df.merge(seda_county, on="fips", how="left")