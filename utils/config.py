"""
Configuration management for aRe_Agent application.
Loads environment variables and provides centralized configuration access.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Central configuration class for the application."""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    STATIC_DIR = BASE_DIR / "static"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    OPENAI_TTS_MODEL: str = os.getenv("OPENAI_TTS_MODEL", "tts-1")
    OPENAI_TTS_VOICE: str = os.getenv("OPENAI_TTS_VOICE", "alloy")
    
    # ChromaDB Configuration
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./data/chromadb")
    CHROMA_COLLECTION_PREFIX: str = os.getenv("CHROMA_COLLECTION_PREFIX", "are_agent")
    
    # Application Configuration
    APP_NAME: str = os.getenv("APP_NAME", "aRe_Agent")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret_key_change_in_production")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    ALLOWED_FILE_TYPES: str = os.getenv("ALLOWED_FILE_TYPES", "pdf")
    
    # Research Configuration
    MAX_RESEARCH_SOURCES: int = int(os.getenv("MAX_RESEARCH_SOURCES", "30"))
    RESEARCH_TIMEOUT_SECONDS: int = int(os.getenv("RESEARCH_TIMEOUT_SECONDS", "60"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "./logs/app.log")
    
    @classmethod
    def validate(cls) -> tuple[bool, Optional[str]]:
        """
        Validate required configuration values.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not cls.OPENAI_API_KEY or cls.OPENAI_API_KEY == "your_openai_api_key_here":
            return False, "OPENAI_API_KEY is not set. Please configure it in .env file."
        
        if not cls.SECRET_KEY or cls.SECRET_KEY == "your_secret_key_for_session_management":
            return False, "SECRET_KEY is not set. Please configure it in .env file."
        
        # Create necessary directories
        try:
            cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
            cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
            Path(cls.CHROMA_DB_PATH).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return False, f"Failed to create necessary directories: {str(e)}"
        
        return True, None
    
    @classmethod
    def get_allowed_file_types(cls) -> list[str]:
        """Get list of allowed file types."""
        return [ft.strip() for ft in cls.ALLOWED_FILE_TYPES.split(",")]
    
    @classmethod
    def get_max_file_size_bytes(cls) -> int:
        """Get maximum file size in bytes."""
        return cls.MAX_FILE_SIZE_MB * 1024 * 1024
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development mode."""
        return cls.APP_ENV.lower() == "development"
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode."""
        return cls.APP_ENV.lower() == "production"


# Create a singleton instance
config = Config()
