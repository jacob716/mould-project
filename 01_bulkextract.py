"""
SUMMARY:
This script performs bulk extraction of key details from PDF property inspection reports.

PROCESS OVERVIEW:
1. Reads each PDF in the specified folder (e.g. reports/batch2).
2. Extracts the full report text using PyMuPDF (fitz).
3. Sends the text to the OpenAI model to extract structured fields in JSON format.
4. Compiles the extracted data into a single DataFrame.
5. Saves the final results as a CSV file (e.g. 'extracted_reports_batch2.csv').

OUTPUT CSV COLUMNS:
- filename
- property_type
- wall_type
- age
- issue_type
- orientation
- ventilation
- window_type
- occupancy
- drying_clothes
- main_issue_location
- secondary_issue_locations

NOTES:
- Any field not mentioned in the report is set to "not mentioned".
- This script should be run before other scripts that classify causes or perform analysis.
"""



import os
import json
import pandas as pd
import fitz  # PyMuPDF for PDF text extraction
from openai import OpenAI

# ====== CONFIG ======
PDF_FOLDER = "reports"  # Folder where your PDFs are stored
OUTPUT_CSV = "test_extracted_reports.csv"
MODEL = "gpt-4o-mini"  # Or "gpt-5-thinking" for extra reasoning
# ====================

# Initialize API client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Your extraction instructions
EXTRACTION_PROMPT = """
Extract the following fields from the property inspection report below.
Your response MUST be valid JSON with exactly these fields:
- property_type: A short description of the type of property (e.g. "semi-detached 2-bedroom maisonette")
- wall_type: Return only one of the following values — "solid", "cavity", "timber", or "not mentioned"
- age: Construction age of the building if stated (e.g. 1950s, early 2000s)
- issue_type: Classify the issue as "mould", "damp", "both", or "not mentioned"
- orientation: The compass direction (north, east, south, west) of any wall or room affected by mould or damp
- ventilation: Description of ventilation present (e.g. extractors, trickle vents, passive vents)
- window_type: Type of windows in the property (e.g. uPVC, single-glazed, double-glazed)
- occupancy: A description of the people and pets living in the property (e.g. "2 adults and 1 dog")
- drying_clothes: Whether clothes are dried indoors. Return either "yes", "no, or "not mentioned"
- main_issue_location: the room(s) where the damp or mould problem is most severe or emphasised. If unclear, return "not mentioned". Limit to 1–2 rooms.
- secondary_issue_locations: other rooms where damp or mould is mentioned but less central. If none, return "not mentioned".

If a value is not mentioned, return "not mentioned" for that field.

Return only the JSON, no explanations.
Report:
\"\"\"{report_text}\"\"\"
"""


# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text("text") + "\n"
    return text.strip()
import re

def extract_json(text):
    """
    Attempts to clean and extract valid JSON from the model's response.
    - Strips code fences and extra text
    - Finds the first JSON-looking block
    """
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
    text = extract_text_from_pdf(pdf_path)
    prompt = EXTRACTION_PROMPT.format(report_text=text)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw = response.choices[0].message.content
    print(f"🔍 Model raw output from {pdf_path}:\n{raw}\n---")  # Optional debugging

    data = extract_json(raw)
    if not data:
        print(f"⚠️ JSON parse error for {pdf_path}, skipping.")
        return None

    return data



# Main loop
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
        print(f"✅ Extraction complete! Saved to {OUTPUT_CSV}")
    else:
        print("⚠️ No results to save.")

if __name__ == "__main__":
    main()
