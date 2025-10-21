import os
import json
import pandas as pd
from openai import OpenAI
from src.extract import extract_body_without_conclusion, extract_body_without_conclusion_or_recommendations  # your new function
import re

# ====== CONFIG ======
PDF_FOLDER = "reports"   # Folder with your PDFs
OUTPUT_CSV = "analysis.csv"
MODEL = "gpt-4o-mini"
LIMIT = None   # set to None to process all files
# ====================

# Initialize API client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Prompt template for cause analysis
ANALYSIS_PROMPT = """
You are analysing damp and mould survey reports.
From the following report text, identify what you believe are the main cause(s) of the reported issues.

Guidelines:
- Write a clear explanation in a short paragraph (1–4 sentences).
- Focus on the underlying causes, not just the symptoms (e.g. say "poor ventilation leading to condensation" instead of just "condensation").
- If multiple factors are relevant, mention them all.
- Keep the answer factual and concise. Do not include recommendations or suggested fixes.
- Do not mention that you are an AI model.

Return your answer as valid JSON only, with this format:

{{
  "analysis": "your explanation here"
}}

Report text:
\"\"\"{report_text}\"\"\"
"""


# ---------- Helpers ----------

def extract_json(text):
    """Attempts to clean and extract valid JSON from the model's response."""
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.IGNORECASE)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None
    return None


def process_report(pdf_path):
    body_text = extract_body_without_conclusion_or_recommendations(pdf_path)
    prompt = ANALYSIS_PROMPT.format(report_text=body_text)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"}
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
    if LIMIT:
        pdf_files = pdf_files[:LIMIT]

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
