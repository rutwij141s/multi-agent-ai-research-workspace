"""
PDF Research Agent for aRe_Agent application.
Handles PDF document upload, analysis, and question answering with RAG.
"""

from typing import Iterator, Optional, Dict, Any, List
from pathlib import Path

from agents.base_agent import BaseAgent
from services.pdf_service import get_pdf_service
from services.citation_service import get_citation_service
from database.repository import get_document_repository
from utils.logging import get_logger
from utils.helpers import generate_id

logger = get_logger(__name__)


class PDFResearchAgent(BaseAgent):
    """Agent for PDF document research and question answering."""
    
    def __init__(self):
        """Initialize PDF Research Agent."""
        super().__init__(
            agent_type="pdf_research",
            name="PDF Research Agent",
            description="Upload and interact with PDF documents using AI-powered search and question answering"
        )
        self.pdf_service = get_pdf_service()
        self.citation_service = get_citation_service()
        self.document_repository = get_document_repository()
    
    def get_system_prompt(self) -> str:
        """Get system prompt for PDF Research Agent."""
        return """You are a PDF Research Agent specializing in document analysis and question answering.

Your responsibilities:
- Answer questions based primarily on the content of uploaded PDF documents
- Provide accurate citations with page numbers when referencing document content
- Clearly distinguish between information from documents and general knowledge
- Summarize document content when requested
- Compare information across multiple documents when applicable
- Extract key findings and important information
- Identify contradictions or differences between documents

Guidelines:
- Always cite the specific document and page number when referencing content
- If information is not found in the documents, clearly state that
- Be precise and factual in your responses
- When multiple documents contain relevant information, synthesize and compare
- Format citations clearly: [Document Name, Page X]
- If asked about content not in the documents, clarify that your answer is based on general knowledge

Remember: Your primary role is to help users understand and extract insights from their uploaded documents."""
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities."""
        return [
            "Upload and process PDF documents",
            "Answer questions based on document content",
            "Provide citations with page numbers",
            "Summarize entire documents",
            "Extract key findings",
            "Compare multiple PDFs",
            "Identify contradictions between documents",
            "Search across all uploaded documents"
        ]
    
    def process_pdf_upload(
        self,
        pdf_file,
        filename: str,
        user_id: str
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Process and store a PDF upload.
        
        Args:
            pdf_file: Binary PDF file object
            filename: Original filename
            user_id: User identifier
            
        Returns:
            Tuple of (success, error_message, document_id)
        """
        try:
            logger.info(f"Processing PDF upload: {filename} for user {user_id}")
            
            # Validate PDF
            is_valid, error = self.pdf_service.validate_pdf(pdf_file)
            if not is_valid:
                return False, error, None
            
            # Reset file pointer
            pdf_file.seek(0)
            
            # Extract text
            pdf_data = self.pdf_service.extract_text_from_pdf(pdf_file, filename)
            
            if not pdf_data.get('success'):
                error_msg = pdf_data.get('error', 'Failed to extract text from PDF')
                return False, error_msg, None
            
            # Generate document ID
            document_id = generate_id()
            
            # Chunk text
            chunks = self.pdf_service.chunk_pdf_text(pdf_data, include_page_numbers=True)
            
            if not chunks:
                return False, "No text content found in PDF", None
            
            # Store in database
            success = self.document_repository.store_pdf_chunks(
                user_id=user_id,
                document_id=document_id,
                filename=filename,
                chunks=chunks
            )
            
            if success:
                logger.info(f"Successfully stored PDF: {filename} ({len(chunks)} chunks)")
                return True, None, document_id
            else:
                return False, "Failed to store PDF in database", None
                
        except Exception as e:
            logger.error(f"Error processing PDF upload: {e}")
            return False, f"Error processing PDF: {str(e)}", None
    
    def search_documents(
        self,
        user_id: str,
        query: str,
        n_results: int = 5,
        document_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search user's documents for relevant content.
        
        Args:
            user_id: User identifier
            query: Search query
            n_results: Number of results
            document_id: Optional specific document to search
            
        Returns:
            List of relevant document chunks with metadata
        """
        try:
            results = self.document_repository.search_pdf_documents(
                user_id=user_id,
                query=query,
                n_results=n_results,
                document_id=document_id
            )
            
            logger.info(f"Document search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def format_context_from_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results into context for the LLM.
        
        Args:
            results: Search results from document search
            
        Returns:
            Formatted context string
        """
        if not results:
            return "No relevant content found in uploaded documents."
        
        context_parts = ["Here is relevant content from the uploaded documents:\n"]
        
        for i, result in enumerate(results, 1):
            text = result.get('text', '')
            metadata = result.get('metadata', {})
            filename = metadata.get('filename', 'Unknown Document')
            page = metadata.get('page', 'Unknown')
            
            context_parts.append(f"\n--- Source {i} ---")
            context_parts.append(f"Document: {filename}")
            context_parts.append(f"Page: {page}")
            context_parts.append(f"Content: {text}")
            context_parts.append("---\n")
        
        return '\n'.join(context_parts)
    
    def process_message(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Process user message with document context."""
        try:
            # Validate message
            is_valid, error = self.validate_message(user_message)
            if not is_valid:
                return f"Invalid message: {error}"
            
            if not user_id:
                return "User ID is required for PDF research."
            
            # Search documents for relevant content
            search_results = self.search_documents(
                user_id=user_id,
                query=user_message,
                n_results=5
            )
            
            # Format context
            document_context = self.format_context_from_results(search_results)
            
            # Prepare enhanced message with context
            enhanced_message = f"""User Question: {user_message}

{document_context}

Based on the above document content, please provide a detailed answer to the user's question. 
Include specific citations (document name and page number) when referencing information from the documents.
If the answer is not found in the documents, clearly state that."""
            
            # Get response from LLM
            response = self.openai_service.chat_completion_with_system(
                system_prompt=self.get_system_prompt(),
                user_message=enhanced_message,
                conversation_history=self.format_conversation_history(conversation_history),
                temperature=0.3,  # Lower temperature for factual responses
                stream=False
            )
            
            return response
            
        except Exception as e:
            return self.handle_error(e)
    
    def process_message_stream(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Iterator[str]:
        """Process user message with document context and stream response."""
        try:
            # Validate message
            is_valid, error = self.validate_message(user_message)
            if not is_valid:
                yield f"Invalid message: {error}"
                return
            
            if not user_id:
                yield "User ID is required for PDF research."
                return
            
            # Search documents for relevant content
            search_results = self.search_documents(
                user_id=user_id,
                query=user_message,
                n_results=5
            )
            
            # Format context
            document_context = self.format_context_from_results(search_results)
            
            # Prepare enhanced message with context
            enhanced_message = f"""User Question: {user_message}

{document_context}

Based on the above document content, please provide a detailed answer to the user's question. 
Include specific citations (document name and page number) when referencing information from the documents.
If the answer is not found in the documents, clearly state that."""
            
            # Stream response from LLM
            response_stream = self.openai_service.chat_completion_with_system(
                system_prompt=self.get_system_prompt(),
                user_message=enhanced_message,
                conversation_history=self.format_conversation_history(conversation_history),
                temperature=0.3,
                stream=True
            )
            
            for chunk in response_stream:
                yield chunk
                
        except Exception as e:
            yield self.handle_error(e)
    
    def get_status_updates(self) -> Iterator[str]:
        """Generate status updates for PDF processing."""
        yield "Initializing PDF Research Agent..."
        yield "Searching uploaded documents..."
        yield "Retrieving relevant passages..."
        yield "Analyzing document content..."
        yield "Generating response with citations..."
    
    def list_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List all documents for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of document information
        """
        try:
            return self.document_repository.list_user_documents(user_id)
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []
    
    def delete_document(self, user_id: str, document_id: str) -> bool:
        """
        Delete a document.
        
        Args:
            user_id: User identifier
            document_id: Document identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.document_repository.delete_pdf_document(user_id, document_id)
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
