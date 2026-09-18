"""
Chat interface component for aRe_Agent application.
Handles message display and user input.
"""

import streamlit as st
from typing import List, Dict, Any, Optional
from auth.session import SessionManager
from utils.logging import get_logger

logger = get_logger(__name__)


def render_chat_interface():
    """Render the main chat interface."""
    # Display conversation history
    render_message_history()
    
    # Chat input at the bottom
    render_chat_input()


def render_message_history():
    """Render conversation message history."""
    history = SessionManager.get_conversation_history()
    
    if not history:
        render_welcome_message()
        return
    
    # Display messages
    for message in history:
        role = message.get('role', 'user')
        content = message.get('content', '')
        metadata = message.get('metadata', {})
        
        if role == 'user':
            render_user_message(content)
        elif role == 'assistant':
            render_assistant_message(content, metadata)


def render_welcome_message():
    """Render welcome message when no conversation history."""
    current_agent = SessionManager.get_current_agent()
    
    if not current_agent:
        st.info("👈 Please select an agent from the sidebar to begin")
        return
    
    # Get agent-specific welcome message
    welcome_messages = {
        'pdf_research': """
### Welcome to PDF Research Agent

Upload PDF documents and ask questions about their content.

**Capabilities:**
- Upload and analyze PDF documents
- Answer questions with citations
- Summarize documents
- Compare multiple PDFs
- Extract key findings

**How to use:**
1. Upload a PDF document
2. Ask questions about the content
3. Get answers with page references
        """,
        'horoscope': """
### Welcome to Horoscope Research Agent

Get personalized horoscope insights based on real-time research.

**Capabilities:**
- Daily, weekly, and monthly horoscopes
- Personalized readings based on birth date
- Research from 20-30 sources
- Planetary transit information

**How to use:**
1. Provide your birth date or zodiac sign
2. Choose the horoscope period
3. Receive researched insights
        """,
        'general_chat': """
### Welcome to General AI Agent

Your versatile AI assistant for various tasks.

**Capabilities:**
- Natural conversations
- Code generation and debugging
- Writing assistance
- Technical explanations
- Problem-solving

**How to use:**
Simply ask any question or describe what you need help with!
        """,
        'history_geopolitics': """
### Welcome to History & Geopolitics Agent

Research-oriented agent for historical and geopolitical queries.

**Capabilities:**
- Historical research and analysis
- Geopolitical insights
- International relations
- War and conflict history
- Current events context

**How to use:**
Ask about historical events, geopolitical situations, or current affairs!
        """
    }
    
    message = welcome_messages.get(current_agent, "Welcome! How can I assist you today?")
    st.markdown(message)


def render_user_message(content: str):
    """Render a user message."""
    with st.chat_message("user"):
        st.markdown(content)


def render_assistant_message(content: str, metadata: Optional[Dict[str, Any]] = None):
    """Render an assistant message."""
    with st.chat_message("assistant"):
        st.markdown(content)
        
        # Display metadata if available
        if metadata and metadata.get('sources'):
            with st.expander("View Sources"):
                sources = metadata['sources']
                for i, source in enumerate(sources, 1):
                    st.caption(f"{i}. {source}")


def render_chat_input():
    """Render chat input field."""
    current_agent = SessionManager.get_current_agent()
    
    if not current_agent:
        st.info("Please select an agent to start chatting")
        return
    
    # Placeholder text based on agent
    placeholders = {
        'pdf_research': "Ask a question about your uploaded documents...",
        'horoscope': "Ask about your horoscope...",
        'general_chat': "Ask me anything...",
        'history_geopolitics': "Ask about history or geopolitics..."
    }
    
    placeholder = placeholders.get(current_agent, "Type your message...")
    
    # Chat input
    if prompt := st.chat_input(placeholder):
        # Add user message to history
        SessionManager.add_message_to_history('user', prompt)
        
        # Trigger rerun to process message
        st.rerun()


def display_streaming_message(message_placeholder, status_placeholder=None):
    """
    Display a streaming message.
    
    Args:
        message_placeholder: Streamlit placeholder for message content
        status_placeholder: Optional placeholder for status updates
        
    Returns:
        Generator for streaming chunks
    """
    full_response = ""
    
    def update_stream(chunk: str):
        nonlocal full_response
        full_response += chunk
        message_placeholder.markdown(full_response + "▌")
    
    return update_stream, lambda: message_placeholder.markdown(full_response)


def render_agent_specific_inputs():
    """Render agent-specific input fields."""
    current_agent = SessionManager.get_current_agent()
    
    if current_agent == 'pdf_research':
        render_pdf_upload()
    elif current_agent == 'horoscope':
        render_horoscope_inputs()


def render_pdf_upload():
    """Render PDF upload interface."""
    st.markdown("### Upload PDF Document")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF document to analyze"
    )
    
    if uploaded_file:
        if st.button("Process PDF"):
            return uploaded_file
    
    return None


def render_horoscope_inputs():
    """Render horoscope-specific inputs."""
    with st.expander("Horoscope Settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            birth_date = st.date_input("Birth Date (Optional)")
        
        with col2:
            zodiac_signs = [
                "Aries", "Taurus", "Gemini", "Cancer",
                "Leo", "Virgo", "Libra", "Scorpio",
                "Sagittarius", "Capricorn", "Aquarius", "Pisces"
            ]
            zodiac_sign = st.selectbox("Or Select Zodiac Sign", [""] + zodiac_signs)
        
        period = st.radio(
            "Horoscope Period",
            ["Daily", "Weekly", "Monthly"],
            horizontal=True
        )
        
        return {
            'birth_date': str(birth_date) if birth_date else None,
            'zodiac_sign': zodiac_sign if zodiac_sign else None,
            'period': period.lower()
        }
    
    return {}
