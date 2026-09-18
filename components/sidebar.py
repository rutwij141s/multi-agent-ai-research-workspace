"""
Sidebar component for aRe_Agent application.
Displays navigation, agent selection, and user information.
"""

import streamlit as st
from auth.session import SessionManager
from agents.agent_router import get_agent_router
from utils.logging import get_logger

logger = get_logger(__name__)


def render_sidebar():
    """Render the application sidebar."""
    with st.sidebar:
        # App header
        st.markdown("# aRe_Agent")
        st.markdown("---")
        
        # User info section
        if SessionManager.is_logged_in():
            username = SessionManager.get_username()
            st.markdown(f"**Welcome, {username}**")
            
            # Logout button
            if st.button("Logout", use_container_width=True):
                SessionManager.logout_user()
                st.rerun()
            
            st.markdown("---")
            
            # Agent selection
            render_agent_selector()
            
            st.markdown("---")
            
            # Actions
            render_sidebar_actions()
            
        else:
            st.info("Please log in to access aRe_Agent")


def render_agent_selector():
    """Render agent selection interface."""
    st.markdown("### Select Agent")
    
    router = get_agent_router()
    agents = router.list_agents()
    
    if not agents:
        st.warning("No agents available")
        return
    
    current_agent = SessionManager.get_current_agent()
    
    # Create agent selection options
    agent_options = {agent['name']: agent['agent_type'] for agent in agents}
    agent_names = list(agent_options.keys())
    
    # Find current selection index
    current_index = 0
    if current_agent:
        for i, agent_type in enumerate(agent_options.values()):
            if agent_type == current_agent:
                current_index = i
                break
    
    # Agent selector
    selected_name = st.selectbox(
        "Choose an agent:",
        agent_names,
        index=current_index,
        key="agent_selector"
    )
    
    selected_type = agent_options[selected_name]
    
    # Update session if changed
    if selected_type != current_agent:
        SessionManager.set_current_agent(selected_type)
        st.rerun()
    
    # Display agent description
    selected_agent_info = next(
        (agent for agent in agents if agent['agent_type'] == selected_type),
        None
    )
    
    if selected_agent_info:
        st.caption(selected_agent_info['description'])


def render_sidebar_actions():
    """Render sidebar action buttons."""
    st.markdown("### Actions")
    
    # New conversation
    if st.button("New Conversation", use_container_width=True):
        SessionManager.start_new_conversation()
        st.success("Started new conversation")
        st.rerun()
    
    # Clear history
    if st.button("Clear History", use_container_width=True):
        SessionManager.clear_conversation_history()
        st.success("History cleared")
        st.rerun()
    
    # Show conversation info
    current_agent = SessionManager.get_current_agent()
    history = SessionManager.get_conversation_history()
    
    if current_agent and history:
        st.caption(f"Messages: {len(history)}")
    
    # PDF Agent specific actions
    if current_agent == "pdf_research":
        render_pdf_actions()


def render_pdf_actions():
    """Render PDF-specific sidebar actions."""
    st.markdown("---")
    st.markdown("### PDF Documents")
    
    uploaded_docs = SessionManager.get_uploaded_documents()
    
    if uploaded_docs:
        st.caption(f"{len(uploaded_docs)} document(s) uploaded")
        
        # List documents
        for doc in uploaded_docs:
            filename = doc.get('filename', 'Unknown')
            st.caption(f"• {filename}")
    else:
        st.caption("No documents uploaded yet")


def render_login_sidebar():
    """Render sidebar for non-logged-in users."""
    with st.sidebar:
        st.markdown("# aRe_Agent")
        st.markdown("---")
        st.info("Please log in or sign up to access the application")
