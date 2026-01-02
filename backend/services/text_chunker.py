def chunk_text(text, source, chunk_size=500, overlap=100):
    """Chunks text with overlap to preserve context across boundaries."""
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        # Only keep chunks that carry meaningful information
        if len(chunk) > 100:
            chunks.append({
                "text": chunk,
                "source": source
            })

        # Slide the window forward by less than chunk_size to create overlap
        start += chunk_size - overlap

    return chunks