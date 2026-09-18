"""
Base agent class for aRe_Agent application.
Defines the interface that all agents must implement.
"""

from abc import ABC, abstractmethod
from typing import Iterator, Optional, Dict, Any, List

from services.openai_service import get_openai_service
from utils.logging import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, agent_type: str, name: str, description: str):
        """
        Initialize base agent.
        
        Args:
            agent_type: Unique agent type identifier
            name: Display name for the agent
            description: Agent description
        """
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.openai_service = get_openai_service()
        
        logger.info(f"Initialized agent: {name} ({agent_type})")
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.
        
        Returns:
            System prompt string
        """
        pass
    
    @abstractmethod
    def process_message(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Process a user message and return a response.
        
        Args:
            user_message: User's message
            conversation_history: Optional conversation history
            user_id: Optional user identifier
            **kwargs: Additional agent-specific parameters
            
        Returns:
            Agent response
        """
        pass
    
    @abstractmethod
    def process_message_stream(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Iterator[str]:
        """
        Process a user message and stream the response.
        
        Args:
            user_message: User's message
            conversation_history: Optional conversation history
            user_id: Optional user identifier
            **kwargs: Additional agent-specific parameters
            
        Yields:
            Response chunks
        """
        pass
    
    def get_capabilities(self) -> List[str]:
        """
        Get list of agent capabilities.
        
        Returns:
            List of capability descriptions
        """
        return []
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get agent metadata.
        
        Returns:
            Dictionary of agent metadata
        """
        return {
            'agent_type': self.agent_type,
            'name': self.name,
            'description': self.description,
            'capabilities': self.get_capabilities()
        }
    
    def format_conversation_history(
        self,
        history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """
        Format conversation history for OpenAI API.
        
        Args:
            history: Raw conversation history
            
        Returns:
            Formatted history for API
        """
        if not history:
            return []
        
        formatted = []
        for msg in history:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role in ['user', 'assistant', 'system']:
                formatted.append({
                    'role': role,
                    'content': content
                })
        
        return formatted
    
    def validate_message(self, message: str) -> tuple[bool, Optional[str]]:
        """
        Validate user message.
        
        Args:
            message: User message
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not message or not message.strip():
            return False, "Message cannot be empty"
        
        if len(message) > 10000:
            return False, "Message is too long (max 10,000 characters)"
        
        return True, None
    
    def get_status_updates(self) -> Iterator[str]:
        """
        Generate status updates during processing.
        
        Yields:
            Status update strings
        """
        yield f"Initializing {self.name}..."
        yield "Understanding request..."
        yield "Generating response..."
    
    def handle_error(self, error: Exception) -> str:
        """
        Handle and format errors.
        
        Args:
            error: Exception that occurred
            
        Returns:
            User-friendly error message
        """
        error_msg = str(error)
        logger.error(f"Agent error in {self.name}: {error_msg}")
        
        return f"I encountered an error while processing your request: {error_msg}"
    
    def __str__(self) -> str:
        """String representation of agent."""
        return f"{self.name} ({self.agent_type})"
    
    def __repr__(self) -> str:
        """Representation of agent."""
        return f"<{self.__class__.__name__} type={self.agent_type} name={self.name}>"
