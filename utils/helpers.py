"""
Helper utilities for aRe_Agent application.
Common functions used across the application.
"""

import hashlib
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, Any
import streamlit as st

from utils.config import config
from utils.logging import get_logger

logger = get_logger(__name__)


def generate_id() -> str:
    """
    Generate a unique ID.
    
    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def generate_short_id(length: int = 8) -> str:
    """
    Generate a short unique ID.
    
    Args:
        length: Length of the ID
        
    Returns:
        Short ID string
    """
    return uuid.uuid4().hex[:length]


def hash_text(text: str) -> str:
    """
    Generate SHA256 hash of text.
    
    Args:
        text: Text to hash
        
    Returns:
        Hex digest of the hash
    """
    return hashlib.sha256(text.encode()).hexdigest()


def hash_file(file_path: Union[str, Path]) -> str:
    """
    Generate SHA256 hash of a file.
    
    Args:
        file_path: Path to file
        
    Returns:
        Hex digest of the file hash
    """
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove dangerous characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path separators and dangerous characters
    filename = re.sub(r'[\/\\:*?"<>|]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    # Ensure filename is not empty
    if not filename:
        filename = f"file_{generate_short_id()}"
    
    return filename


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def validate_file_upload(uploaded_file: Any) -> tuple[bool, Optional[str]]:
    """
    Validate uploaded file.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if uploaded_file is None:
        return False, "No file uploaded"
    
    # Check file size
    file_size = uploaded_file.size
    max_size = config.get_max_file_size_bytes()
    
    if file_size > max_size:
        return False, f"File size ({format_file_size(file_size)}) exceeds maximum allowed size ({format_file_size(max_size)})"
    
    # Check file type
    file_extension = Path(uploaded_file.name).suffix.lower().lstrip('.')
    allowed_types = config.get_allowed_file_types()
    
    if file_extension not in allowed_types:
        return False, f"File type '.{file_extension}' is not allowed. Allowed types: {', '.join(allowed_types)}"
    
    return True, None


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_timestamp(dt: Optional[datetime] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime as string.
    
    Args:
        dt: Datetime object. If None, uses current time.
        format_str: Format string
        
    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(format_str)


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse date string into datetime object.
    
    Args:
        date_str: Date string
        
    Returns:
        Datetime object or None if parsing fails
    """
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m-%d-%Y",
        "%m/%d/%Y",
        "%Y-%m-%d %H:%M:%S",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk in characters
        overlap: Overlap between chunks in characters
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < text_length:
            # Look for sentence endings
            sentence_end = max(
                text.rfind('. ', start, end),
                text.rfind('! ', start, end),
                text.rfind('? ', start, end),
                text.rfind('\n', start, end)
            )
            
            if sentence_end > start:
                end = sentence_end + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap if end < text_length else text_length
    
    return chunks


def extract_urls(text: str) -> list[str]:
    """
    Extract URLs from text.
    
    Args:
        text: Text to search
        
    Returns:
        List of URLs found
    """
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, text)


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    return text.strip()


def safe_get_session_state(key: str, default: Any = None) -> Any:
    """
    Safely get value from Streamlit session state.
    
    Args:
        key: Session state key
        default: Default value if key not found
        
    Returns:
        Session state value or default
    """
    try:
        return st.session_state.get(key, default)
    except Exception:
        return default


def safe_set_session_state(key: str, value: Any) -> bool:
    """
    Safely set value in Streamlit session state.
    
    Args:
        key: Session state key
        value: Value to set
        
    Returns:
        True if successful, False otherwise
    """
    try:
        st.session_state[key] = value
        return True
    except Exception as e:
        logger.error(f"Failed to set session state for key '{key}': {e}")
        return False


def format_sources(sources: list[dict]) -> str:
    """
    Format list of sources for display.
    
    Args:
        sources: List of source dictionaries
        
    Returns:
        Formatted sources string
    """
    if not sources:
        return "No sources available"
    
    formatted = []
    for i, source in enumerate(sources, 1):
        title = source.get('title', 'Unknown')
        url = source.get('url', '')
        domain = source.get('domain', '')
        
        if url:
            formatted.append(f"{i}. [{title}]({url})")
        else:
            formatted.append(f"{i}. {title} ({domain})")
    
    return '\n'.join(formatted)
