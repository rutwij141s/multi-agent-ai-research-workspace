"""
Text-to-Speech service for aRe_Agent application.
Handles audio generation using OpenAI TTS API.
"""

from pathlib import Path
from typing import Optional
from openai import OpenAI
from openai import OpenAIError

from utils.config import config
from utils.logging import get_logger
from utils.helpers import generate_short_id, sanitize_filename

logger = get_logger(__name__)


class TTSService:
    """Service for text-to-speech conversion."""
    
    def __init__(self):
        """Initialize TTS service."""
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_TTS_MODEL
        self.voice = config.OPENAI_TTS_VOICE
        self.output_dir = Path("./data/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"TTS service initialized with model: {self.model}, voice: {self.voice}")
    
    def generate_speech(
        self,
        text: str,
        filename: Optional[str] = None,
        voice: Optional[str] = None
    ) -> Path:
        """
        Generate speech from text.
        
        Args:
            text: Text to convert to speech
            filename: Optional output filename (without extension)
            voice: Optional voice override (alloy, echo, fable, onyx, nova, shimmer)
            
        Returns:
            Path to generated audio file
            
        Raises:
            OpenAIError: If API call fails
        """
        try:
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")
            
            # Limit text length (TTS has limits)
            max_chars = 4096
            if len(text) > max_chars:
                logger.warning(f"Text truncated from {len(text)} to {max_chars} characters")
                text = text[:max_chars]
            
            # Generate filename if not provided
            if filename is None:
                filename = f"speech_{generate_short_id()}"
            else:
                filename = sanitize_filename(filename)
            
            output_path = self.output_dir / f"{filename}.mp3"
            
            # Use provided voice or default
            selected_voice = voice or self.voice
            
            logger.info(f"Generating speech audio: {output_path}")
            
            response = self.client.audio.speech.create(
                model=self.model,
                voice=selected_voice,
                input=text
            )
            
            # Save audio file
            response.stream_to_file(output_path)
            
            logger.info(f"Audio generated successfully: {output_path}")
            return output_path
            
        except OpenAIError as e:
            logger.error(f"OpenAI API error during TTS: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating speech: {e}")
            raise
    
    def get_available_voices(self) -> list[str]:
        """
        Get list of available TTS voices.
        
        Returns:
            List of voice names
        """
        return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    def cleanup_old_audio(self, max_files: int = 100):
        """
        Clean up old audio files to save space.
        
        Args:
            max_files: Maximum number of audio files to keep
        """
        try:
            audio_files = sorted(
                self.output_dir.glob("*.mp3"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            if len(audio_files) > max_files:
                files_to_delete = audio_files[max_files:]
                for file in files_to_delete:
                    file.unlink()
                    logger.debug(f"Deleted old audio file: {file}")
                
                logger.info(f"Cleaned up {len(files_to_delete)} old audio files")
                
        except Exception as e:
            logger.error(f"Error cleaning up audio files: {e}")


# Singleton instance
_tts_service = None


def get_tts_service() -> TTSService:
    """Get or create TTS service instance."""
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service
