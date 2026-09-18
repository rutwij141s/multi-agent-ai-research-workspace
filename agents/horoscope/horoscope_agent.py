"""
Horoscope Research Agent for aRe_Agent application.
Provides personalized horoscope insights with real-time web research.
"""

from typing import Iterator, Optional, Dict, Any, List
from datetime import datetime

from agents.base_agent import BaseAgent
from services.research_service import get_research_service
from services.citation_service import get_citation_service
from utils.logging import get_logger
from utils.helpers import parse_date

logger = get_logger(__name__)


class HoroscopeAgent(BaseAgent):
    """Agent for horoscope research and personalized astrology insights."""
    
    def __init__(self):
        """Initialize Horoscope Agent."""
        super().__init__(
            agent_type="horoscope",
            name="Horoscope Research Agent",
            description="Get personalized horoscope insights based on real-time research from multiple sources"
        )
        self.research_service = get_research_service()
        self.citation_service = get_citation_service()
        
        self.zodiac_signs = {
            'aries': (3, 21, 4, 19),
            'taurus': (4, 20, 5, 20),
            'gemini': (5, 21, 6, 20),
            'cancer': (6, 21, 7, 22),
            'leo': (7, 23, 8, 22),
            'virgo': (8, 23, 9, 22),
            'libra': (9, 23, 10, 22),
            'scorpio': (10, 23, 11, 21),
            'sagittarius': (11, 22, 12, 21),
            'capricorn': (12, 22, 1, 19),
            'aquarius': (1, 20, 2, 18),
            'pisces': (2, 19, 3, 20)
        }
    
    def get_system_prompt(self) -> str:
        """Get system prompt for Horoscope Agent."""
        return """You are a Horoscope Research Agent specializing in astrology and personalized horoscope insights.

Your responsibilities:
- Provide personalized horoscope readings based on birth date and zodiac sign
- Synthesize information from multiple research sources
- Clearly distinguish between sourced information and interpretive content
- Offer daily, weekly, and monthly horoscopes
- Provide insights into planetary transits and astrological events
- Maintain a balanced, thoughtful tone

Guidelines:
- Base factual astronomical information on research sources
- Clearly separate researched facts from astrological interpretation
- Number and mention actual sources used when providing researched information
- If fewer sources are available than expected, state the actual number
- Never fabricate sources or citations
- Acknowledge uncertainty when information is limited
- Provide personalized insights based on the user's zodiac sign
- Be respectful of different beliefs about astrology

Remember: Transparency about sources and the research process is essential. Users should understand what information comes from research versus interpretation."""
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities."""
        return [
            "Personalized horoscope readings",
            "Daily, weekly, and monthly horoscopes",
            "Real-time research from 20-30 sources",
            "Zodiac sign information",
            "Planetary transit information",
            "Astrological event insights",
            "Birth date analysis",
            "Source-based interpretations"
        ]
    
    def determine_zodiac_sign(self, birth_date: datetime) -> str:
        """
        Determine zodiac sign from birth date.
        
        Args:
            birth_date: Date of birth
            
        Returns:
            Zodiac sign name
        """
        month = birth_date.month
        day = birth_date.day
        
        for sign, (start_month, start_day, end_month, end_day) in self.zodiac_signs.items():
            if (month == start_month and day >= start_day) or (month == end_month and day <= end_day):
                return sign.capitalize()
        
        return "Unknown"
    
    def conduct_horoscope_research(
        self,
        zodiac_sign: str,
        period: str = "daily",
        include_transits: bool = False
    ) -> Dict[str, Any]:
        """
        Conduct web research for horoscope information.
        
        Args:
            zodiac_sign: User's zodiac sign
            period: Period (daily, weekly, monthly)
            include_transits: Whether to include planetary transit information
            
        Returns:
            Research results dictionary
        """
        try:
            logger.info(f"Conducting horoscope research for {zodiac_sign} ({period})")
            
            # Build research queries
            queries = [
                f"{zodiac_sign} {period} horoscope {datetime.now().strftime('%Y %B')}",
                f"{zodiac_sign} horoscope today",
                f"{zodiac_sign} astrology {period}"
            ]
            
            if include_transits:
                queries.append(f"planetary transits {zodiac_sign} astrology")
            
            # Conduct research
            all_sources = []
            
            for query in queries:
                results = self.research_service.search_web(
                    query=query,
                    max_results=10
                )
                all_sources.extend(results)
            
            # Deduplicate and rank sources
            unique_sources = self.citation_service.deduplicate_sources(all_sources)
            ranked_sources = self.citation_service.rank_sources(unique_sources, zodiac_sign)
            
            # Limit to reasonable number
            final_sources = ranked_sources[:30]
            
            logger.info(f"Completed research with {len(final_sources)} sources")
            
            return {
                'zodiac_sign': zodiac_sign,
                'period': period,
                'sources': final_sources,
                'source_count': len(final_sources),
                'queries_used': queries
            }
            
        except Exception as e:
            logger.error(f"Error conducting horoscope research: {e}")
            return {
                'zodiac_sign': zodiac_sign,
                'period': period,
                'sources': [],
                'source_count': 0,
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
            return "No research sources were found. Please provide a horoscope based on general astrological knowledge."
        
        context_parts = [
            f"Based on research from {len(sources)} sources:\n"
        ]
        
        for i, source in enumerate(sources[:15], 1):  # Include top 15 in context
            title = source.get('title', 'Unknown')
            snippet = source.get('snippet', '')
            domain = source.get('domain', '')
            
            context_parts.append(f"\nSource {i}: {title} ({domain})")
            context_parts.append(f"Content: {snippet}\n")
        
        # Add source summary
        context_parts.append(f"\n\nTotal sources researched: {len(sources)}")
        context_parts.append(self.citation_service.create_source_summary(sources))
        
        return '\n'.join(context_parts)
    
    def process_message(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Process user message for horoscope request."""
        try:
            # Validate message
            is_valid, error = self.validate_message(user_message)
            if not is_valid:
                return f"Invalid message: {error}"
            
            # Extract parameters from kwargs
            birth_date_str = kwargs.get('birth_date')
            zodiac_sign = kwargs.get('zodiac_sign', '').capitalize()
            period = kwargs.get('period', 'daily').lower()
            
            # Determine zodiac sign if birth date provided
            if birth_date_str and not zodiac_sign:
                birth_date = parse_date(birth_date_str)
                if birth_date:
                    zodiac_sign = self.determine_zodiac_sign(birth_date)
            
            # Conduct research if sign is known
            research_data = None
            if zodiac_sign and zodiac_sign.lower() in self.zodiac_signs:
                research_data = self.conduct_horoscope_research(
                    zodiac_sign=zodiac_sign,
                    period=period,
                    include_transits=kwargs.get('include_transits', False)
                )
            
            # Format context
            if research_data:
                research_context = self.format_research_context(research_data)
                enhanced_message = f"""User Request: {user_message}

Zodiac Sign: {zodiac_sign}
Period: {period}

Research Information:
{research_context}

Please provide a personalized horoscope reading based on the research above. 
Clearly distinguish between information from sources and your interpretive insights.
Mention the number of sources used and provide a balanced, thoughtful reading."""
            else:
                enhanced_message = f"""User Request: {user_message}

Please provide astrological insights for this request.
Note: No specific zodiac sign or birth date was provided, so provide general guidance."""
            
            # Get response from LLM
            response = self.openai_service.chat_completion_with_system(
                system_prompt=self.get_system_prompt(),
                user_message=enhanced_message,
                conversation_history=self.format_conversation_history(conversation_history),
                temperature=0.7,
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
        """Process user message and stream horoscope response."""
        try:
            # Validate message
            is_valid, error = self.validate_message(user_message)
            if not is_valid:
                yield f"Invalid message: {error}"
                return
            
            # Extract parameters
            birth_date_str = kwargs.get('birth_date')
            zodiac_sign = kwargs.get('zodiac_sign', '').capitalize()
            period = kwargs.get('period', 'daily').lower()
            
            # Determine zodiac sign
            if birth_date_str and not zodiac_sign:
                birth_date = parse_date(birth_date_str)
                if birth_date:
                    zodiac_sign = self.determine_zodiac_sign(birth_date)
            
            # Conduct research
            research_data = None
            if zodiac_sign and zodiac_sign.lower() in self.zodiac_signs:
                research_data = self.conduct_horoscope_research(
                    zodiac_sign=zodiac_sign,
                    period=period,
                    include_transits=kwargs.get('include_transits', False)
                )
            
            # Format context
            if research_data:
                research_context = self.format_research_context(research_data)
                enhanced_message = f"""User Request: {user_message}

Zodiac Sign: {zodiac_sign}
Period: {period}

Research Information:
{research_context}

Please provide a personalized horoscope reading based on the research above. 
Clearly distinguish between information from sources and your interpretive insights.
Mention the number of sources used and provide a balanced, thoughtful reading."""
            else:
                enhanced_message = f"""User Request: {user_message}

Please provide astrological insights for this request.
Note: No specific zodiac sign or birth date was provided, so provide general guidance."""
            
            # Stream response
            response_stream = self.openai_service.chat_completion_with_system(
                system_prompt=self.get_system_prompt(),
                user_message=enhanced_message,
                conversation_history=self.format_conversation_history(conversation_history),
                temperature=0.7,
                stream=True
            )
            
            for chunk in response_stream:
                yield chunk
                
        except Exception as e:
            yield self.handle_error(e)
    
    def get_status_updates(self) -> Iterator[str]:
        """Generate status updates for horoscope research."""
        yield "Initializing Horoscope Research Agent..."
        yield "Collecting current astrological information..."
        yield "Researching from multiple sources..."
        yield "Analyzing planetary positions..."
        yield "Synthesizing personalized insights..."
        yield "Generating horoscope reading..."
