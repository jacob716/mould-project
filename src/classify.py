import subprocess

def classify_issue(conclusion_text: str, model: str = "mistral") -> str:
    """
    Sends the conclusion text to a local LLM (Ollama) for classification.

    Returns the predicted category as a string.
    """


    prompt = f"""
    You are a damp and mould inspection expert. Read the conclusion below and classify the primary cause into ONE of the following categories:

    - Condensation-related mould
    - Structural damp
    - Ventilation deficiency
    - Insulation/thermal bridging
    - Surface mould (non-structural)
    - Mixed causes
    - No issue detected

    Return ONLY the category. No explanations or extra output.

    Conclusion:
    {conclusion_text}
    """.strip()

    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode(),
        capture_output=True,
    )
    output = result.stdout.decode().strip()
    return output


def identify_features(full_text: str, model: str = "mistral") -> str:
    prompt = f"""
Extract the following fields from the property inspection report below. Your response **must be valid JSON** with exactly these fields.
If a value is not mentioned in the report, return "not mentioned" for that field.

Instructions per field:
- **postcode**: The postcode of the property if mentioned
- **property_type**: A short description of the type of property (e.g. "semi-detached 2-bedroom maisonette")
- **wall_type**: Wall construction type (e.g. cavity wall, solid wall, timber frame)
- **age**: Construction age of the building if stated (e.g. 1950s, early 2000s)
- **orientation**: The compass direction (north, east, south, west) of any wall or room affected by mould
- **ventilation**: Description of ventilation present (e.g. extractors, trickle vents, passive vents)
- **window_type**: Type of windows in the property (e.g. uPVC, single-glazed, double-glazed)
- **ducting_length**: Length or quality of ducting if stated, or "not mentioned"
- **people**: Number of people living in the property, or general description (e.g. family of 4)
- **pets**: Number/type of pets if mentioned (e.g. 2 dogs), or "not mentioned"
- **drying_clothes**: Whether clothes are dried indoors
- **where_else_is_mould**: Other locations in the property where mould was found or mentioned
- **solution**: Summary of recommended actions or solutions from the report
- **date_of_survey**: Date the inspection took place, if available

Format your response **exactly** like this:

### START_JSON
{{
  "postcode": "...",
  "property_type": "...",
  "wall_type": "...",
  "age": "...",
  "orientation": "...",
  "ventilation": "...",
  "window_type": "...",
  "ducting_length": "...",
  "people": "...",
  "pets": "...",
  "drying_clothes": "...",
  "where_else_is_mould": "...",
  "solution": "...",
  "date_of_survey": "..."
}}
### END_JSON

Do **not** include explanations, markdown, or commentary — only return the JSON block.

Report:
\"\"\"
{full_text}
\"\"\"
    """

    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode(),
        capture_output=True,
    )
    output = result.stdout.decode().strip()
    return output
