import os
import faiss
import numpy as np
import pickle

class VectorStore:
    def __init__(self, index_path):
        self.index_path = index_path
        self.index_file = os.path.join(index_path, "index.faiss")
        self.metadata_file = os.path.join(index_path, "metadata.pkl")
        self.index = None
        self.metadata = []

    def create_or_update_index(self, embeddings, new_metadata):
        """Creates a new FAISS index or adds vectors to an existing one."""
        embeddings = np.array(embeddings).astype("float32")
        
        if self.index is None:
            dimension = embeddings.shape[1]
            # Using IndexFlatL2 for high accuracy in smaller/medium datasets
            self.index = faiss.IndexFlatL2(dimension)
            
        self.index.add(embeddings)
        self.metadata.extend(new_metadata)
        self.save()

    def search(self, query_embedding, top_k=8):
        """
        Retrieves top_k relevant chunks. 
        Day 25: Increased top_k to 8 to improve recall for hybrid reranking.
        """
        if self.index is None or self.index.ntotal == 0:
            return []

        # FAISS search requires a 2D array
        distances, indices = self.index.search(
            np.array([query_embedding]).astype("float32"), 
            top_k
        )

        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.metadata):
                results.append(self.metadata[idx])
        
        return results

    def save(self):
        """Persists the FAISS index and metadata to disk."""
        if not os.path.exists(self.index_path):
            os.makedirs(self.index_path)
            
        faiss.write_index(self.index, self.index_file)
        with open(self.metadata_file, "wb") as f:
            pickle.dump(self.metadata, f)

    def load(self):
        """Loads the index and metadata from disk if they exist."""
        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.metadata_file, "rb") as f:
                self.metadata = pickle.load(f)
        else:
            self.index = None
            self.metadata = []