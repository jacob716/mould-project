import os
import csv
import re
from pathlib import Path

# folder with your new batch
reports_path = Path("reports/newreports")

# get all files
files = sorted([f for f in reports_path.glob("*.pdf")])

mapping = []
start_id = 301  # since 0300 was the last used ID

for idx, file in enumerate(files, start=start_id):
    # make ID padded to 4 digits
    file_id = f"{idx:04d}"

    # extract postcode (last part of filename, strip '(2)' etc.)
    raw_postcode = file.stem.split("_")[-1]
    postcode = re.sub(r" \(\d+\)$", "", raw_postcode)

    # new filename
    new_name = f"{file_id}_{postcode}.pdf"
    new_path = reports_path / new_name

    # rename
    file.rename(new_path)

    # keep mapping
    mapping.append([file_id, new_name, file.name])

# append mapping to the existing CSV
with open("mapping.csv", "a", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(mapping)
