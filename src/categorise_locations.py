"""
categorise_locations.py
-----------------------

Utility function for detecting and categorising room/location mentions
in damp and mould survey report data.

Usage:
    from src.categorise_locations import categorise_location_multiple

    df["main_issue_location_categorised"] = (
        df["main_issue_location"]
        .apply(categorise_location_multiple)
        .apply(lambda x: ", ".join(x))  # join list into string, optional
    )
"""

import re

# === Room keyword patterns (case-insensitive) ===
LOCATION_KEYWORDS = {
    "Bathroom": [r"bathroom"],
    "Bedroom": [r"bedroom"],
    "Kitchen": [r"kitchen"],
    "Living/Lounge": [r"living", r"lounge"],
    "Hallway": [r"hallway", r"corridor"],
}


def categorise_location_multiple(text):
    """
    Categorise a text string into one or more location categories.

    Parameters
    ----------
    text : str
        Free-text description of the location(s) of damp/mould issues.

    Returns
    -------
    list of str
        A list of matching categories.
        If no match: ["Other"]
        If text empty or 'not mentioned': ["Not mentioned"]
    """

    # Handle missing or blank inputs
    if not isinstance(text, str) or text.strip() == "" or text.strip().lower() == "not mentioned":
        return ["Not mentioned"]

    text_lower = text.lower()
    matches = []

    for category, patterns in LOCATION_KEYWORDS.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                matches.append(category)
                break  # stop checking more patterns for this category

    if not matches:
        return ["Other"]

    # Remove duplicates and sort alphabetically for consistency
    return sorted(set(matches))
