from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

class EmbeddingManager:
    """Manage text embeddings for RAG system."""
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
    
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for text(s)."""
        if isinstance(texts, str):
            texts = [texts]
        return self.model.encode(texts)
    
    def cosine_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings."""
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))