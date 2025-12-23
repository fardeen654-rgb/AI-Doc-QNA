def chunk_text(
    text: str,
    source: str,
    chunk_size: int = 500,
    overlap: int = 100
) -> list:
    """
    Split text into overlapping chunks with source metadata.
    Returns list of dicts: [{"text": "...", "source": "file.pdf"}]
    """
    if not text:
        return []

    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = start + chunk_size
        chunk_content = text[start:end].strip()

        if chunk_content:
            chunks.append({
                "text": chunk_content,
                "source": source
            })

        start = end - overlap
        if start < 0:
            start = 0

    return chunks