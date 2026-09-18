"""
Repository pattern for aRe_Agent database operations.
Provides high-level database operations abstraction.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime

from database.collections import get_collection_manager
from utils.logging import get_logger
from utils.helpers import generate_id, hash_text

logger = get_logger(__name__)


class DocumentRepository:
    """Repository for document storage and retrieval."""
    
    def __init__(self):
        """Initialize document repository."""
        self.collection_manager = get_collection_manager()
        logger.info("Document repository initialized")
    
    def store_pdf_chunks(
        self,
        user_id: str,
        document_id: str,
        filename: str,
        chunks: List[Dict[str, Any]]
    ) -> bool:
        """
        Store PDF document chunks.
        
        Args:
            user_id: User identifier
            document_id: Unique document identifier
            filename: PDF filename
            chunks: List of chunk dictionaries from PDFService
            
        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self.collection_manager.get_pdf_collection(user_id)
            
            documents = []
            metadatas = []
            ids = []
            
            for chunk in chunks:
                documents.append(chunk['text'])
                
                metadata = {
                    'document_id': document_id,
                    'filename': filename,
                    'chunk_index': chunk.get('chunk_index', 0),
                    'user_id': user_id,
                    'uploaded_at': datetime.now().isoformat()
                }
                
                # Add page number if available
                if 'page' in chunk:
                    metadata['page'] = chunk['page']
                
                metadatas.append(metadata)
                ids.append(chunk.get('chunk_id', generate_id()))
            
            success = self.collection_manager.add_documents(
                collection=collection,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            if success:
                logger.info(f"Stored {len(chunks)} chunks for document {document_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error storing PDF chunks: {e}")
            return False
    
    def search_pdf_documents(
        self,
        user_id: str,
        query: str,
        n_results: int = 5,
        document_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search user's PDF documents.
        
        Args:
            user_id: User identifier
            query: Search query
            n_results: Number of results to return
            document_id: Optional filter by specific document
            
        Returns:
            List of matching chunks with metadata
        """
        try:
            collection = self.collection_manager.get_pdf_collection(user_id)
            
            where_filter = {'user_id': user_id}
            if document_id:
                where_filter['document_id'] = document_id
            
            results = self.collection_manager.query_collection(
                collection=collection,
                query_text=query,
                n_results=n_results,
                where=where_filter
            )
            
            # Format results
            formatted_results = []
            if results['ids']:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i]
                    })
            
            logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching PDF documents: {e}")
            return []
    
    def delete_pdf_document(
        self,
        user_id: str,
        document_id: str
    ) -> bool:
        """
        Delete all chunks of a PDF document.
        
        Args:
            user_id: User identifier
            document_id: Document identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self.collection_manager.get_pdf_collection(user_id)
            
            success = self.collection_manager.delete_documents(
                collection=collection,
                where={
                    'user_id': user_id,
                    'document_id': document_id
                }
            )
            
            if success:
                logger.info(f"Deleted document {document_id} for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting PDF document: {e}")
            return False
    
    def list_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List all documents for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of document info dictionaries
        """
        try:
            collection = self.collection_manager.get_pdf_collection(user_id)
            
            results = self.collection_manager.get_documents(
                collection=collection,
                where={'user_id': user_id}
            )
            
            # Group by document_id
            documents_map = {}
            
            for i in range(len(results['ids'])):
                metadata = results['metadatas'][i]
                doc_id = metadata.get('document_id')
                
                if doc_id not in documents_map:
                    documents_map[doc_id] = {
                        'document_id': doc_id,
                        'filename': metadata.get('filename'),
                        'uploaded_at': metadata.get('uploaded_at'),
                        'chunk_count': 0
                    }
                
                documents_map[doc_id]['chunk_count'] += 1
            
            documents_list = list(documents_map.values())
            logger.info(f"Found {len(documents_list)} documents for user {user_id}")
            return documents_list
            
        except Exception as e:
            logger.error(f"Error listing user documents: {e}")
            return []
    
    def get_document_count(self, user_id: str) -> int:
        """
        Get total number of document chunks for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of chunks
        """
        try:
            collection = self.collection_manager.get_pdf_collection(user_id)
            return self.collection_manager.count_documents(collection)
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0


class ConversationRepository:
    """Repository for conversation history storage and retrieval."""
    
    def __init__(self):
        """Initialize conversation repository."""
        self.collection_manager = get_collection_manager()
        logger.info("Conversation repository initialized")
    
    def store_conversation_turn(
        self,
        user_id: str,
        conversation_id: str,
        role: str,
        content: str,
        agent_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store a conversation turn.
        
        Args:
            user_id: User identifier
            conversation_id: Conversation identifier
            role: Message role (user/assistant)
            content: Message content
            agent_type: Optional agent type
            metadata: Optional additional metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self.collection_manager.get_conversation_collection(user_id)
            
            turn_metadata = {
                'user_id': user_id,
                'conversation_id': conversation_id,
                'role': role,
                'timestamp': datetime.now().isoformat()
            }
            
            if agent_type:
                turn_metadata['agent_type'] = agent_type
            
            if metadata:
                turn_metadata.update(metadata)
            
            turn_id = generate_id()
            
            success = self.collection_manager.add_documents(
                collection=collection,
                documents=[content],
                metadatas=[turn_metadata],
                ids=[turn_id]
            )
            
            if success:
                logger.debug(f"Stored conversation turn for {conversation_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error storing conversation turn: {e}")
            return False
    
    def get_conversation_history(
        self,
        user_id: str,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history.
        
        Args:
            user_id: User identifier
            conversation_id: Conversation identifier
            limit: Optional limit on number of turns
            
        Returns:
            List of conversation turns
        """
        try:
            collection = self.collection_manager.get_conversation_collection(user_id)
            
            results = self.collection_manager.get_documents(
                collection=collection,
                where={
                    'user_id': user_id,
                    'conversation_id': conversation_id
                },
                limit=limit
            )
            
            # Format and sort by timestamp
            turns = []
            for i in range(len(results['ids'])):
                turns.append({
                    'id': results['ids'][i],
                    'content': results['documents'][i],
                    'metadata': results['metadatas'][i]
                })
            
            # Sort by timestamp
            turns.sort(key=lambda x: x['metadata'].get('timestamp', ''))
            
            logger.debug(f"Retrieved {len(turns)} turns for conversation {conversation_id}")
            return turns
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def delete_conversation(
        self,
        user_id: str,
        conversation_id: str
    ) -> bool:
        """
        Delete a conversation.
        
        Args:
            user_id: User identifier
            conversation_id: Conversation identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self.collection_manager.get_conversation_collection(user_id)
            
            success = self.collection_manager.delete_documents(
                collection=collection,
                where={
                    'user_id': user_id,
                    'conversation_id': conversation_id
                }
            )
            
            if success:
                logger.info(f"Deleted conversation {conversation_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            return False


# Singleton instances
_document_repository = None
_conversation_repository = None


def get_document_repository() -> DocumentRepository:
    """Get or create document repository instance."""
    global _document_repository
    if _document_repository is None:
        _document_repository = DocumentRepository()
    return _document_repository


def get_conversation_repository() -> ConversationRepository:
    """Get or create conversation repository instance."""
    global _conversation_repository
    if _conversation_repository is None:
        _conversation_repository = ConversationRepository()
    return _conversation_repository
