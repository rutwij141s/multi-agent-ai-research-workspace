"""
OpenAI API service for aRe_Agent application.
Handles interactions with OpenAI API for chat completions.
"""

from typing import Iterator, Optional, List, Dict, Any, Union
from openai import OpenAI
from openai import OpenAIError

from utils.config import config
from utils.logging import get_logger

logger = get_logger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI API."""
    
    def __init__(self):
        """Initialize OpenAI service."""
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL
        logger.info(f"OpenAI service initialized with model: {self.model}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Union[str, Iterator[str]]:
        """
        Generate chat completion.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Completion text or iterator of text chunks if streaming
            
        Raises:
            OpenAIError: If API call fails
        """
        try:
            logger.debug(f"Requesting chat completion (stream={stream})")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                return self._stream_response(response)
            else:
                content = response.choices[0].message.content
                logger.debug(f"Received completion: {len(content)} characters")
                return content
                
        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in chat completion: {e}")
            raise
    
    def _stream_response(self, response) -> Iterator[str]:
        """
        Stream response chunks.
        
        Args:
            response: OpenAI streaming response
            
        Yields:
            Text chunks
        """
        try:
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Error streaming response: {e}")
            yield f"\n\n[Error: {str(e)}]"
    
    def chat_completion_with_system(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Union[str, Iterator[str]]:
        """
        Generate chat completion with system prompt.
        
        Args:
            system_prompt: System prompt to set behavior
            user_message: User's message
            conversation_history: Optional previous messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Completion text or iterator of text chunks
        """
        messages = [{"role": "system", "content": system_prompt}]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": user_message})
        
        return self.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Approximate token count
        """
        # Rough estimation: ~4 characters per token
        return len(text) // 4
    
    def validate_api_key(self) -> bool:
        """
        Validate that the API key works.
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            # Make a minimal API call to test the key
            self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            logger.info("API key validation successful")
            return True
        except OpenAIError as e:
            logger.error(f"API key validation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during API key validation: {e}")
            return False


# Singleton instance
_openai_service = None


def get_openai_service() -> OpenAIService:
    """Get or create OpenAI service instance."""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service
