from sentence_transformers import SentenceTransformer

class EmbeddingService:
    """
    Handles converting text chunks into numerical vectors (embeddings).
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # This downloads the model on the first run (approx 80MB)
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: list):
        """
        Convert list of text chunks into embeddings.
        Returns a list of vectors (arrays of numbers).
        """
        if not texts:
            return []

        # encode() turns words into math!
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings