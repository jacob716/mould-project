from PyPDF2 import PdfReader
import pdfplumber

def extract_raw_text(pdf_path: str) -> str:
    """Extract raw text from PDF using pdfplumber."""
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def clean_raw_text(raw_text: str) -> str:
    """Clean out footers, boilerplate, and irrelevant sections from the extracted text."""

    # Remove known footer phrases
    FOOTER_LINES = [
        "Cornerstone Technical Report",
        "© Cornerstone Management Services Ltd 2009.",
        "Reg Office: 24 Picton House Hussar Court Westside View Waterlooville Hants PO7 7SQ",
        "Tel: 0344 846 0955 E: enquiries@cornerstone-ltd.co.uk W: www.cornerstone-ltd.co.uk",
        "No part of this document is to be reproduced without the prior consent of Cornerstone Management Services Ltd."
    ]

    text_lines = raw_text.splitlines()
    filtered_lines = [line for line in text_lines if line.strip() not in FOOTER_LINES]
    cleaned_text = "\n".join(filtered_lines)

    def remove_section_range(text: str, from_section: str, to_section: str) -> str:
        """
        Removes everything from `from_section` up to (but not including) `to_section`,
        regardless of whitespace, newlines, etc.
        """
        start = text.find(from_section)
        end = text.find(to_section, start)

        if start != -1 and end != -1:
            return text[:start] + text[end:]
        return text  # if either not found, return unmodified

    # cleaned_text = remove_section_range(cleaned_text, "4.0 Property Profile", "5.0 Thermal")
    # cleaned_text = remove_section_range(cleaned_text, "5.0 Thermal", "6.0")

    def extract_section_range(text: str, from_section: str, to_section: str) -> str:
        start = text.find(from_section)
        end = text.find(to_section, start)

        if start != -1 and end != -1:
            return text[start:end].strip()
        return ""  # or return full text / raise error

    section_1_to_3 = extract_section_range(cleaned_text, "1.0 Property:", "4.0 Moisture")


    return section_1_to_3.strip()

def extract_full_text(pdf_path: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    FOOTER_LINES = [
        "Cornerstone Technical Report",
        "© Cornerstone Management Services Ltd 2009.",
        "Reg Office: 24 Picton House Hussar Court Westside View Waterlooville Hants PO7 7SQ",
        "Tel: 0344 846 0955 E: enquiries@cornerstone-ltd.co.uk W: www.cornerstone-ltd.co.uk",
        "No part of this document is to be reproduced without the prior consent of Cornerstone Management Services Ltd."
    ]

    text_lines = full_text.splitlines()
    filtered_lines = [line for line in text_lines if line.strip() not in FOOTER_LINES]
    cleaned_text = "\n".join(filtered_lines)

    return cleaned_text.strip()

def extract_conclusion_section(pdf_path: str) -> str | None:
    """
    Extracts the 'Conclusion' section from a PDF file.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        The conclusion text as a string, or None if not found.
    """
    reader = PdfReader(pdf_path)
    full_text = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"



    # Look for "Conclusion" section
    if "3.0 Conclusion:" in full_text:
        parts = full_text.split("3.0 Conclusion:", 1)
        conclusion_block = parts[1]

        # Cut off at 3.1 Recommendations if it exists
        if "3.1 Recommendations" in conclusion_block:
            conclusion_block = conclusion_block.split("3.1 Recommendations", 1)[0]

        FOOTER_LINES = [
        "Cornerstone Technical R eport",
        "© Cornerstone Management Services Ltd 2009.",
        "Reg Office: 24  Picton House Hussar Court Westside View Waterlooville  Hants PO 7 7SQ",
        "Tel: 0 344 846 0955    E: enquiries@cornerstone -ltd.co.uk    W: www.cornerstone -ltd.co.uk",
        "No part of this document is to be reproduced without the prior consent of Cornerstone Management Services Ltd."
        ]

        # Remove any lines that exactly match known footer lines
        conclusion_lines = conclusion_block.splitlines()
        filtered_lines = [line for line in conclusion_lines if line.strip() not in FOOTER_LINES]
        conclusion_block = "\n".join(filtered_lines)


        return conclusion_block.strip()


    return None

def extract_atmospheric_conditions(pdf_path: str) -> str:

    raw_text = extract_raw_text(pdf_path)
        # Remove known footer phrases
    FOOTER_LINES = [
        "Cornerstone Technical Report",
        "© Cornerstone Management Services Ltd 2009.",
        "Reg Office: 24 Picton House Hussar Court Westside View Waterlooville Hants PO7 7SQ",
        "Tel: 0344 846 0955 E: enquiries@cornerstone-ltd.co.uk W: www.cornerstone-ltd.co.uk",
        "No part of this document is to be reproduced without the prior consent of Cornerstone Management Services Ltd."
    ]

    text_lines = raw_text.splitlines()
    filtered_lines = [line for line in text_lines if line.strip() not in FOOTER_LINES]
    cleaned_text = "\n".join(filtered_lines)

    import re

    """
    Finds the first '4.x Atmospheric conditions' section and removes all text before it.
    """
    # Match any 4.x Atmospheric conditions section (e.g. 4.1–4.6)
    match = re.search(r"4\.[0-9]\s+Atmospheric conditions", cleaned_text)

    if not match:
        return ""  # Or return raw_text if you'd rather keep everything if no match found

    return cleaned_text[match.start():].strip()

import re

def extract_atmospheric_table(pdf_path: str) -> str:
    """
    Extracts only the data rows from the atmospheric conditions table.
    Skips the column headers and unit lines.
    """
    raw_text = extract_raw_text(pdf_path)
    def is_section_heading(line):
        return re.match(r"^\d+\.\d+(\s+\w+|:)", line.strip())

    def is_paragraph(line):
        return len(line.strip()) > 50 and re.match(r"^[A-Z]", line.strip())

    FOOTER_LINES = [
        "Cornerstone Technical Report",
        "© Cornerstone Management Services Ltd 2009.",
        "Reg Office: 24 Picton House Hussar Court Westside View Waterlooville Hants PO7 7SQ",
        "Tel: 0344 846 0955 E: enquiries@cornerstone-ltd.co.uk W: www.cornerstone-ltd.co.uk",
        "No part of this document is to be reproduced without the prior consent of Cornerstone Management Services Ltd."
    ]

    # Remove footer lines
    lines = [line for line in raw_text.splitlines() if line.strip() not in FOOTER_LINES]

    table_lines = []
    capture = False
    skipped_header = False
    skipped_units = False

    for line in lines:
        stripped = line.strip()

        # Detect the table header line
        if not capture and re.search(r"Location\s+Relative Humidity.*Specific Humidity", stripped):
            capture = True
            continue  # skip the header line

        if capture:
            if not skipped_units and re.match(r"^[%°CcGKkg/\s.]+$", stripped):
                skipped_units = True  # Skip unit-only line
                continue

            if is_section_heading(stripped) or is_paragraph(stripped) or stripped == "":
                break  # Stop at next section or blank or paragraph

            table_lines.append(line)

    return "\n".join(table_lines).strip()
