"""
Status panel component for aRe_Agent application.
Displays processing status and progress indicators.
"""

import streamlit as st
import time
from typing import Iterator, Optional
from utils.logging import get_logger

logger = get_logger(__name__)


class StatusPanel:
    """Manages status display during agent processing."""
    
    def __init__(self):
        """Initialize status panel."""
        self.container = None
        self.status_placeholder = None
        self.progress_bar = None
    
    def create(self) -> 'StatusPanel':
        """
        Create status panel UI elements.
        
        Returns:
            Self for method chaining
        """
        self.container = st.container()
        with self.container:
            self.status_placeholder = st.empty()
            self.progress_bar = st.progress(0)
        return self
    
    def update_status(self, message: str, progress: Optional[float] = None):
        """
        Update status message and progress.
        
        Args:
            message: Status message to display
            progress: Optional progress value (0.0 to 1.0)
        """
        if self.status_placeholder:
            self.status_placeholder.info(f"⚙️ {message}")
        
        if progress is not None and self.progress_bar:
            self.progress_bar.progress(progress)
    
    def show_processing(self, status_iterator: Iterator[str]):
        """
        Show processing status updates.
        
        Args:
            status_iterator: Iterator of status messages
        """
        try:
            statuses = list(status_iterator)
            total_steps = len(statuses)
            
            for i, status in enumerate(statuses):
                progress = (i + 1) / total_steps
                self.update_status(status, progress)
                time.sleep(0.3)  # Brief pause for visibility
                
        except Exception as e:
            logger.error(f"Error displaying status: {e}")
    
    def show_success(self, message: str = "Processing complete"):
        """
        Show success message.
        
        Args:
            message: Success message
        """
        if self.status_placeholder:
            self.status_placeholder.success(f"✅ {message}")
        
        if self.progress_bar:
            self.progress_bar.progress(1.0)
    
    def show_error(self, message: str):
        """
        Show error message.
        
        Args:
            message: Error message
        """
        if self.status_placeholder:
            self.status_placeholder.error(f"❌ {message}")
    
    def clear(self):
        """Clear status panel."""
        if self.status_placeholder:
            self.status_placeholder.empty()
        
        if self.progress_bar:
            self.progress_bar.empty()
    
    def hide(self):
        """Hide the entire status panel."""
        if self.container:
            self.container.empty()


def render_simple_status(message: str, status_type: str = "info"):
    """
    Render a simple status message.
    
    Args:
        message: Status message
        status_type: Type of status (info, success, warning, error)
    """
    if status_type == "info":
        st.info(message)
    elif status_type == "success":
        st.success(message)
    elif status_type == "warning":
        st.warning(message)
    elif status_type == "error":
        st.error(message)


def render_agent_status(agent_name: str, is_processing: bool = False):
    """
    Render current agent status.
    
    Args:
        agent_name: Name of current agent
        is_processing: Whether agent is currently processing
    """
    if is_processing:
        st.info(f"🤖 {agent_name} is processing your request...")
    else:
        st.caption(f"Current Agent: {agent_name}")


def show_spinner_with_status(message: str = "Processing..."):
    """
    Show a spinner with status message.
    
    Args:
        message: Status message
        
    Returns:
        Streamlit spinner context manager
    """
    return st.spinner(message)
