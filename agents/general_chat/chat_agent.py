"""
General Chat Agent for aRe_Agent application.
Provides general-purpose AI assistance for various tasks.
"""

from typing import Iterator, Optional, Dict, Any, List

from agents.base_agent import BaseAgent
from utils.logging import get_logger

logger = get_logger(__name__)


class GeneralChatAgent(BaseAgent):
    """Agent for general-purpose conversational AI assistance."""
    
    def __init__(self):
        """Initialize General Chat Agent."""
        super().__init__(
            agent_type="general_chat",
            name="General AI Agent",
            description="General-purpose AI assistant for conversations, coding, writing, and problem-solving"
        )
    
    def get_system_prompt(self) -> str:
        """Get system prompt for General Chat Agent."""
        return """You are a General AI Assistant designed to help users with a wide variety of tasks.

Your capabilities include:
- Natural language conversations and discussions
- Code generation, debugging, and explanation
- Writing assistance (essays, emails, creative writing)
- Problem-solving and brainstorming
- Technical explanations and tutorials
- Research assistance and information synthesis
- Data analysis and interpretation
- Structured outputs (lists, tables, markdown)

Guidelines:
- Be helpful, accurate, and professional
- Adapt your tone to match the user's needs
- Provide clear explanations for complex topics
- Use markdown formatting for better readability
- Include code blocks with proper syntax highlighting when relevant
- Ask clarifying questions when the request is ambiguous
- Break down complex problems into manageable steps
- Cite sources or acknowledge when information may be uncertain

Remember: You're a versatile assistant capable of handling diverse requests across many domains. Maintain context throughout the conversation and provide thoughtful, well-structured responses."""
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities."""
        return [
            "Natural language conversations",
            "Code generation and debugging",
            "Writing and editing assistance",
            "Technical explanations",
            "Problem-solving and brainstorming",
            "Research and analysis",
            "Markdown formatting",
            "Multi-turn conversations with context",
            "Structured outputs (tables, lists)",
            "Creative and technical content"
        ]
    
    def process_message(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Process user message for general chat."""
        try:
            # Validate message
            is_valid, error = self.validate_message(user_message)
            if not is_valid:
                return f"Invalid message: {error}"
            
            # Get response from LLM
            response = self.openai_service.chat_completion_with_system(
                system_prompt=self.get_system_prompt(),
                user_message=user_message,
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
        """Process user message and stream response."""
        try:
            # Validate message
            is_valid, error = self.validate_message(user_message)
            if not is_valid:
                yield f"Invalid message: {error}"
                return
            
            # Stream response from LLM
            response_stream = self.openai_service.chat_completion_with_system(
                system_prompt=self.get_system_prompt(),
                user_message=user_message,
                conversation_history=self.format_conversation_history(conversation_history),
                temperature=0.7,
                stream=True
            )
            
            for chunk in response_stream:
                yield chunk
                
        except Exception as e:
            yield self.handle_error(e)
    
    def get_status_updates(self) -> Iterator[str]:
        """Generate status updates for general chat."""
        yield "Initializing General AI Agent..."
        yield "Understanding your request..."
        yield "Preparing response..."
