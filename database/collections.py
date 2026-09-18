"""
ChromaDB collections manager for aRe_Agent application.
Manages different collections for various use cases.
"""

from typing import List, Dict, Optional, Any
import chromadb
from chromadb.api.models.Collection import Collection

from database.chroma_client import get_chroma_client
from services.embedding_service import get_embedding_service
from utils.config import config
from utils.logging import get_logger
from utils.helpers import generate_id

logger = get_logger(__name__)


class CollectionManager:
    """Manages ChromaDB collections for different purposes."""
    
    def __init__(self):
        """Initialize collection manager."""
        self.chroma_client = get_chroma_client()
        self.embedding_service = get_embedding_service()
        self.prefix = config.CHROMA_COLLECTION_PREFIX
        logger.info("Collection manager initialized")
    
    def get_or_create_collection(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Collection:
        """
        Get existing collection or create new one.
        
        Args:
            name: Collection name (will be prefixed)
            metadata: Optional collection metadata
            
        Returns:
            ChromaDB collection
        """
        try:
            collection_name = f"{self.prefix}_{name}"
            
            collection = self.chroma_client.get_client().get_or_create_collection(
                name=collection_name,
                metadata=metadata or {}
            )
            
            logger.debug(f"Got or created collection: {collection_name}")
            return collection
            
        except Exception as e:
            logger.error(f"Error getting/creating collection {name}: {e}")
            raise
    
    def get_pdf_collection(self, user_id: str) -> Collection:
        """
        Get collection for user's PDF documents.
        
        Args:
            user_id: User identifier
            
        Returns:
            ChromaDB collection for PDFs
        """
        return self.get_or_create_collection(
            name=f"pdf_{user_id}",
            metadata={"type": "pdf", "user_id": user_id}
        )
    
    def get_conversation_collection(self, user_id: str) -> Collection:
        """
        Get collection for user's conversation history.
        
        Args:
            user_id: User identifier
            
        Returns:
            ChromaDB collection for conversations
        """
        return self.get_or_create_collection(
            name=f"conversation_{user_id}",
            metadata={"type": "conversation", "user_id": user_id}
        )
    
    def add_documents(
        self,
        collection: Collection,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> bool:
        """
        Add documents to collection with embeddings.
        
        Args:
            collection: ChromaDB collection
            documents: List of text documents
            metadatas: Optional list of metadata dicts
            ids: Optional list of document IDs
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not documents:
                logger.warning("No documents to add")
                return False
            
            # Generate IDs if not provided
            if ids is None:
                ids = [generate_id() for _ in documents]
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(documents)} documents")
            embeddings = self.embedding_service.generate_embeddings(documents)
            
            if not embeddings:
                logger.error("Failed to generate embeddings")
                return False
            
            # Add to collection
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to collection {collection.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to collection: {e}")
            return False
    
    def query_collection(
        self,
        collection: Collection,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query collection for similar documents.
        
        Args:
            collection: ChromaDB collection
            query_text: Query text
            n_results: Number of results to return
            where: Optional metadata filter
            where_document: Optional document content filter
            
        Returns:
            Query results dictionary
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.generate_embedding(query_text)
            
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return {"ids": [], "documents": [], "metadatas": [], "distances": []}
            
            # Query collection
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                where_document=where_document
            )
            
            logger.debug(f"Query returned {len(results['ids'][0]) if results['ids'] else 0} results")
            return results
            
        except Exception as e:
            logger.error(f"Error querying collection: {e}")
            return {"ids": [], "documents": [], "metadatas": [], "distances": []}
    
    def delete_documents(
        self,
        collection: Collection,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Delete documents from collection.
        
        Args:
            collection: ChromaDB collection
            ids: Optional list of document IDs to delete
            where: Optional metadata filter for deletion
            
        Returns:
            True if successful, False otherwise
        """
        try:
            collection.delete(ids=ids, where=where)
            logger.info(f"Deleted documents from collection {collection.name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            return False
    
    def update_documents(
        self,
        collection: Collection,
        ids: List[str],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Update documents in collection.
        
        Args:
            collection: ChromaDB collection
            ids: List of document IDs to update
            documents: Optional new document texts
            metadatas: Optional new metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            update_params = {"ids": ids}
            
            if documents:
                # Generate new embeddings if documents are updated
                embeddings = self.embedding_service.generate_embeddings(documents)
                update_params["documents"] = documents
                update_params["embeddings"] = embeddings
            
            if metadatas:
                update_params["metadatas"] = metadatas
            
            collection.update(**update_params)
            logger.info(f"Updated {len(ids)} documents in collection {collection.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating documents: {e}")
            return False
    
    def get_documents(
        self,
        collection: Collection,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get documents from collection.
        
        Args:
            collection: ChromaDB collection
            ids: Optional list of document IDs
            where: Optional metadata filter
            limit: Optional limit on number of results
            
        Returns:
            Documents dictionary
        """
        try:
            results = collection.get(
                ids=ids,
                where=where,
                limit=limit
            )
            logger.debug(f"Retrieved {len(results['ids'])} documents from {collection.name}")
            return results
        except Exception as e:
            logger.error(f"Error getting documents: {e}")
            return {"ids": [], "documents": [], "metadatas": []}
    
    def count_documents(self, collection: Collection) -> int:
        """
        Count documents in collection.
        
        Args:
            collection: ChromaDB collection
            
        Returns:
            Number of documents
        """
        try:
            return collection.count()
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            return 0
    
    def delete_user_collections(self, user_id: str) -> bool:
        """
        Delete all collections for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            collections_to_delete = [
                f"{self.prefix}_pdf_{user_id}",
                f"{self.prefix}_conversation_{user_id}"
            ]
            
            for collection_name in collections_to_delete:
                try:
                    self.chroma_client.delete_collection(collection_name)
                except Exception as e:
                    logger.warning(f"Could not delete collection {collection_name}: {e}")
            
            logger.info(f"Deleted collections for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user collections: {e}")
            return False


# Singleton instance
_collection_manager = None


def get_collection_manager() -> CollectionManager:
    """Get or create collection manager instance."""
    global _collection_manager
    if _collection_manager is None:
        _collection_manager = CollectionManager()
    return _collection_manager
