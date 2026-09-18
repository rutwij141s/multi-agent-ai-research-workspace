"""
Web research service for aRe_Agent application.
Handles real-time web research and source collection.
"""

from typing import List, Dict, Optional
import time
from datetime import datetime
from duckduckgo_search import DDGS

from utils.config import config
from utils.logging import get_logger
from utils.helpers import clean_text, extract_urls

logger = get_logger(__name__)


class ResearchService:
    """Service for conducting web research."""
    
    def __init__(self):
        """Initialize research service."""
        self.max_sources = config.MAX_RESEARCH_SOURCES
        self.timeout = config.RESEARCH_TIMEOUT_SECONDS
        logger.info(f"Research service initialized (max_sources={self.max_sources})")
    
    def search_web(
        self,
        query: str,
        max_results: Optional[int] = None,
        region: str = "wt-wt"
    ) -> List[Dict[str, str]]:
        """
        Search the web for information.
        
        Args:
            query: Search query
            max_results: Maximum number of results (None uses config default)
            region: Search region code
            
        Returns:
            List of search result dictionaries with title, url, snippet, domain
        """
        try:
            if not query or not query.strip():
                logger.warning("Empty query provided")
                return []
            
            max_results = max_results or self.max_sources
            
            logger.info(f"Searching web: '{query}' (max_results={max_results})")
            
            results = []
            
            with DDGS() as ddgs:
                search_results = ddgs.text(
                    query,
                    region=region,
                    safesearch="moderate",
                    max_results=max_results
                )
                
                for result in search_results:
                    processed_result = {
                        'title': clean_text(result.get('title', '')),
                        'url': result.get('href', ''),
                        'snippet': clean_text(result.get('body', '')),
                        'domain': self._extract_domain(result.get('href', '')),
                        'retrieved_at': datetime.now().isoformat()
                    }
                    results.append(processed_result)
            
            logger.info(f"Found {len(results)} search results")
            return results
            
        except Exception as e:
            logger.error(f"Error during web search: {e}")
            return []
    
    def research_topic(
        self,
        topic: str,
        context: Optional[str] = None,
        num_queries: int = 3
    ) -> Dict[str, any]:
        """
        Conduct comprehensive research on a topic using multiple search queries.
        
        Args:
            topic: Main topic to research
            context: Additional context to refine research
            num_queries: Number of different search queries to perform
            
        Returns:
            Dictionary containing sources and metadata
        """
        try:
            logger.info(f"Researching topic: '{topic}'")
            
            # Generate multiple search queries
            queries = self._generate_queries(topic, context, num_queries)
            
            all_sources = []
            seen_urls = set()
            
            # Perform searches
            results_per_query = max(10, self.max_sources // num_queries)
            
            for query in queries:
                results = self.search_web(query, max_results=results_per_query)
                
                # Deduplicate by URL
                for result in results:
                    url = result.get('url', '')
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_sources.append(result)
                
                # Respect rate limits
                time.sleep(0.5)
            
            # Limit to max sources
            all_sources = all_sources[:self.max_sources]
            
            research_data = {
                'topic': topic,
                'queries_used': queries,
                'sources': all_sources,
                'total_sources': len(all_sources),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Research completed: {len(all_sources)} unique sources found")
            return research_data
            
        except Exception as e:
            logger.error(f"Error during topic research: {e}")
            return {
                'topic': topic,
                'queries_used': [],
                'sources': [],
                'total_sources': 0,
                'error': str(e)
            }
    
    def _generate_queries(
        self,
        topic: str,
        context: Optional[str],
        num_queries: int
    ) -> List[str]:
        """
        Generate multiple search queries for a topic.
        
        Args:
            topic: Main topic
            context: Additional context
            num_queries: Number of queries to generate
            
        Returns:
            List of search queries
        """
        queries = [topic]
        
        if num_queries > 1 and context:
            queries.append(f"{topic} {context}")
        
        if num_queries > 2:
            queries.append(f"{topic} latest information")
        
        if num_queries > 3:
            queries.append(f"{topic} facts")
        
        return queries[:num_queries]
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.
        
        Args:
            url: Full URL
            
        Returns:
            Domain name
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return ""
    
    def filter_sources(
        self,
        sources: List[Dict[str, str]],
        min_snippet_length: int = 50
    ) -> List[Dict[str, str]]:
        """
        Filter sources based on quality criteria.
        
        Args:
            sources: List of source dictionaries
            min_snippet_length: Minimum snippet length to keep
            
        Returns:
            Filtered list of sources
        """
        filtered = []
        
        for source in sources:
            snippet = source.get('snippet', '')
            
            # Filter out low-quality sources
            if len(snippet) < min_snippet_length:
                continue
            
            # Check for required fields
            if not source.get('url') or not source.get('title'):
                continue
            
            filtered.append(source)
        
        logger.debug(f"Filtered {len(sources)} sources to {len(filtered)}")
        return filtered
    
    def format_sources_for_display(self, sources: List[Dict[str, str]]) -> str:
        """
        Format sources for user-friendly display.
        
        Args:
            sources: List of source dictionaries
            
        Returns:
            Formatted string
        """
        if not sources:
            return "No sources available."
        
        formatted_lines = [f"\n### Sources ({len(sources)} found)\n"]
        
        for i, source in enumerate(sources, 1):
            title = source.get('title', 'Unknown')
            url = source.get('url', '')
            domain = source.get('domain', '')
            
            formatted_lines.append(f"{i}. **{title}**")
            if url:
                formatted_lines.append(f"   - {url}")
            if domain:
                formatted_lines.append(f"   - Domain: {domain}")
            formatted_lines.append("")
        
        return '\n'.join(formatted_lines)


# Singleton instance
_research_service = None


def get_research_service() -> ResearchService:
    """Get or create research service instance."""
    global _research_service
    if _research_service is None:
        _research_service = ResearchService()
    return _research_service
