"""
Centralized error handling for aRe_Agent application.
Provides consistent error handling and user-friendly messages.
"""

import streamlit as st
from typing import Callable, Any
import functools
from openai import OpenAIError

from utils.logging import get_logger

logger = get_logger(__name__)


class AppError(Exception):
    """Base exception for application errors."""
    pass


class AuthenticationError(AppError):
    """Authentication related errors."""
    pass


class ValidationError(AppError):
    """Validation related errors."""
    pass


class DatabaseError(AppError):
    """Database related errors."""
    pass


class ServiceError(AppError):
    """External service related errors."""
    pass


def handle_errors(user_message: str = "An error occurred. Please try again."):
    """
    Decorator for handling errors in functions.
    
    Args:
        user_message: User-friendly error message
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except OpenAIError as e:
                logger.error(f"OpenAI API error in {func.__name__}: {e}")
                st.error(f"AI Service Error: {str(e)}")
                return None
            except ValidationError as e:
                logger.warning(f"Validation error in {func.__name__}: {e}")
                st.warning(str(e))
                return None
            except AuthenticationError as e:
                logger.warning(f"Authentication error in {func.__name__}: {e}")
                st.error(str(e))
                return None
            except DatabaseError as e:
                logger.error(f"Database error in {func.__name__}: {e}")
                st.error("Database error. Please try again later.")
                return None
            except ServiceError as e:
                logger.error(f"Service error in {func.__name__}: {e}")
                st.error(f"Service error: {str(e)}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
                st.error(user_message)
                return None
        return wrapper
    return decorator


def safe_execute(func: Callable, default_return: Any = None, error_message: str = "Operation failed") -> Any:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        default_return: Default return value on error
        error_message: Error message to log
        
    Returns:
        Function result or default value
    """
    try:
        return func()
    except Exception as e:
        logger.error(f"{error_message}: {e}")
        return default_return


def validate_input(
    value: Any,
    field_name: str,
    required: bool = True,
    min_length: int = None,
    max_length: int = None,
    allowed_types: tuple = None
) -> tuple[bool, str]:
    """
    Validate input value.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        required: Whether the field is required
        min_length: Minimum length for strings/lists
        max_length: Maximum length for strings/lists
        allowed_types: Tuple of allowed types
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required
    if required and (value is None or value == ""):
        return False, f"{field_name} is required"
    
    # Check type
    if allowed_types and value is not None and not isinstance(value, allowed_types):
        return False, f"{field_name} must be of type {allowed_types}"
    
    # Check length for strings and lists
    if hasattr(value, '__len__'):
        length = len(value)
        
        if min_length is not None and length < min_length:
            return False, f"{field_name} must be at least {min_length} characters"
        
        if max_length is not None and length > max_length:
            return False, f"{field_name} must be at most {max_length} characters"
    
    return True, ""


def display_error(error: Exception, context: str = ""):
    """
    Display error in a user-friendly format.
    
    Args:
        error: Exception to display
        context: Additional context about where error occurred
    """
    error_type = type(error).__name__
    error_message = str(error)
    
    logger.error(f"Error{' in ' + context if context else ''}: {error_type} - {error_message}")
    
    if isinstance(error, OpenAIError):
        st.error("⚠️ AI Service Error: Unable to connect to AI service. Please check your API key and try again.")
    elif isinstance(error, ValidationError):
        st.warning(f"⚠️ Validation Error: {error_message}")
    elif isinstance(error, AuthenticationError):
        st.error(f"🔒 Authentication Error: {error_message}")
    elif isinstance(error, DatabaseError):
        st.error("💾 Database Error: Unable to access database. Please try again later.")
    elif isinstance(error, ServiceError):
        st.error(f"🔌 Service Error: {error_message}")
    else:
        st.error(f"❌ An unexpected error occurred. Please try again or contact support.")


def with_error_boundary(component_func: Callable, fallback_message: str = "Component failed to load"):
    """
    Wrap a component function with an error boundary.
    
    Args:
        component_func: Component function to wrap
        fallback_message: Message to display on error
    """
    def wrapper(*args, **kwargs):
        try:
            return component_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Component error in {component_func.__name__}: {e}", exc_info=True)
            st.error(fallback_message)
            return None
    return wrapper


class ErrorRecovery:
    """Handles error recovery strategies."""
    
    @staticmethod
    def retry_with_backoff(
        func: Callable,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0
    ) -> Any:
        """
        Retry a function with exponential backoff.
        
        Args:
            func: Function to retry
            max_retries: Maximum number of retries
            initial_delay: Initial delay in seconds
            backoff_factor: Backoff multiplication factor
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        import time
        
        delay = initial_delay
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= backoff_factor
        
        raise last_exception
    
    @staticmethod
    def fallback_chain(*functions):
        """
        Try functions in sequence until one succeeds.
        
        Args:
            *functions: Functions to try in order
            
        Returns:
            Result from first successful function
            
        Raises:
            Exception if all functions fail
        """
        last_exception = None
        
        for func in functions:
            try:
                return func()
            except Exception as e:
                last_exception = e
                logger.warning(f"Function {func.__name__} failed, trying next: {e}")
        
        raise last_exception or Exception("All fallback functions failed")
