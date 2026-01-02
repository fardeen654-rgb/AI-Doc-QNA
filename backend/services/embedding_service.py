import torch
import os
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    def __init__(self):
        """
        Initialize the service without loading the heavy model into memory immediately.
        This keeps the app's startup RAM usage very low.
        """
        self.model = None
        # 'all-MiniLM-L6-v2' is roughly 80% smaller and 4x faster than base models.
        self.model_name = 'all-MiniLM-L6-v2'

    def _load_model(self):
        """
        Internal helper to perform 'Lazy Loading'. 
        The model is only hydrated into RAM the first time it's needed.
        """
        if self.model is None:
            print(f"--- Production Optimization: Loading {self.model_name} ---")
            
            # Optimization 1: Use FP16 precision to cut RAM usage by ~50%.
            # Optimization 2: Explicitly use CPU for Render's Free Tier.
            try:
                self.model = SentenceTransformer(
                    self.model_name, 
                    device='cpu',
                    model_kwargs={"torch_dtype": torch.float16}
                )
                # Optimization 3: Set to eval mode to disable training overhead.
                self.model.eval()
            except Exception as e:
                print(f"Error loading model: {e}")
                # Fallback to standard loading if FP16 is unsupported
                self.model = SentenceTransformer(self.model_name, device='cpu')
                
        return self.model

    def embed_texts(self, texts):
        """
        Converts a list of strings into vector embeddings.
        :param texts: List of strings (document chunks or user query).
        """
        # Trigger lazy load
        model = self._load_model()
        
        # Optimization 4: Disable gradient tracking to save memory during inference.
        with torch.no_grad():
            embeddings = model.encode(
                texts, 
                convert_to_numpy=True, 
                show_progress_bar=False
            )
            
        return embeddings