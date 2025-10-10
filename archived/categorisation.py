"""
SUMMARY:
This script classifies and standardises text fields in the merged report dataset
into consistent, structured categories.

PROCESS OVERVIEW:
1. Loads the merged CSV file (e.g. merged_reports_batch2.csv).
2. Sends relevant text fields (property type, ventilation, window type, and cause)
   to the OpenAI model for classification based on predefined categories.
3. Receives structured JSON responses containing standardised values.
4. Adds new "_categorised" columns to the DataFrame.
5. Saves the result as a new CSV (e.g. merged_reports_categorised_batch2.csv).

OUTPUT CSV COLUMNS (added):
- property_type_categorised
- ventilation_categorised
- window_type_categorised
- cause_primary
- cause_secondary

NOTES:
- This step should be run *after* merging the extracted and cause-classified CSVs.
- It produces a dataset ready for analysis and visualisation.
"""


import os
import json
import pandas as pd
from openai import OpenAI

# ====== CONFIG ======
CSV_FOLDER = "csv_files"
INPUT_CSV = os.path.join(CSV_FOLDER, "merged_reports_batch2.csv")
OUTPUT_CSV = os.path.join(CSV_FOLDER, "merged_reports_categorised_batch2.csv")
MODEL = "gpt-4o"  # full GPT-4o model
# ====================

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_TEMPLATE = """
You are a classifier for housing survey reports.
From the provided text, classify into the following categories:

- property_type: one of ["detached", "semi-detached/end terrace", "mid terrace", "ground floor flat", "flat", "other", "not mentioned"]
- ventilation: one of ["natural ventilation", "extract ventilation", "PIV", "continuous mechanical ventilation", "MVHR", "other", "not mentioned"]
- window_type: one of ["uPVC", "timber", "uPVC and timber", "aluminium", "other", "not mentioned"]
- cause_primary: one of ["poor ventilation", "residual construction moisture", "rising damp", "external moisture penetration", "internal leaks/plumbing", "insufficient heating", "lifestyle factors", "other/unclear"]
- cause_secondary: one of ["poor ventilation", "residual construction moisture", "rising damp", "external moisture penetration", "internal leaks/plumbing", "insufficient heating", "lifestyle factors", "other/unclear", "none"]

Definitions for causes:
- poor ventilation → condensation, high humidity, closed trickle vents, ineffective extract fans, lack of airflow.
- residual construction moisture → leftover dampness from recent building or renovation work that has not yet dried out.
- rising damp → ground moisture moving upward into walls/skirtings due to failed or missing damp proof course (low-level, up to ~1m).
- external moisture penetration → rain ingress, water through cracks, defective membranes or roofs letting moisture in from outside.
- internal leaks/plumbing → leaks from pipes, plumbing, bathrooms, or internal water sources.
- insufficient heating → lack of adequate heating leading to cold surfaces and condensation.
- lifestyle factors → drying clothes indoors, placing furniture against walls, clutter blocking airflow, occupant behaviour (not related to heating).
- other/unclear → vague, mixed, or unspecified causes that do not clearly fit the above.

Rules:
- cause_primary = the main cause of damp/mould.
- cause_secondary = a secondary contributing cause, or "none" if not applicable.
- If both natural and mechanical ventilation are present, choose the mechanical system.
- If extract ventilation is present together with another mechanical system (PIV, continuous, MVHR), choose the non-extract system.
- "Forced ventilation" in kitchens or bathrooms should be treated as extract ventilation.
- Only use "other/unclear" if the text clearly does not fit into any category.

Return only valid JSON in this format:
{{
  "property_type": "...",
  "ventilation": "...",
  "window_type": "...",
  "cause_primary": "...",
  "cause_secondary": "..."
}}

Text:
PROPERTY TYPE: {property_text}
VENTILATION: {ventilation_text}
WINDOW TYPE: {window_text}
CAUSE: {cause_text}
"""

def classify_row(property_text, ventilation_text, window_text, cause_text):
    prompt = PROMPT_TEMPLATE.format(
        property_text=property_text,
        ventilation_text=ventilation_text,
        window_text=window_text,
        cause_text=cause_text
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"}  # ensures JSON only
    )

    return json.loads(response.choices[0].message.content)


def main():
    df = pd.read_csv(INPUT_CSV)

    categories = []
    for i, row in df.iterrows():
        print(f"Processing row {i+1}/{len(df)}...")
        result = classify_row(
            row.get("property_type", ""),
            row.get("ventilation", ""),
            row.get("window_type", ""),
            row.get("cause", "")
        )
        categories.append(result)

    cats_df = pd.DataFrame(categories)

    # 🔹 Rename specific columns to add _categorised
    cats_df = cats_df.rename(columns={
        "property_type": "property_type_categorised",
        "ventilation": "ventilation_categorised",
        "window_type": "window_type_categorised"
    })

    df_out = pd.concat([df, cats_df], axis=1)

    df_out.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Categorised CSV saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
