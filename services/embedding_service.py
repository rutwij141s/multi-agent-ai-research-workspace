"""
Embedding service for aRe_Agent application.
Handles text embedding generation using OpenAI API.
"""

from typing import List, Union
from openai import OpenAI
from openai import OpenAIError

from utils.config import config
from utils.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self):
        """Initialize embedding service."""
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_EMBEDDING_MODEL
        logger.info(f"Embedding service initialized with model: {self.model}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
            
        Raises:
            OpenAIError: If API call fails
        """
        try:
            if not text or not text.strip():
                logger.warning("Empty text provided for embedding")
                return []
            
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding of dimension {len(embedding)}")
            return embedding
            
        except OpenAIError as e:
            logger.error(f"OpenAI API error during embedding: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating embedding: {e}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            OpenAIError: If API call fails
        """
        try:
            if not texts:
                logger.warning("Empty text list provided for embeddings")
                return []
            
            # Filter out empty texts
            valid_texts = [t for t in texts if t and t.strip()]
            
            if not valid_texts:
                logger.warning("No valid texts after filtering")
                return []
            
            response = self.client.embeddings.create(
                model=self.model,
                input=valid_texts
            )
            
            embeddings = [item.embedding for item in response.data]
            logger.debug(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except OpenAIError as e:
            logger.error(f"OpenAI API error during batch embedding: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating embeddings: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings for this model.
        
        Returns:
            Embedding dimension
        """
        # text-embedding-3-small has 1536 dimensions
        # text-embedding-3-large has 3072 dimensions
        # text-embedding-ada-002 has 1536 dimensions
        
        dimension_map = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }
        
        return dimension_map.get(self.model, 1536)


# Singleton instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
