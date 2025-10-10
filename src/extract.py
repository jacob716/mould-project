from PyPDF2 import PdfReader
import pdfplumber
import re
import unicodedata

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
        "No part of this document is to be reproduced without the prior consent of Cornerstone Management Services Ltd.",
        "21A Picton House, Hussar Court, Westside View, Waterlooville, Hampshire PO7 7SQ",
        "20A Picton House, Hussar Court, Westside View, Waterlooville, Hampshire, PO7 7SQ"
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
        "No part of this document is to be reproduced without the prior consent of Cornerstone Management Services Ltd.",
        "21A Picton House, Hussar Court, Westside View, Waterlooville, Hampshire PO7 7SQ",
        "20A Picton House, Hussar Court, Westside View, Waterlooville, Hampshire, PO7 7SQ",
        "Tel: 0844 846 0955 Fax: 0844 846 0956 E: enquiries@cornerstone-ltd.co.uk W: www.cornerstone-ltd.co.uk",
        "Unit 52 Broadmarsh Business & Innovation Centre, Harts Farm Way, Havant, Hants, PO9 1HS",
        "© Powered by Formworks",
        "© Cornerstone Management Services Ltd",
        "Tel: 023 9200 9270 Fax: 023 9226 2557 E: enquiries@cornerstone-ltd.co.uk W: www.cornerstone-ltd.co.uk"
    ]

    FOOTER_PATTERNS = [
        r"Cornerstone",            # company name
        r"©",                      # copyright
        r"Tel[: ]",                # telephone
        r"Fax[: ]",                # fax
        r"E: ",                    # email
        r"W: ",                    # website
        r"Registered Office",
        r"Reg Office",
        r"\bLtd\b",                # company suffix
        r"Form ID",                # "Form ID : 5460"
        r"Page \d+ of \d+",        # "Page 7 of 13"
        r"digitalfieldsolutions",  # specific site
        r"http[s]?://",            # any URL
    ]

    def is_footer_line(line: str) -> bool:
        if line.strip() in FOOTER_LINES:
            return True
        return any(re.search(p, line, re.IGNORECASE) for p in FOOTER_PATTERNS)

    text_lines = full_text.splitlines()
    filtered_lines = [line for line in text_lines if not is_footer_line(line)]
    cleaned_text = "\n".join(filtered_lines)

    return cleaned_text.strip()



