from sentence_transformers import SentenceTransformer
import os

class EmbeddingService:
    def __init__(self):
        self._model = None  # Don't load yet!

    def get_model(self):
        if self._model is None:
            # Use 'all-MiniLM-L6-v2' (only ~80MB) instead of heavier models
            self._model = SentenceTransformer('all-MiniLM-L6-v2')
        return self._model

    def embed(self, text):
        model = self.get_model()
        return model.encode(text)