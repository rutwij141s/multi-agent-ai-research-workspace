"""
Tests for service layer.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from services.pdf_service import PDFService
from services.citation_service import CitationService
from utils.helpers import (
    generate_id,
    sanitize_filename,
    chunk_text,
    validate_input
)


class TestPDFService:
    """Test PDF service functionality."""
    
    def test_chunk_text(self):
        """Test text chunking."""
        service = PDFService()
        text = "This is a test. " * 100  # Create long text
        
        chunks = chunk_text(text, chunk_size=100, overlap=20)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 120 for chunk in chunks)  # Allow for overlap


class TestCitationService:
    """Test citation service functionality."""
    
    def test_format_citation_simple(self):
        """Test simple citation formatting."""
        service = CitationService()
        source = {
            'title': 'Test Article',
            'url': 'https://example.com/article',
            'domain': 'example.com'
        }
        
        citation = service.format_citation(source, style='simple')
        
        assert 'Test Article' in citation
        assert 'example.com' in citation
    
    def test_format_citation_markdown(self):
        """Test markdown citation formatting."""
        service = CitationService()
        source = {
            'title': 'Test Article',
            'url': 'https://example.com/article'
        }
        
        citation = service.format_citation(source, style='markdown')
        
        assert '[Test Article]' in citation
        assert '(https://example.com/article)' in citation
    
    def test_deduplicate_sources(self):
        """Test source deduplication."""
        service = CitationService()
        sources = [
            {'title': 'Article 1', 'url': 'https://example.com/1'},
            {'title': 'Article 2', 'url': 'https://example.com/2'},
            {'title': 'Article 1 Duplicate', 'url': 'https://example.com/1'},
        ]
        
        unique = service.deduplicate_sources(sources)
        
        assert len(unique) == 2
        assert unique[0]['url'] == 'https://example.com/1'
        assert unique[1]['url'] == 'https://example.com/2'
    
    def test_rank_sources(self):
        """Test source ranking."""
        service = CitationService()
        sources = [
            {
                'title': 'Test Article',
                'snippet': 'Short snippet',
                'domain': 'example.com'
            },
            {
                'title': 'Test Research Article',
                'snippet': 'Long snippet with more content and information',
                'domain': 'university.edu'
            }
        ]
        
        ranked = service.rank_sources(sources, query='test research')
        
        # .edu should rank higher
        assert 'edu' in ranked[0]['domain']


class TestHelpers:
    """Test helper utilities."""
    
    def test_generate_id(self):
        """Test ID generation."""
        id1 = generate_id()
        id2 = generate_id()
        
        assert id1 != id2
        assert len(id1) > 0
        assert isinstance(id1, str)
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert sanitize_filename('test.pdf') == 'test.pdf'
        assert sanitize_filename('test/file.pdf') == 'test_file.pdf'
        assert sanitize_filename('test\\file.pdf') == 'test_file.pdf'
        assert sanitize_filename('test:file.pdf') == 'test_file.pdf'
        assert sanitize_filename('') != ''  # Should generate a name
    
    def test_chunk_text_basic(self):
        """Test basic text chunking."""
        text = "A" * 1000
        chunks = chunk_text(text, chunk_size=100, overlap=10)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 110 for chunk in chunks)
    
    def test_chunk_text_empty(self):
        """Test chunking empty text."""
        chunks = chunk_text("", chunk_size=100, overlap=10)
        
        assert len(chunks) == 0
    
    def test_validate_input(self):
        """Test input validation."""
        from utils.error_handlers import validate_input
        
        # Required field
        valid, error = validate_input("test", "field", required=True)
        assert valid is True
        
        valid, error = validate_input("", "field", required=True)
        assert valid is False
        assert "required" in error.lower()
        
        # Length validation
        valid, error = validate_input("test", "field", min_length=5)
        assert valid is False
        assert "5 characters" in error
        
        valid, error = validate_input("test", "field", max_length=3)
        assert valid is False
        assert "3 characters" in error
        
        # Type validation
        valid, error = validate_input(123, "field", allowed_types=(str,))
        assert valid is False
