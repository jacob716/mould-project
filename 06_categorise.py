"""
SUMMARY:
Classifies and standardises fields for analysis. Reads the fully merged dataset
(including conclusion 'cause' and body-only 'analysis') and outputs consistent,
analysis-ready categories.

PROCESS OVERVIEW:
1) Load merged_reports_with_analysis_batchX.csv
2) Send key text fields to the model with strict label sets
3) Receive structured JSON:
   - property_type, ventilation, window_type (categorised)
   - cause_primary, cause_secondary         (from conclusion cause)
   - analysis_primary, analysis_secondary   (from body-only analysis)
4) Append new columns and save merged_reports_categorised_batchX.csv

NOTES:
- Uses left-as-is for original text columns; only adds new categorised fields.
- analysis_* uses the same taxonomy as cause_* to enable comparison.

"""

import os
import json
import pandas as pd
from openai import OpenAI

# ====== CONFIG ======
CSV_FOLDER = "csv_files"  # use if you keep CSVs in a subfolder; otherwise set to "."
INPUT_CSV  = os.path.join(CSV_FOLDER, "merged_reports_with_analysis_batch2.csv")
OUTPUT_CSV = os.path.join(CSV_FOLDER, "merged_reports_categorised_batch2.csv")
MODEL = "gpt-4o"  # full GPT-4o model
BATCH_LIMIT = None  # e.g. 50 for a test subset; None to process all
# ====================

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_TEMPLATE = """
You are a strict classifier for housing damp/mould survey data. Map the provided
texts into the exact categories below. If a field is unclear, pick the closest
valid label (do NOT invent new labels).

Return ONLY valid JSON with EXACTLY these keys:
- property_type
- ventilation
- window_type
- cause_primary
- cause_secondary
- analysis_primary
- analysis_secondary

Allowed values:

property_type:
  ["detached", "semi-detached/end terrace", "mid terrace",
   "ground floor flat", "flat", "other", "not mentioned"]

ventilation:
  ["natural ventilation", "extract ventilation", "PIV",
   "continuous mechanical ventilation", "MVHR", "other", "not mentioned"]

window_type:
  ["uPVC", "timber", "uPVC and timber", "aluminium", "other", "not mentioned"]

cause_* and analysis_* (use the SAME taxonomy):
  ["poor ventilation", "residual construction moisture", "rising damp",
   "external moisture penetration", "internal leaks/plumbing",
   "insufficient heating", "lifestyle factors", "other/unclear", "none"]

Rules & clarifications:
- cause_primary/secondary refer to the CONCLUSION-derived CAUSE text.
- analysis_primary/secondary refer to the BODY-derived ANALYSIS text.
- If only one cause is evident, set *_secondary to "none".
- Use "poor ventilation" for condensation due to airflow/extract issues.
- "Forced ventilation" in wet rooms counts as "extract ventilation".
- If mechanical + natural are both present, prefer the mechanical label.
- Only use "other/unclear" if it clearly doesn't match any category.

Now classify:

PROPERTY TYPE (raw): {property_text}
VENTILATION (raw): {ventilation_text}
WINDOW TYPE (raw): {window_text}

CAUSE (from conclusion): {cause_text}
ANALYSIS (from body text): {analysis_text}
"""

def _safe(val: str) -> str:
    if val is None:
        return ""
    s = str(val).strip()
    return s

def classify_row(property_text, ventilation_text, window_text, cause_text, analysis_text):
    prompt = PROMPT_TEMPLATE.format(
        property_text=_safe(property_text),
        ventilation_text=_safe(ventilation_text),
        window_text=_safe(window_text),
        cause_text=_safe(cause_text),
        analysis_text=_safe(analysis_text)
    )

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"}  # enforce valid JSON
    )

    try:
        data = json.loads(resp.choices[0].message.content)
    except Exception:
        # Fallback minimal structure to avoid crashing the run
        data = {
            "property_type": "not mentioned",
            "ventilation": "not mentioned",
            "window_type": "not mentioned",
            "cause_primary": "other/unclear",
            "cause_secondary": "none",
            "analysis_primary": "other/unclear",
            "analysis_secondary": "none",
        }
    return data


def main():
    df = pd.read_csv(INPUT_CSV)

    if BATCH_LIMIT is not None:
        df = df.head(BATCH_LIMIT)

    results = []
    n = len(df)
    for i, row in df.iterrows():
        print(f"Processing {i+1}/{n} …")
        result = classify_row(
            row.get("property_type", ""),
            row.get("ventilation", ""),
            row.get("window_type", ""),
            row.get("cause", ""),      # conclusion-derived short cause text
            row.get("analysis", ""),   # body-only analysis paragraph
        )
        results.append(result)

    cats = pd.DataFrame(results)

    # Rename core feature columns to *_categorised to keep originals intact
    cats = cats.rename(columns={
        "property_type": "property_type_categorised",
        "ventilation": "ventilation_categorised",
        "window_type": "window_type_categorised",
    })

    # Concatenate with original dataframe
    df_out = pd.concat([df, cats], axis=1)

    # Save
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df_out.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Categorised CSV saved to {OUTPUT_CSV}")
    print(f"📊 Shape: {df_out.shape}")
    print("🧱 Added columns:",
          ["property_type_categorised", "ventilation_categorised", "window_type_categorised",
           "cause_primary", "cause_secondary", "analysis_primary", "analysis_secondary"])

if __name__ == "__main__":
    main()
