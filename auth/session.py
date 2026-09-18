"""
Session management for aRe_Agent application.
Handles user sessions in Streamlit.
"""

from typing import Optional, Dict, Any
import streamlit as st

from utils.logging import get_logger
from utils.helpers import generate_id

logger = get_logger(__name__)


class SessionManager:
    """Manages user sessions in Streamlit."""
    
    # Session state keys
    USER_ID_KEY = "user_id"
    USERNAME_KEY = "username"
    EMAIL_KEY = "email"
    SESSION_ID_KEY = "session_id"
    LOGGED_IN_KEY = "logged_in"
    CURRENT_AGENT_KEY = "current_agent"
    CONVERSATION_ID_KEY = "conversation_id"
    CONVERSATION_HISTORY_KEY = "conversation_history"
    UPLOADED_DOCUMENTS_KEY = "uploaded_documents"
    
    @staticmethod
    def initialize_session():
        """Initialize session state with default values."""
        if SessionManager.SESSION_ID_KEY not in st.session_state:
            st.session_state[SessionManager.SESSION_ID_KEY] = generate_id()
            logger.info(f"New session initialized: {st.session_state[SessionManager.SESSION_ID_KEY]}")
        
        if SessionManager.LOGGED_IN_KEY not in st.session_state:
            st.session_state[SessionManager.LOGGED_IN_KEY] = False
        
        if SessionManager.CURRENT_AGENT_KEY not in st.session_state:
            st.session_state[SessionManager.CURRENT_AGENT_KEY] = None
        
        if SessionManager.CONVERSATION_HISTORY_KEY not in st.session_state:
            st.session_state[SessionManager.CONVERSATION_HISTORY_KEY] = []
        
        if SessionManager.UPLOADED_DOCUMENTS_KEY not in st.session_state:
            st.session_state[SessionManager.UPLOADED_DOCUMENTS_KEY] = []
    
    @staticmethod
    def login_user(user_data: Dict[str, Any]):
        """
        Log in a user and set session data.
        
        Args:
            user_data: User data dictionary from authentication
        """
        st.session_state[SessionManager.LOGGED_IN_KEY] = True
        st.session_state[SessionManager.USER_ID_KEY] = user_data.get('user_id')
        st.session_state[SessionManager.USERNAME_KEY] = user_data.get('username')
        st.session_state[SessionManager.EMAIL_KEY] = user_data.get('email')
        
        logger.info(f"User logged in: {user_data.get('username')} (ID: {user_data.get('user_id')})")
    
    @staticmethod
    def logout_user():
        """Log out the current user and clear session data."""
        username = st.session_state.get(SessionManager.USERNAME_KEY, "Unknown")
        
        # Clear user-specific data
        st.session_state[SessionManager.LOGGED_IN_KEY] = False
        st.session_state[SessionManager.USER_ID_KEY] = None
        st.session_state[SessionManager.USERNAME_KEY] = None
        st.session_state[SessionManager.EMAIL_KEY] = None
        st.session_state[SessionManager.CURRENT_AGENT_KEY] = None
        st.session_state[SessionManager.CONVERSATION_HISTORY_KEY] = []
        st.session_state[SessionManager.UPLOADED_DOCUMENTS_KEY] = []
        
        if SessionManager.CONVERSATION_ID_KEY in st.session_state:
            st.session_state[SessionManager.CONVERSATION_ID_KEY] = None
        
        logger.info(f"User logged out: {username}")
    
    @staticmethod
    def is_logged_in() -> bool:
        """
        Check if a user is logged in.
        
        Returns:
            True if logged in, False otherwise
        """
        return st.session_state.get(SessionManager.LOGGED_IN_KEY, False)
    
    @staticmethod
    def get_user_id() -> Optional[str]:
        """
        Get current user ID.
        
        Returns:
            User ID or None if not logged in
        """
        return st.session_state.get(SessionManager.USER_ID_KEY)
    
    @staticmethod
    def get_username() -> Optional[str]:
        """
        Get current username.
        
        Returns:
            Username or None if not logged in
        """
        return st.session_state.get(SessionManager.USERNAME_KEY)
    
    @staticmethod
    def get_email() -> Optional[str]:
        """
        Get current user email.
        
        Returns:
            Email or None if not logged in
        """
        return st.session_state.get(SessionManager.EMAIL_KEY)
    
    @staticmethod
    def get_session_id() -> str:
        """
        Get current session ID.
        
        Returns:
            Session ID
        """
        return st.session_state.get(SessionManager.SESSION_ID_KEY, "")
    
    @staticmethod
    def set_current_agent(agent_type: Optional[str]):
        """
        Set the current agent.
        
        Args:
            agent_type: Agent type identifier or None
        """
        st.session_state[SessionManager.CURRENT_AGENT_KEY] = agent_type
        
        # Start new conversation when switching agents
        if agent_type:
            SessionManager.start_new_conversation()
            logger.info(f"Switched to agent: {agent_type}")
    
    @staticmethod
    def get_current_agent() -> Optional[str]:
        """
        Get the current agent type.
        
        Returns:
            Agent type or None
        """
        return st.session_state.get(SessionManager.CURRENT_AGENT_KEY)
    
    @staticmethod
    def start_new_conversation():
        """Start a new conversation."""
        conversation_id = generate_id()
        st.session_state[SessionManager.CONVERSATION_ID_KEY] = conversation_id
        st.session_state[SessionManager.CONVERSATION_HISTORY_KEY] = []
        logger.info(f"Started new conversation: {conversation_id}")
    
    @staticmethod
    def get_conversation_id() -> Optional[str]:
        """
        Get current conversation ID.
        
        Returns:
            Conversation ID or None
        """
        return st.session_state.get(SessionManager.CONVERSATION_ID_KEY)
    
    @staticmethod
    def add_message_to_history(role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add a message to conversation history.
        
        Args:
            role: Message role (user/assistant)
            content: Message content
            metadata: Optional metadata
        """
        if SessionManager.CONVERSATION_HISTORY_KEY not in st.session_state:
            st.session_state[SessionManager.CONVERSATION_HISTORY_KEY] = []
        
        message = {
            'role': role,
            'content': content,
            'metadata': metadata or {}
        }
        
        st.session_state[SessionManager.CONVERSATION_HISTORY_KEY].append(message)
    
    @staticmethod
    def get_conversation_history() -> list[Dict[str, Any]]:
        """
        Get conversation history.
        
        Returns:
            List of message dictionaries
        """
        return st.session_state.get(SessionManager.CONVERSATION_HISTORY_KEY, [])
    
    @staticmethod
    def clear_conversation_history():
        """Clear conversation history."""
        st.session_state[SessionManager.CONVERSATION_HISTORY_KEY] = []
        logger.debug("Conversation history cleared")
    
    @staticmethod
    def add_uploaded_document(document_id: str, filename: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Track an uploaded document.
        
        Args:
            document_id: Document identifier
            filename: Document filename
            metadata: Optional metadata
        """
        if SessionManager.UPLOADED_DOCUMENTS_KEY not in st.session_state:
            st.session_state[SessionManager.UPLOADED_DOCUMENTS_KEY] = []
        
        doc_info = {
            'document_id': document_id,
            'filename': filename,
            'metadata': metadata or {}
        }
        
        st.session_state[SessionManager.UPLOADED_DOCUMENTS_KEY].append(doc_info)
        logger.info(f"Document added to session: {filename}")
    
    @staticmethod
    def get_uploaded_documents() -> list[Dict[str, Any]]:
        """
        Get list of uploaded documents in current session.
        
        Returns:
            List of document info dictionaries
        """
        return st.session_state.get(SessionManager.UPLOADED_DOCUMENTS_KEY, [])
    
    @staticmethod
    def clear_uploaded_documents():
        """Clear uploaded documents list."""
        st.session_state[SessionManager.UPLOADED_DOCUMENTS_KEY] = []
        logger.debug("Uploaded documents cleared")
    
    @staticmethod
    def get_session_info() -> Dict[str, Any]:
        """
        Get comprehensive session information.
        
        Returns:
            Dictionary of session information
        """
        return {
            'session_id': SessionManager.get_session_id(),
            'logged_in': SessionManager.is_logged_in(),
            'user_id': SessionManager.get_user_id(),
            'username': SessionManager.get_username(),
            'email': SessionManager.get_email(),
            'current_agent': SessionManager.get_current_agent(),
            'conversation_id': SessionManager.get_conversation_id(),
            'message_count': len(SessionManager.get_conversation_history()),
            'document_count': len(SessionManager.get_uploaded_documents())
        }
    
    @staticmethod
    def require_login(func):
        """
        Decorator to require login for a function.
        
        Args:
            func: Function to decorate
            
        Returns:
            Decorated function
        """
        def wrapper(*args, **kwargs):
            if not SessionManager.is_logged_in():
                st.warning("Please log in to access this feature.")
                st.stop()
            return func(*args, **kwargs)
        return wrapper
