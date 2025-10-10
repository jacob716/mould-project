import os
import pandas as pd
import re

# import both extractors
from src.extract import extract_full_text, extract_conclusion_section

# ========= CONFIG =========
PDF_FOLDER = "reports"                   # folder with your PDFs
OUTPUT_CSV = "reports_with_conclusions.csv"
# ==========================

rows = []

for fname in os.listdir(PDF_FOLDER):
    if fname.endswith(".pdf"):
        pdf_path = os.path.join(PDF_FOLDER, fname)
        try:
            conclusion_text = extract_conclusion_section(pdf_path)
            rows.append({"filename": fname, "conclusion": conclusion_text})
            print(f"✅ Extracted conclusion from {fname}")
        except Exception as e:
            print(f"⚠️ Failed on {fname}: {e}")
            rows.append({"filename": fname, "conclusion": ""})

# Save to CSV
df = pd.DataFrame(rows)
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

print(f"\n✅ Finished. Extracted conclusions for {len(df)} reports → saved to {OUTPUT_CSV}")
