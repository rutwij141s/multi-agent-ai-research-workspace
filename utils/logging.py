"""
Logging configuration for aRe_Agent application.
Provides structured logging with file and console handlers.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from utils.config import config


class LoggerSetup:
    """Configure and manage application logging."""
    
    _loggers = {}
    _initialized = False
    
    @classmethod
    def setup(cls, name: str = "are_agent") -> logging.Logger:
        """
        Set up and return a logger instance.
        
        Args:
            name: Logger name
            
        Returns:
            Configured logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # Set level from config
        log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(log_level)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
        
        # File handler
        try:
            log_file = Path(config.LOG_FILE)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Failed to set up file logging: {e}")
        
        # Prevent propagation to root logger
        logger.propagate = False
        
        cls._loggers[name] = logger
        cls._initialized = True
        
        return logger
    
    @classmethod
    def get_logger(cls, name: str = "are_agent") -> logging.Logger:
        """
        Get or create a logger instance.
        
        Args:
            name: Logger name
            
        Returns:
            Logger instance
        """
        if name not in cls._loggers:
            return cls.setup(name)
        return cls._loggers[name]


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Convenience function to get a logger.
    
    Args:
        name: Optional logger name. If None, uses module name.
        
    Returns:
        Logger instance
    """
    if name is None:
        # Get the caller's module name
        import inspect
        frame = inspect.currentframe()
        if frame and frame.f_back:
            caller_module = frame.f_back.f_globals.get('__name__', 'are_agent')
            name = caller_module
        else:
            name = 'are_agent'
    
    return LoggerSetup.get_logger(name)


# Initialize default logger
default_logger = LoggerSetup.setup()
