import os
import faiss
import pickle
import numpy as np

class VectorStore:
    def __init__(self, index_path: str):
        self.index_path = index_path
        self.index_file = os.path.join(index_path, "index.faiss")
        self.meta_file = os.path.join(index_path, "chunks.pkl")
        self.index = None
        self.chunks = []

    def create_or_update_index(self, embeddings: list, chunks: list):
        vectors = np.array(embeddings).astype("float32")
        dim = vectors.shape[1]

        if self.index is None:
            self.index = faiss.IndexFlatL2(dim)

        self.index.add(vectors)
        self.chunks.extend(chunks)
        self._save()

    def search(self, query_embedding: list, top_k: int = 5):
        if self.index is None: return []
        query_vector = np.array([query_embedding]).astype("float32")
        distances, indices = self.index.search(query_vector, top_k)

        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.chunks):
                results.append(self.chunks[idx])
        return results

    def _save(self):
        os.makedirs(self.index_path, exist_ok=True)
        faiss.write_index(self.index, self.index_file)
        with open(self.meta_file, "wb") as f:
            pickle.dump(self.chunks, f)

    def load(self):
        if os.path.exists(self.index_file) and os.path.exists(self.meta_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.meta_file, "rb") as f:
                self.chunks = pickle.load(f)
            return True
        return False