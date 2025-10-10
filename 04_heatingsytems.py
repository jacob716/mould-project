import pandas as pd
import re

INPUT_CSV = "csv_files/raw_reports.csv"
OUTPUT_CSV = "heating_systems.csv"

# Define heating keywords and categories
HEATING_KEYWORDS = {
    "Gas central heating": [r"\bgas\b", r"combi", r"boiler"],
    "Oil or LPG central heating": [r"\boil\b", r"\blpg\b"],
    "Biomass central heating": [r"biomass", r"wood[- ]?burn", r"pellet"],
    "Heat pump": [r"heat pump", r"air source", r"ground source"],
    "Electric storage heaters or radiators": [
        r"storage heater",
        r"electric radiator",
        r"panel heater"
    ],
}

def find_heating_system(text):
    if not isinstance(text, str):
        return "Not mentioned"
    text = text.lower()
    found = []
    for category, patterns in HEATING_KEYWORDS.items():
        for pat in patterns:
            if re.search(pat, text):
                found.append(category)
                break  # stop after first match within this category
    if not found:
        return "Not mentioned"
    return "; ".join(found)

# Load reports
df = pd.read_csv(INPUT_CSV)

# Apply finder
df["heating_system"] = df["text"].apply(find_heating_system)

# Save only filename + heating_system
df[["filename", "heating_system"]].to_csv(
    OUTPUT_CSV, index=False, encoding="utf-8-sig"
)

print(f"✅ Done! Heating systems saved to {OUTPUT_CSV}")
