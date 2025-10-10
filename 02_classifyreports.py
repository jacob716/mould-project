"""
SUMMARY:
This script processes all PDF reports in the specified folder (e.g. reports/batch2)
and extracts the *primary cause* of mould/damp from each report's conclusion section.

PROCESS OVERVIEW:
1. Reads each PDF and extracts its conclusion text (using extract_conclusion_section).
2. Sends the conclusion to the OpenAI model to identify the main cause.
3. Collects results (cause + filename) into a DataFrame.
4. Saves the final output as a CSV file, e.g. 'classified_causes_batch2.csv'.

OUTPUT CSV COLUMNS:
- filename : Name of the source PDF report
- cause    : Short summary of the primary cause (≤10 words)
"""



import os
import json
import pandas as pd
from openai import OpenAI
from src.extract import extract_conclusion_section  # your function
import re

# ====== CONFIG ======
PDF_FOLDER = "reports"  # Folder with your PDFs
OUTPUT_CSV = "test_classified_causes.csv"
MODEL = "gpt-4o-mini"
# ====================

# Initialize API client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Prompt template for cause extraction (free text)
CAUSE_PROMPT = """
You are a classifier for damp and mould survey reports.
From the conclusion text below, extract the **primary cause** of the issue.

Return your answer as valid JSON only, with exactly this format:

{{
  "cause": "concise summary of the main cause (max 10 words)"
}}

Keep the cause short and to the point, e.g.:
- "condensation from inadequate ventilation"
- "residual construction moisture"
- "rain penetration through defective roof"
- "furniture blocking airflow"

Conclusion text:
\"\"\"{report_text}\"\"\"
"""


# ---------- Helpers ----------

def extract_json(text):
    """Attempts to clean and extract valid JSON from the model's response."""
    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.IGNORECASE)

    # Try full parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: find first {...} block and try again
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None
    return None

def process_report(pdf_path):
    conclusion_text = extract_conclusion_section(pdf_path)
    prompt = CAUSE_PROMPT.format(report_text=conclusion_text)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"}  # ensures JSON only
    )

    raw = response.choices[0].message.content
    print(f"🔍 Model raw output from {pdf_path}:\n{raw}\n---")

    data = extract_json(raw)
    if not data:
        print(f"⚠️ JSON parse error for {pdf_path}, skipping.")
        return None

    return data

# ---------- Main loop ----------

def main():
    all_results = []
    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]

    for pdf_file in pdf_files:
        pdf_path = os.path.join(PDF_FOLDER, pdf_file)
        print(f"📄 Processing: {pdf_file}")
        result = process_report(pdf_path)
        if result:
            result["filename"] = pdf_file
            all_results.append(result)

    if all_results:
        df = pd.DataFrame(all_results)
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"✅ Classification complete! Saved to {OUTPUT_CSV}")
    else:
        print("⚠️ No results to save.")

if __name__ == "__main__":
    main()