def extract_atmospheric_conditions(pdf_path: str) -> str:

    raw_text = extract_raw_text(pdf_path)
        # Remove known footer phrases
    FOOTER_LINES = [
        "Cornerstone Technical Report",
        "© Cornerstone Management Services Ltd 2009.",
        "21A Picton House, Hussar Court, Westside View, Waterlooville, Hampshire PO7 7SQ",
        "Reg Office: 24 Picton House Hussar Court Westside View Waterlooville Hants PO7 7SQ",
        "Tel: 0344 846 0955 E: enquiries@cornerstone-ltd.co.uk W: www.cornerstone-ltd.co.uk",
        "No part of this document is to be reproduced without the prior consent of Cornerstone Management Services Ltd.",
        "20A Picton House, Hussar Court, Westside View, Waterlooville, Hampshire, PO7 7SQ"
        "21A Picton House, Hussar Court, Westside View, Waterlooville, Hampshire PO7 7SQ"
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
        "20A Picton House, Hussar Court, Westside View, Waterlooville, Hampshire, PO7 7SQ",
        "Tel: 0344 846 0955 E: enquiries@cornerstone-ltd.co.uk W: www.cornerstone-ltd.co.uk",
        "No part of this document is to be reproduced without the prior consent of Cornerstone Management Services Ltd.",
        "21A Picton House, Hussar Court, Westside View, Waterlooville, Hampshire PO7 7SQ"
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
        if not capture and re.search(r"Location.*Relative Humidity.*Specific Humidity", stripped):
            capture = True
            continue  # skip the header line

        if capture:
            if not skipped_units and re.match(r"^[%°CcGKkg/\s.]+$", stripped):
                skipped_units = True  # Skip unit-only line
                continue

            if is_section_heading(stripped) or is_paragraph(stripped) or stripped == "":
                break  # Stop at next section or blank or paragraph

            # Remove units like %, g/Kg, °C from the line
            cleaned_line = re.sub(r"\s*%|\s*g/kg|\s*°C", "", line, flags=re.IGNORECASE)


            # 1) Normalize weird unicode minus/spacing
            cleaned_line = unicodedata.normalize("NFKC", cleaned_line)

            # turn " - 1.3" / "– 1.3" / "— 1.3" (start of line) into "-1.3"
            cleaned_line = re.sub(r'^[\-–—]\s+(?=\d)', '-', cleaned_line)

            # turn " …  -  1.3" in the middle of a line into " -1.3"
            cleaned_line = re.sub(r'(?<=\s)[\-–—]\s+(?=\d)', '-', cleaned_line)

            # 2) Convert European decimal commas to dots: "22,4" -> "22.4"
            cleaned_line = re.sub(r'(\d),(\d)', r'\1.\2', cleaned_line)

            # 3) Collapse multiple spaces
            cleaned_line = re.sub(r'\s{2,}', ' ', cleaned_line).strip()

            table_lines.append(cleaned_line)


    return "\n".join(table_lines).strip()


def extract_relevant(pdf_path: str) -> str | None:
    """
    Extracts all text from section 1.0 Property through 3.0 Conclusion (inclusive),
    and stops at the next section (e.g. 3.1, 4.0).
    """
    full_text = extract_full_text(pdf_path)
    lines = full_text.splitlines()

    def is_section_heading(line):
        return re.match(r"^\d+\.\d+(\s+\w+|:)", line.strip())

    capture = False
    relevant_lines = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("1.0 Property:"):
            capture = True

        if capture:
            if is_section_heading(stripped):
                # Extract the section number (e.g., "3.1" from "3.1 Recommendations:")
                section_match = re.match(r"^(\d+)\.(\d+)", stripped)
                if section_match:
                    major, minor = int(section_match.group(1)), int(section_match.group(2))
                    if major > 3 or (major == 3 and minor > 0):
                        break  # stop after 3.0

            relevant_lines.append(line)

    return "\n".join(relevant_lines).strip() if relevant_lines else None


def extract_conclusion_section(pdf_path: str) -> str:
    """
    Extracts the 'Conclusion' section from a PDF file.
    - Handles numbered (e.g. '3.0 Conclusion' or '3.0 Conclusion:') and plain 'Conclusion' headings.
    - Cuts off at the next section heading (numbered or known keyword, with or without a colon).
    - If no conclusion found, returns an empty string.
    """
    full_text = extract_full_text(pdf_path)

    # --- Case 1: Numbered heading like '3.0 Conclusion' or '3.0 Conclusion:'
    match = re.search(r'(?mi)^\d+\.\d+\s*conclusion:?\s*$', full_text)
    if match:
        end_index = match.end()
        conclusion_block = full_text[end_index:]

        # Next numbered heading (with or without colon)
        cutoff_match = re.search(r'(?mi)^\d+\.\d+\s+\w.*:?\s*$', conclusion_block)
        if cutoff_match:
            return conclusion_block[:cutoff_match.start()].strip()
        else:
            return conclusion_block.strip()

    # --- Case 2: Plain 'Conclusion' (with or without colon)
    match = re.search(r'(?mi)^conclusion:?\s*$', full_text)
    if match:
        end_index = match.end()
        conclusion_block = full_text[end_index:]

        # Next keyword heading (with or without colon)
        cutoff_match = re.search(
            r'(?mi)^(recommendations|observations|ventilation|incident|property|moisture\s+survey|survey\s+equipment):?\s*$',
            conclusion_block
        )
        if cutoff_match:
            return conclusion_block[:cutoff_match.start()].strip()
        else:
            return conclusion_block.strip()

    # --- No Conclusion found
    return full_text.strip()



def extract_body_without_conclusion(pdf_path: str) -> str:
    """
    Extracts the full text of the PDF excluding the 'Conclusion' section,
    and also chops off any trailing 'x.y Survey Equipment' section.
    Handles headings with or without a colon.
    """
    full_text = extract_full_text(pdf_path)

    # --- Case 1: Numbered heading like '3.0 Conclusion' or '3.0 Conclusion:'
    match = re.search(r'(?mi)^\d+\.\d+\s*conclusion:?\s*$', full_text)
    if match:
        start_index = match.start()
        end_index = match.end()
        conclusion_block = full_text[end_index:]

        # Next numbered heading (with or without colon)
        cutoff_match = re.search(r'(?mi)^\d+\.\d+\s+\w.*:?\s*$', conclusion_block)
        if cutoff_match:
            body = (full_text[:start_index] + conclusion_block[cutoff_match.start():]).strip()
        else:
            body = full_text[:start_index].strip()

    # --- Case 2: Plain 'Conclusion' (with or without colon)
    else:
        match = re.search(r'(?mi)^conclusion:?\s*$', full_text)
        if match:
            start_index = match.start()
            end_index = match.end()
            conclusion_block = full_text[end_index:]

            # Next keyword heading (with or without colon)
            cutoff_match = re.search(
                r'(?mi)^(recommendations|observations|ventilation|incident|property|moisture\s+survey):?\s*$',
                conclusion_block
            )
            if cutoff_match:
                body = (full_text[:start_index] + conclusion_block[cutoff_match.start():]).strip()
            else:
                body = full_text[:start_index].strip()
        else:
            body = full_text.strip()

    # --- Final cleanup: chop off trailing "Survey Equipment" (with or without colon)
    survey_match = re.search(r'(?mi)^\d+\.\d+\s*survey\s+equipment:?\s*$', body)
    if survey_match:
        body = body[:survey_match.start()].strip()

    return body


import re

def extract_body_without_conclusion_or_recommendations(pdf_path: str) -> str:
    """
    Extracts the full text of the PDF excluding:
      - the 'Conclusion' section,
      - the 'Recommendations' section,
      - and any trailing 'x.y Survey Equipment' section.
    Handles headings with or without a colon.
    """
    full_text = extract_full_text(pdf_path)
    body = full_text

    # --- Remove Conclusion section (numbered or plain)
    conclusion_match = re.search(r'(?mi)^\d+\.\d+\s*conclusion:?\s*$|^conclusion:?\s*$', body)
    if conclusion_match:
        start_index = conclusion_match.start()
        end_index = conclusion_match.end()
        after_conclusion = body[end_index:]

        # Find next numbered heading after Conclusion
        cutoff_match = re.search(r'(?mi)^\d+\.\d+\s+\w.*:?\s*$', after_conclusion)
        if cutoff_match:
            next_start = end_index + cutoff_match.start()
            body = body[:start_index] + body[next_start:]
        else:
            body = body[:start_index]

    # --- Remove Recommendations section if present
    recs_match = re.search(r'(?mi)^\d+\.\d+\s*recommendations:?\s*$', body)
    if recs_match:
        recs_start = recs_match.start()
        recs_end = recs_match.end()
        after_recs = body[recs_end:]

        # Find next numbered heading after Recommendations
        cutoff_match = re.search(r'(?mi)^\d+\.\d+\s+\w.*:?\s*$', after_recs)
        if cutoff_match:
            next_start = recs_end + cutoff_match.start()
            body = body[:recs_start] + body[next_start:]
        else:
            body = body[:recs_start]

    # --- Remove trailing Survey Equipment section
    survey_match = re.search(r'(?mi)^\d+\.\d+\s*survey\s+equipment:?\s*$', body)
    if survey_match:
        body = body[:survey_match.start()].strip()

    return body.strip()
