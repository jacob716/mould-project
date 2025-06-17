from PyPDF2 import PdfReader

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
