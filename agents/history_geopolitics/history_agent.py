"""
History & Geopolitics Agent for aRe_Agent application.
Specialized research agent for historical and geopolitical queries.
"""

from typing import Iterator, Optional, Dict, Any, List

from agents.base_agent import BaseAgent
from services.research_service import get_research_service
from services.citation_service import get_citation_service
from utils.logging import get_logger

logger = get_logger(__name__)


class HistoryGeopoliticsAgent(BaseAgent):
    """Agent for historical and geopolitical research and analysis."""
    
    def __init__(self):
        """Initialize History & Geopolitics Agent."""
        super().__init__(
            agent_type="history_geopolitics",
            name="History & Geopolitics Agent",
            description="Research-oriented agent for world history, geopolitics, and international relations"
        )
        self.research_service = get_research_service()
        self.citation_service = get_citation_service()
    
    def get_system_prompt(self) -> str:
        """Get system prompt for History & Geopolitics Agent."""
        return """You are a History & Geopolitics Research Agent specializing in historical analysis and geopolitical understanding.

Your areas of expertise:
- World history (ancient, medieval, modern)
- Wars, conflicts, and international relations
- Political history and government systems
- Economic history and trade
- Diplomatic history and treaties
- Territorial disputes and borders
- Historical causes and consequences
- Comparative historical analysis
- Current geopolitical developments

Guidelines:
- Prefer authoritative and academic sources when available
- Distinguish primary sources from secondary sources
- Provide dates and historical context
- Identify disputed historical interpretations when relevant
- Clearly separate established facts from scholarly interpretations
- Maintain neutrality on politically sensitive topics
- Avoid political persuasion or bias
- Acknowledge complexity and multiple perspectives
- For current geopolitical topics, use recent research sources
- Cite sources when providing specific historical facts or current information

Remember: Your role is to provide factual, well-researched, and balanced historical and geopolitical analysis. Acknowledge uncertainty and different scholarly interpretations when appropriate."""
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities."""
        return [
            "Historical research and analysis",
            "Geopolitical analysis",
            "International relations insights",
            "War and conflict history",
            "Political and economic history",
            "Timeline construction",
            "Comparative historical analysis",
            "Current events context",
            "Source-based research",
            "Neutral, factual presentation"
        ]
    
    def determine_if_research_needed(self, user_message: str) -> bool:
        """
        Determine if web research is needed for the query.
        
        Args:
            user_message: User's message
            
        Returns:
            True if research is recommended
        """
        # Keywords indicating current events or recent history
        current_keywords = [
            'current', 'recent', 'today', 'now', 'latest', 
            '2020', '2021', '2022', '2023', '2024', '2025', '2026',
            'ongoing', 'contemporary'
        ]
        
        message_lower = user_message.lower()
        return any(keyword in message_lower for keyword in current_keywords)
    
    def conduct_historical_research(
        self,
        query: str,
        max_sources: int = 15
    ) -> Dict[str, Any]:
        """
        Conduct web research for historical/geopolitical information.
        
        Args:
            query: Research query
            max_sources: Maximum sources to collect
            
        Returns:
            Research results dictionary
        """
        try:
            logger.info(f"Conducting historical research: {query}")
            
            # Conduct research
            research_data = self.research_service.research_topic(
                topic=query,
                context="historical geopolitical analysis",
                num_queries=2
            )
            
            sources = research_data.get('sources', [])
            
            # Rank and filter sources
            ranked_sources = self.citation_service.rank_sources(sources, query)
            filtered_sources = self.citation_service.filter_sources(ranked_sources)
            
            # Limit to max sources
            final_sources = filtered_sources[:max_sources]
            
            logger.info(f"Completed research with {len(final_sources)} sources")
            
            return {
                'query': query,
                'sources': final_sources,
                'source_count': len(final_sources),
                'research_conducted': True
            }
            
        except Exception as e:
            logger.error(f"Error conducting research: {e}")
            return {
                'query': query,
                'sources': [],
                'source_count': 0,
                'research_conducted': False,
                'error': str(e)
            }
    
    def format_research_context(self, research_data: Dict[str, Any]) -> str:
        """
        Format research results into context for LLM.
        
        Args:
            research_data: Research results
            
        Returns:
            Formatted context string
        """
        sources = research_data.get('sources', [])
        
        if not sources:
            return ""
        
        context_parts = [
            f"\n--- Research Information ({len(sources)} sources) ---\n"
        ]
        
        for i, source in enumerate(sources, 1):
            title = source.get('title', 'Unknown')
            snippet = source.get('snippet', '')
            domain = source.get('domain', '')
            url = source.get('url', '')
            
            context_parts.append(f"\nSource {i}: {title}")
            context_parts.append(f"Domain: {domain}")
            if url:
                context_parts.append(f"URL: {url}")
            context_parts.append(f"Content: {snippet}\n")
        
        context_parts.append(f"\n{self.citation_service.create_source_summary(sources)}\n")
        
        return '\n'.join(context_parts)
    
    def process_message(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Process user message for historical/geopolitical query."""
        try:
            # Validate message
            is_valid, error = self.validate_message(user_message)
            if not is_valid:
                return f"Invalid message: {error}"
            
            # Determine if research is needed
            force_research = kwargs.get('force_research', False)
            needs_research = force_research or self.determine_if_research_needed(user_message)
            
            # Conduct research if needed
            research_context = ""
            if needs_research:
                research_data = self.conduct_historical_research(user_message)
                research_context = self.format_research_context(research_data)
            
            # Prepare message
            if research_context:
                enhanced_message = f"""User Question: {user_message}
{research_context}

Based on the research above and your historical knowledge, please provide a comprehensive, 
well-sourced answer. Cite specific sources when referencing researched information.
Maintain neutrality and acknowledge different perspectives when relevant."""
            else:
                enhanced_message = f"""User Question: {user_message}

Please provide a comprehensive historical or geopolitical analysis based on established 
historical knowledge. Include relevant dates, context, and multiple perspectives when appropriate."""
            
            # Get response from LLM
            response = self.openai_service.chat_completion_with_system(
                system_prompt=self.get_system_prompt(),
                user_message=enhanced_message,
                conversation_history=self.format_conversation_history(conversation_history),
                temperature=0.5,  # Balanced temperature for factual yet analytical responses
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
        """Process user message and stream response."""
        try:
            # Validate message
            is_valid, error = self.validate_message(user_message)
            if not is_valid:
                yield f"Invalid message: {error}"
                return
            
            # Determine if research is needed
            force_research = kwargs.get('force_research', False)
            needs_research = force_research or self.determine_if_research_needed(user_message)
            
            # Conduct research if needed
            research_context = ""
            if needs_research:
                research_data = self.conduct_historical_research(user_message)
                research_context = self.format_research_context(research_data)
            
            # Prepare message
            if research_context:
                enhanced_message = f"""User Question: {user_message}
{research_context}

Based on the research above and your historical knowledge, please provide a comprehensive, 
well-sourced answer. Cite specific sources when referencing researched information.
Maintain neutrality and acknowledge different perspectives when relevant."""
            else:
                enhanced_message = f"""User Question: {user_message}

Please provide a comprehensive historical or geopolitical analysis based on established 
historical knowledge. Include relevant dates, context, and multiple perspectives when appropriate."""
            
            # Stream response
            response_stream = self.openai_service.chat_completion_with_system(
                system_prompt=self.get_system_prompt(),
                user_message=enhanced_message,
                conversation_history=self.format_conversation_history(conversation_history),
                temperature=0.5,
                stream=True
            )
            
            for chunk in response_stream:
                yield chunk
                
        except Exception as e:
            yield self.handle_error(e)
    
    def get_status_updates(self) -> Iterator[str]:
        """Generate status updates for historical research."""
        yield "Initializing History & Geopolitics Agent..."
        yield "Analyzing query context..."
        yield "Researching historical sources..."
        yield "Cross-referencing information..."
        yield "Synthesizing analysis..."
        yield "Generating response..."
