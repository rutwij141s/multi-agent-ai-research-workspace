"""
Citation service for aRe_Agent application.
Handles citation formatting and source management.
"""

from typing import List, Dict, Optional
from datetime import datetime

from utils.logging import get_logger
from utils.helpers import truncate_text

logger = get_logger(__name__)


class CitationService:
    """Service for managing citations and sources."""
    
    def __init__(self):
        """Initialize citation service."""
        logger.info("Citation service initialized")
    
    def format_citation(
        self,
        source: Dict[str, str],
        style: str = "simple"
    ) -> str:
        """
        Format a single citation.
        
        Args:
            source: Source dictionary with title, url, domain, etc.
            style: Citation style (simple, academic, markdown)
            
        Returns:
            Formatted citation string
        """
        try:
            title = source.get('title', 'Unknown Source')
            url = source.get('url', '')
            domain = source.get('domain', '')
            retrieved_at = source.get('retrieved_at', '')
            
            if style == "academic":
                citation = f"{title}."
                if domain:
                    citation += f" {domain}."
                if retrieved_at:
                    try:
                        date = datetime.fromisoformat(retrieved_at).strftime("%Y-%m-%d")
                        citation += f" Retrieved {date}."
                    except:
                        pass
                if url:
                    citation += f" {url}"
                return citation
            
            elif style == "markdown":
                if url:
                    return f"[{title}]({url})"
                else:
                    return f"**{title}** ({domain})"
            
            else:  # simple
                if url:
                    return f"{title} - {url}"
                else:
                    return f"{title} ({domain})"
                    
        except Exception as e:
            logger.error(f"Error formatting citation: {e}")
            return "Unknown Source"
    
    def format_citation_list(
        self,
        sources: List[Dict[str, str]],
        style: str = "markdown",
        numbered: bool = True
    ) -> str:
        """
        Format a list of citations.
        
        Args:
            sources: List of source dictionaries
            style: Citation style
            numbered: Whether to number citations
            
        Returns:
            Formatted citations string
        """
        if not sources:
            return "No sources available."
        
        lines = []
        
        for i, source in enumerate(sources, 1):
            citation = self.format_citation(source, style)
            
            if numbered:
                lines.append(f"{i}. {citation}")
            else:
                lines.append(f"- {citation}")
        
        return '\n'.join(lines)
    
    def create_pdf_citation(
        self,
        filename: str,
        page: Optional[int] = None,
        chunk_text: Optional[str] = None
    ) -> str:
        """
        Create citation for PDF source.
        
        Args:
            filename: PDF filename
            page: Page number
            chunk_text: Text excerpt for context
            
        Returns:
            Formatted PDF citation
        """
        citation = f"**{filename}**"
        
        if page:
            citation += f", page {page}"
        
        if chunk_text:
            excerpt = truncate_text(chunk_text, max_length=100)
            citation += f"\n> {excerpt}"
        
        return citation
    
    def deduplicate_sources(
        self,
        sources: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Remove duplicate sources based on URL.
        
        Args:
            sources: List of source dictionaries
            
        Returns:
            Deduplicated list of sources
        """
        seen_urls = set()
        unique_sources = []
        
        for source in sources:
            url = source.get('url', '')
            
            if not url:
                # Keep sources without URLs
                unique_sources.append(source)
                continue
            
            if url not in seen_urls:
                seen_urls.add(url)
                unique_sources.append(source)
        
        logger.debug(f"Deduplicated {len(sources)} sources to {len(unique_sources)}")
        return unique_sources
    
    def rank_sources(
        self,
        sources: List[Dict[str, str]],
        query: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Rank sources by relevance and quality.
        
        Args:
            sources: List of source dictionaries
            query: Optional query for relevance scoring
            
        Returns:
            Ranked list of sources
        """
        try:
            scored_sources = []
            
            for source in sources:
                score = 0
                
                title = source.get('title', '').lower()
                snippet = source.get('snippet', '').lower()
                domain = source.get('domain', '').lower()
                
                # Quality indicators
                if len(snippet) > 200:
                    score += 2
                elif len(snippet) > 100:
                    score += 1
                
                # Domain reputation (simple heuristics)
                trusted_domains = ['edu', 'gov', 'org']
                if any(td in domain for td in trusted_domains):
                    score += 3
                
                # Relevance to query
                if query:
                    query_lower = query.lower()
                    query_terms = query_lower.split()
                    
                    for term in query_terms:
                        if len(term) > 3:  # Skip short words
                            if term in title:
                                score += 2
                            if term in snippet:
                                score += 1
                
                scored_sources.append((score, source))
            
            # Sort by score (descending)
            scored_sources.sort(key=lambda x: x[0], reverse=True)
            
            ranked = [source for _, source in scored_sources]
            logger.debug(f"Ranked {len(sources)} sources")
            return ranked
            
        except Exception as e:
            logger.error(f"Error ranking sources: {e}")
            return sources
    
    def extract_key_points(
        self,
        sources: List[Dict[str, str]],
        max_points: int = 5
    ) -> List[str]:
        """
        Extract key points from sources.
        
        Args:
            sources: List of source dictionaries
            max_points: Maximum number of points to extract
            
        Returns:
            List of key point strings
        """
        key_points = []
        
        for source in sources[:max_points]:
            snippet = source.get('snippet', '')
            
            if snippet:
                # Take first sentence or up to 150 chars
                first_sentence = snippet.split('.')[0]
                if len(first_sentence) > 150:
                    first_sentence = first_sentence[:150] + "..."
                
                key_points.append(first_sentence)
        
        return key_points
    
    def create_source_summary(self, sources: List[Dict[str, str]]) -> str:
        """
        Create a summary of sources used.
        
        Args:
            sources: List of source dictionaries
            
        Returns:
            Summary string
        """
        if not sources:
            return "No sources were used for this response."
        
        num_sources = len(sources)
        domains = list(set(s.get('domain', 'unknown') for s in sources))
        
        summary = f"Based on research from {num_sources} sources"
        
        if domains and len(domains) <= 5:
            domain_list = ", ".join(domains)
            summary += f" including: {domain_list}"
        
        return summary + "."


# Singleton instance
_citation_service = None


def get_citation_service() -> CitationService:
    """Get or create citation service instance."""
    global _citation_service
    if _citation_service is None:
        _citation_service = CitationService()
    return _citation_service
