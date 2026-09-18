"""
ChromaDB client for aRe_Agent application.
Manages ChromaDB connection and initialization.
"""

from pathlib import Path
from typing import Optional
import chromadb
from chromadb.config import Settings

from utils.config import config
from utils.logging import get_logger

logger = get_logger(__name__)


class ChromaDBClient:
    """Manages ChromaDB client connection."""
    
    def __init__(self):
        """Initialize ChromaDB client."""
        self.db_path = Path(config.CHROMA_DB_PATH)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB persistent client."""
        try:
            logger.info(f"Initializing ChromaDB at {self.db_path}")
            
            self.client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            logger.info("ChromaDB client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise
    
    def get_client(self) -> chromadb.PersistentClient:
        """
        Get ChromaDB client instance.
        
        Returns:
            ChromaDB client
        """
        if self.client is None:
            self._initialize_client()
        return self.client
    
    def list_collections(self) -> list[str]:
        """
        List all collections in the database.
        
        Returns:
            List of collection names
        """
        try:
            collections = self.client.list_collections()
            collection_names = [col.name for col in collections]
            logger.debug(f"Found {len(collection_names)} collections")
            return collection_names
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection.
        
        Args:
            collection_name: Name of collection to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection {collection_name}: {e}")
            return False
    
    def reset_database(self) -> bool:
        """
        Reset entire database (delete all collections).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.reset()
            logger.warning("Database reset - all collections deleted")
            return True
        except Exception as e:
            logger.error(f"Error resetting database: {e}")
            return False
    
    def get_collection_count(self, collection_name: str) -> int:
        """
        Get number of items in a collection.
        
        Args:
            collection_name: Name of collection
            
        Returns:
            Number of items in collection
        """
        try:
            collection = self.client.get_collection(name=collection_name)
            return collection.count()
        except Exception as e:
            logger.error(f"Error getting collection count for {collection_name}: {e}")
            return 0
    
    def health_check(self) -> tuple[bool, Optional[str]]:
        """
        Check if ChromaDB is healthy and accessible.
        
        Returns:
            Tuple of (is_healthy, error_message)
        """
        try:
            # Try to list collections
            _ = self.client.list_collections()
            return True, None
        except Exception as e:
            error_msg = f"ChromaDB health check failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg


# Singleton instance
_chroma_client = None


def get_chroma_client() -> ChromaDBClient:
    """Get or create ChromaDB client instance."""
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = ChromaDBClient()
    return _chroma_client
