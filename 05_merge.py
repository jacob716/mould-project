"""
SUMMARY:
Merges extracted data, causes, analysis, and heating system info into one complete dataset.
"""

import pandas as pd

# ====== CONFIG ======
EXTRACTED_CSV = "extracted_reports.csv"
CAUSES_CSV = "classified_causes.csv"
ANALYSIS_CSV = "analysis.csv"
HEATING_CSV = "heating_systems.csv"
OUTPUT_CSV = "merged_columns.csv"
# ====================

# Load all dataframes
df_extracted = pd.read_csv(EXTRACTED_CSV)
df_causes = pd.read_csv(CAUSES_CSV)
df_analysis = pd.read_csv(ANALYSIS_CSV)
df_heating = pd.read_csv(HEATING_CSV)

# Merge on filename
df_merged = (
    df_extracted
    .merge(df_causes, on="filename", how="left")
    .merge(df_analysis, on="filename", how="left")
    .merge(df_heating, on="filename", how="left")
)

df_merged.to_csv(OUTPUT_CSV, index=False)
print(f"✅ Fully merged CSV saved to {OUTPUT_CSV}")
print(f"📊 Shape: {df_merged.shape}")
print(f"🧱 Columns: {list(df_merged.columns)}")
