import pandas as pd

# Paths
MAIN_CSV = "extracted_reports_batch2.csv"          # your main data
CAUSES_CSV = "classified_causes_batch2.csv"       # your cause classifications
OUTPUT_CSV = "merged_reports_batch2.csv"              # merged output

# Load both CSVs
df_main = pd.read_csv(MAIN_CSV)
df_causes = pd.read_csv(CAUSES_CSV)

# Merge on filename
df_merged = pd.merge(df_main, df_causes, on="filename", how="left")

# Save result
df_merged.to_csv(OUTPUT_CSV, index=False)

print(f"✅ Merged CSV saved to {OUTPUT_CSV}")
