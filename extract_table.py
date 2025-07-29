"""
extract_table.py

Extracts the atmospheric conditions table from one or more PDF reports
and saves the combined results to a single CSV file.

Usage:
    python extract_table.py path/to/report1.pdf path/to/report2.pdf ...
    python extract_table.py reports/*.pdf   # all reports in the folder

Output:
    outputs/all_atmospheric_data.csv

Each row includes a 'Report' column with the source filename.
Requires: pandas, and extract functions from src/extract.py
"""




import sys
import os
import pandas as pd
from src.extract import extract_atmospheric_table

def parse_table_to_dataframe(table_text: str, report_name: str) -> pd.DataFrame:
    columns = ["Location", "Relative Humidity", "Air Temp", "Dew Point", "Specific Humidity"]
    data = []

    for line in table_text.splitlines():
        parts = line.strip().split()
        if len(parts) >= 5:
            location = " ".join(parts[:-4])
            row = [report_name, location] + parts[-4:]
            data.append(row)

    return pd.DataFrame(data, columns=["Report"] + columns)

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_table.py <pdf1> <pdf2> ...")
        return

    os.makedirs("outputs", exist_ok=True)
    output_path = "outputs/all_atmospheric_data.csv"
    all_rows = []

    for pdf_path in sys.argv[1:]:
        report_name = os.path.splitext(os.path.basename(pdf_path))[0]

        try:
            table_text = extract_atmospheric_table(pdf_path)

            if not table_text:
                print(f"⚠️  No table found in: {pdf_path}")
                continue

            df = parse_table_to_dataframe(table_text, report_name)
            all_rows.append(df)
            print(f"✅ Extracted from: {pdf_path}")
        except Exception as e:
            print(f"❌ Error with {pdf_path}: {e}")

    # Combine all tables and save
    if all_rows:
        combined = pd.concat(all_rows, ignore_index=True)
        combined.to_csv(output_path, index=False)
        print(f"\n📦 Master CSV saved to: {output_path}")
    else:
        print("⚠️  No data extracted from any reports.")

if __name__ == "__main__":
    main()
