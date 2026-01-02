def keyword_score(query, text):
    """Calculates a simple lexical match score."""
    query_words = set(query.lower().split())
    text_words = set(text.lower().split())
    return len(query_words & text_words)

def hybrid_rerank(query, chunks):
    """Reranks retrieved chunks by boosting those with exact keyword matches."""
    scored = []

    for c in chunks:
        # Boost semantic results that also contain query keywords
        score = keyword_score(query, c["text"])
        scored.append((score, c))

    # Sort based on highest keyword overlap
    scored.sort(reverse=True, key=lambda x: x[0])
    return [c for _, c in scored]