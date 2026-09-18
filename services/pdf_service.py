"""
PDF processing service for aRe_Agent application.
Handles PDF text extraction and processing.
"""

from pathlib import Path
from typing import List, Dict, Optional, BinaryIO
import PyPDF2
import pdfplumber

from utils.config import config
from utils.logging import get_logger
from utils.helpers import hash_file, chunk_text, clean_text, generate_id

logger = get_logger(__name__)


class PDFService:
    """Service for PDF document processing."""
    
    def __init__(self):
        """Initialize PDF service."""
        self.chunk_size = 1000
        self.chunk_overlap = 200
        logger.info("PDF service initialized")
    
    def extract_text_from_pdf(self, pdf_file: BinaryIO, filename: str) -> Dict[str, any]:
        """
        Extract text from PDF file.
        
        Args:
            pdf_file: Binary file object
            filename: Name of the file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            logger.info(f"Extracting text from PDF: {filename}")
            
            # Try pdfplumber first (better text extraction)
            text_by_page = []
            total_text = ""
            
            try:
                with pdfplumber.open(pdf_file) as pdf:
                    num_pages = len(pdf.pages)
                    
                    for page_num, page in enumerate(pdf.pages, 1):
                        page_text = page.extract_text() or ""
                        text_by_page.append({
                            'page': page_num,
                            'text': clean_text(page_text)
                        })
                        total_text += page_text + "\n\n"
                
                logger.info(f"Extracted text from {num_pages} pages using pdfplumber")
                
            except Exception as e:
                logger.warning(f"pdfplumber failed, trying PyPDF2: {e}")
                
                # Fallback to PyPDF2
                pdf_file.seek(0)  # Reset file pointer
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text() or ""
                    text_by_page.append({
                        'page': page_num + 1,
                        'text': clean_text(page_text)
                    })
                    total_text += page_text + "\n\n"
                
                logger.info(f"Extracted text from {num_pages} pages using PyPDF2")
            
            total_text = clean_text(total_text)
            
            result = {
                'filename': filename,
                'num_pages': len(text_by_page),
                'text_by_page': text_by_page,
                'total_text': total_text,
                'total_chars': len(total_text),
                'success': True
            }
            
            logger.info(f"Successfully extracted {len(total_text)} characters from {filename}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {filename}: {e}")
            return {
                'filename': filename,
                'num_pages': 0,
                'text_by_page': [],
                'total_text': "",
                'total_chars': 0,
                'success': False,
                'error': str(e)
            }
    
    def chunk_pdf_text(
        self,
        pdf_data: Dict[str, any],
        include_page_numbers: bool = True
    ) -> List[Dict[str, any]]:
        """
        Split PDF text into chunks for embedding.
        
        Args:
            pdf_data: Dictionary from extract_text_from_pdf
            include_page_numbers: Whether to track page numbers in chunks
            
        Returns:
            List of chunk dictionaries
        """
        try:
            chunks = []
            
            if include_page_numbers:
                # Chunk by page
                for page_data in pdf_data.get('text_by_page', []):
                    page_num = page_data['page']
                    page_text = page_data['text']
                    
                    if not page_text.strip():
                        continue
                    
                    # Split page into smaller chunks if needed
                    page_chunks = chunk_text(
                        page_text,
                        chunk_size=self.chunk_size,
                        overlap=self.chunk_overlap
                    )
                    
                    for i, chunk_text in enumerate(page_chunks):
                        chunks.append({
                            'chunk_id': generate_id(),
                            'text': chunk_text,
                            'page': page_num,
                            'chunk_index': i,
                            'filename': pdf_data['filename']
                        })
            else:
                # Chunk entire document
                total_text = pdf_data.get('total_text', '')
                text_chunks = chunk_text(
                    total_text,
                    chunk_size=self.chunk_size,
                    overlap=self.chunk_overlap
                )
                
                for i, chunk_text in enumerate(text_chunks):
                    chunks.append({
                        'chunk_id': generate_id(),
                        'text': chunk_text,
                        'chunk_index': i,
                        'filename': pdf_data['filename']
                    })
            
            logger.info(f"Created {len(chunks)} chunks from {pdf_data['filename']}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking PDF text: {e}")
            return []
    
    def extract_metadata(self, pdf_file: BinaryIO) -> Dict[str, any]:
        """
        Extract metadata from PDF.
        
        Args:
            pdf_file: Binary file object
            
        Returns:
            Dictionary of metadata
        """
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            metadata = pdf_reader.metadata or {}
            
            return {
                'title': metadata.get('/Title', ''),
                'author': metadata.get('/Author', ''),
                'subject': metadata.get('/Subject', ''),
                'creator': metadata.get('/Creator', ''),
                'producer': metadata.get('/Producer', ''),
                'creation_date': metadata.get('/CreationDate', ''),
            }
        except Exception as e:
            logger.error(f"Error extracting PDF metadata: {e}")
            return {}
    
    def validate_pdf(self, pdf_file: BinaryIO) -> tuple[bool, Optional[str]]:
        """
        Validate that file is a valid PDF.
        
        Args:
            pdf_file: Binary file object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Check if encrypted
            if pdf_reader.is_encrypted:
                return False, "PDF is password-protected"
            
            # Check if has pages
            if len(pdf_reader.pages) == 0:
                return False, "PDF has no pages"
            
            # Try to extract text from first page
            first_page = pdf_reader.pages[0]
            _ = first_page.extract_text()
            
            pdf_file.seek(0)  # Reset file pointer
            return True, None
            
        except Exception as e:
            logger.error(f"PDF validation failed: {e}")
            return False, f"Invalid or corrupted PDF: {str(e)}"
    
    def get_pdf_info(self, pdf_file: BinaryIO, filename: str) -> Dict[str, any]:
        """
        Get comprehensive PDF information.
        
        Args:
            pdf_file: Binary file object
            filename: Name of the file
            
        Returns:
            Dictionary of PDF information
        """
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            metadata = self.extract_metadata(pdf_file)
            pdf_file.seek(0)
            
            return {
                'filename': filename,
                'num_pages': len(pdf_reader.pages),
                'is_encrypted': pdf_reader.is_encrypted,
                'metadata': metadata
            }
        except Exception as e:
            logger.error(f"Error getting PDF info: {e}")
            return {
                'filename': filename,
                'error': str(e)
            }


# Singleton instance
_pdf_service = None


def get_pdf_service() -> PDFService:
    """Get or create PDF service instance."""
    global _pdf_service
    if _pdf_service is None:
        _pdf_service = PDFService()
    return _pdf_service
