import os
import pandas as pd

# import your improved function
from src.extract import extract_full_text   # replace with the actual file name

# ========= CONFIG =========
PDF_FOLDER = "reports"   # path to your folder with PDFs
OUTPUT_CSV = "csv_files/raw_reports.csv"
# ==========================

rows = []

for fname in os.listdir(PDF_FOLDER):
    if fname.endswith(".pdf"):
        pdf_path = os.path.join(PDF_FOLDER, fname)
        try:
            text = extract_full_text(pdf_path)
            rows.append({"filename": fname, "text": text})
            print(f"✅ Extracted {fname}")
        except Exception as e:
            print(f"⚠️ Failed on {fname}: {e}")
            rows.append({"filename": fname, "text": ""})

# Save to CSV
df = pd.DataFrame(rows)
df.to_csv(OUTPUT_CSV, index=False)

print(f"\n✅ Finished. Extracted {len(df)} reports → saved to {OUTPUT_CSV}")
