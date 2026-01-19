"""Embedding service for generating vector embeddings."""
import logging
from typing import List
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings using sentence-transformers."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize the embedding service.
        
        Args:
            model_name: The name of the sentence-transformers model to use
        """
        self.model_name = model_name
        self._model = None
    
    def _load_model(self):
        """Lazy load the embedding model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded successfully")
        return self._model
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding vector for a single text.
        
        Args:
            text: The text to embed
            
        Returns:
            A list of floats representing the embedding vector
        """
        model = self._load_model()
        
        # Generate embedding
        embedding = model.encode(text, convert_to_numpy=True)
        
        # Convert to list of floats
        return embedding.tolist()
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            A list of embedding vectors
        """
        model = self._load_model()
        
        # Generate embeddings in batch for efficiency
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=len(texts) > 10)
        
        # Convert to list of lists
        return embeddings.tolist()
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors.
        
        Returns:
            The dimension of the embedding vectors
        """
        # For all-MiniLM-L6-v2, the dimension is 384
        # This could be determined dynamically if needed
        return 384
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score between -1 and 1
        """
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Compute cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


# Global singleton instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get the global embedding service instance.
    
    Returns:
        The singleton EmbeddingService instance
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
