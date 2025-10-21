# Mould Project

This project automates the analysis of damp and mould survey reports.
It extracts structured data from PDF survey reports and classifies the likely cause of issues using OpenAI models.

## Pipeline

1. **Download reports**
   Place survey PDF files into the `/reports` folder.

2. **Extract main data**
   Run `bulkextract_v2.py` to extract property data into a CSV.
   - Output: `extracted_reports_v2.csv`
   - Configurable: `OUTPUT_CSV`, `MODEL`

3. **Classify cause of issue**
   Run `classify_reports.py` to produce a CSV of causes using OpenAI.
   - Output: e.g. `classified_causes.csv`
   - Configurable: `OUTPUT_CSV`, `MODEL`

4. **Merge results**
   Run `merge_csv.py` to combine both CSVs into a single dataset.
   - Output: `merged_reports.csv`

## Setup

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your_api_key"


