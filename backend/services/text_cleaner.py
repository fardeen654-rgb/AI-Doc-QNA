import re

def clean_text(text: str) -> str:
    """
    Clean and normalize extracted PDF text for AI processing.
    """
    if not text:
        return ""

    # 1. Remove excessive newlines (fixes broken paragraphs)
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # 2. Remove multiple spaces and tabs (normalizes spacing)
    text = re.sub(r"[ \t]+", " ", text)

    # 3. Remove non-ASCII/junk symbols (removes weird icons or artifacts)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)

    # 4. Remove standalone page numbers (heuristic: newline + number + newline)
    text = re.sub(r"\n\d+\n", "\n", text)

    return text.strip()