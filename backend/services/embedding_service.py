import torch
import os
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    def __init__(self):
        """
        Initialize the service without loading the model into memory immediately.
        This keeps the app's startup RAM usage very low.
        """
        self.model = None
        # 'all-MiniLM-L6-v2' is roughly 80% smaller and 4x faster than base models.
        self.model_name = 'all-MiniLM-L6-v2'

    def _load_model(self):
        """
        Internal helper to perform 'Lazy Loading'. 
        The model is only hydrated into RAM the first time a user asks a question.
        """
        if self.model is None:
            print(f"--- Production Optimization: Loading {self.model_name} ---")
            
            # Optimization 1: Use FP16 (Half-Precision) to cut RAM usage by ~50%.
            # Optimization 2: Explicitly use CPU for Render's Free Tier.
            try:
                self.model = SentenceTransformer(
                    self.model_name, 
                    device='cpu',
                    model_kwargs={"torch_dtype": torch.float16}
                )
                # Optimization 3: Set to eval mode to disable dropout/training overhead.
                self.model.eval()
            except Exception as e:
                print(f"Error loading model: {e}")
                # Fallback to standard loading if FP16 is unsupported by the environment
                self.model = SentenceTransformer(self.model_name, device='cpu')
                
        return self.model

    def embed_texts(self, texts):
        """
        Converts a list of strings into a list of vector embeddings.
        :param texts: List of strings (document chunks or user query).
        :return: Numpy array of embeddings.
        """
        # Trigger lazy load
        model = self._load_model()
        
        # Optimization 4: Disable gradient tracking to save memory during inference.
        with torch.no_grad():
            # convert_to_numpy=True is required for FAISS compatibility.
            embeddings = model.encode(
                texts, 
                convert_to_numpy=True, 
                show_progress_bar=False
            )
            
        return embeddings