def chunk_report_by_paragraph(full_text: str, min_length: int = 200) -> list:
    """
    Splits a long report into paragraph-level chunks.
    Chunks with fewer than `min_length` characters are merged with the next.
    """
    import re

    # Split by double newlines or long line breaks (basic paragraphing)
    raw_chunks = re.split(r'\n\s*\n+', full_text)

    # Clean and merge small chunks
    chunks = []
    buffer = ""

    for paragraph in raw_chunks:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if len(paragraph) < min_length:
            buffer += " " + paragraph
        else:
            if buffer:
                chunks.append(buffer.strip())
                buffer = ""
            chunks.append(paragraph)

    if buffer:
        chunks.append(buffer.strip())

    return chunks

import re
from typing import List

def chunk_pdf_text(text: str, target_len: int = 800, max_len: int = 1100) -> List[str]:
    """
    Heuristic chunker for PDF-extracted text.
    - Unwraps hard line breaks that are not paragraph boundaries.
    - Splits on blank lines, numbered headings (e.g., 1.0, 4.2), and bullets.
    - Packs segments into chunks ~target_len (never exceeding max_len).
    """
    # Normalize newlines
    t = text.replace("\r\n", "\n").replace("\r", "\n")

    # 1) Unwrap hard line breaks inside paragraphs:
    # turn single newlines into spaces UNLESS the newline is followed by:
    #   - another newline (blank line)
    #   - a numbered heading like "4.2", "5.0", etc.
    #   - a bullet/indent ("•", "-", digit + ")" )
    unwrap_pattern = re.compile(
        r"\n(?!\n|(?=\s*\d+(\.\d+){1,4}\s)|(?=\s*[•\-]\s)|(?=\s*\d+\))|(?=\s*[A-Z][a-z]+:))"
    )
    t = unwrap_pattern.sub(" ", t)

    # 2) Split on paragraph cues: blank lines, numbered headings, bullets
    split_pattern = re.compile(
        r"(?:\n\s*\n+)|"                   # blank lines
        r"(?=^\s*\d+(\.\d+){1,4}\s)"       # numbered headings at line start (e.g., 4.2 , 5.0)
        r"|(?=^\s*[•\-]\s)"                # bullets
        , re.MULTILINE
    )
    segments = [s.strip() for s in split_pattern.split(t) if s and not s.isspace()]

    # 3) Pack segments into size-bounded chunks
    chunks: List[str] = []
    buf = []
    cur = 0
    for seg in segments:
        seg_len = len(seg)
        if cur == 0:
            buf.append(seg)
            cur += seg_len
            continue
        if cur + 1 + seg_len <= target_len:
            buf.append(seg)
            cur += 1 + seg_len
        elif cur + 1 + seg_len <= max_len:
            # allow a bit of overflow up to max_len
            buf.append(seg)
            chunks.append("\n\n".join(buf))
            buf = []
            cur = 0
        else:
            # flush and start new
            chunks.append("\n\n".join(buf))
            buf = [seg]
            cur = seg_len
    if buf:
        chunks.append("\n\n".join(buf))

    return chunks


def find_ventilation_chunks(chunks: list) -> list:
    keywords = ['ventilation', 'vent', 'extractor', 'fan', 'airflow', 'humidity']
    return [chunk for chunk in chunks if any(k in chunk.lower() for k in keywords)]
