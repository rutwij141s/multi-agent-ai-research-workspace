"""
Main Streamlit application for aRe_Agent.
Multi-agent AI research workspace.
"""

import streamlit as st
import time
from typing import Optional

from auth.session import SessionManager
from auth.authentication import get_auth_service
from agents.agent_router import get_agent_router, initialize_agents
from components import (
    render_sidebar,
    render_login_sidebar,
    render_chat_interface,
    render_agent_cards,
    render_export_buttons,
    StatusPanel
)
from utils.config import config
from utils.logging import get_logger

logger = get_logger(__name__)


def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(
        page_title=config.APP_NAME,
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Validate configuration
    is_valid, error = config.validate()
    if not is_valid:
        st.error(f"Configuration Error: {error}")
        st.stop()
    
    # Initialize session
    SessionManager.initialize_session()
    
    # Show opening animation on first load
    if 'animation_shown' not in st.session_state:
        show_opening_animation()
        st.session_state['animation_shown'] = True
    
    # Initialize agents
    if 'agents_initialized' not in st.session_state:
        try:
            initialize_agents()
            st.session_state['agents_initialized'] = True
        except Exception as e:
            st.error(f"Failed to initialize agents: {e}")
            logger.error(f"Agent initialization failed: {e}")
            st.stop()
    
    # Route to appropriate page
    if SessionManager.is_logged_in():
        show_main_application()
    else:
        show_authentication_page()


def show_opening_animation():
    """Display opening animation with typing effect."""
    placeholder = st.empty()
    
    app_name = "aRe_Agent"
    displayed_text = ""
    
    with placeholder.container():
        st.markdown("<div style='text-align: center; padding: 200px 0;'>", unsafe_allow_html=True)
        text_placeholder = st.empty()
        
        # Typing effect
        for char in app_name:
            displayed_text += char
            text_placeholder.markdown(
                f"<h1 style='font-family: \"Berkshire Swash\", cursive; font-size: 4rem;'>{displayed_text}</h1>",
                unsafe_allow_html=True
            )
            time.sleep(0.15)
        
        time.sleep(0.5)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Clear animation
    time.sleep(0.3)
    placeholder.empty()


def show_authentication_page():
    """Display authentication page (login/signup)."""
    render_login_sidebar()
    
    st.markdown("<h1 style='text-align: center; font-family: \"Berkshire Swash\", cursive;'>aRe_Agent</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem;'>Multi-Agent AI Research Workspace</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Authentication tabs
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        show_login_form()
    
    with tab2:
        show_signup_form()


def show_login_form():
    """Display login form."""
    st.markdown("### Login to Your Account")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                auth_service = get_auth_service()
                success, error, user_data = auth_service.login(username, password)
                
                if success:
                    SessionManager.login_user(user_data)
                    st.success("Login successful!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error(error or "Login failed")


def show_signup_form():
    """Display signup form."""
    st.markdown("### Create New Account")
    
    with st.form("signup_form"):
        username = st.text_input("Username")
        email = st.text_input("Email (Optional)")
        password = st.text_input("Password", type="password")
        password_confirm = st.text_input("Confirm Password", type="password")
        
        st.caption("Password requirements: At least 6 characters, including uppercase, lowercase, and digit")
        
        submit = st.form_submit_button("Sign Up", use_container_width=True)
        
        if submit:
            if not username or not password:
                st.error("Username and password are required")
            elif password != password_confirm:
                st.error("Passwords do not match")
            else:
                auth_service = get_auth_service()
                success, error, user_id = auth_service.signup(
                    username=username,
                    password=password,
                    email=email if email else None
                )
                
                if success:
                    st.success("Account created successfully! Please log in.")
                else:
                    st.error(error or "Signup failed")


def show_main_application():
    """Display main application interface."""
    render_sidebar()
    
    current_agent = SessionManager.get_current_agent()
    
    if not current_agent:
        show_agent_selection_page()
    else:
        show_chat_page()


def show_agent_selection_page():
    """Display agent selection page."""
    st.markdown("<h1 style='text-align: center; font-family: \"Berkshire Swash\", cursive;'>aRe_Agent</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    render_agent_cards()


def show_chat_page():
    """Display chat interface page."""
    current_agent = SessionManager.get_current_agent()
    router = get_agent_router()
    agent = router.get_agent(current_agent)
    
    if not agent:
        st.error(f"Agent '{current_agent}' not found")
        return
    
    # Page header
    st.markdown(f"## {agent.name}")
    st.caption(agent.description)
    st.markdown("---")
    
    # Agent-specific UI elements
    if current_agent == "pdf_research":
        show_pdf_upload_section(agent)
    elif current_agent == "horoscope":
        horoscope_params = show_horoscope_settings()
        st.session_state['horoscope_params'] = horoscope_params
    
    # Chat interface
    render_chat_interface()
    
    # Process new user message
    history = SessionManager.get_conversation_history()
    if history and history[-1]['role'] == 'user':
        process_user_message(agent, history[-1]['content'])


def show_pdf_upload_section(agent):
    """Show PDF upload section."""
    with st.expander("📄 Upload PDF Document", expanded=False):
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload a PDF document to analyze"
        )
        
        if uploaded_file:
            if st.button("Process PDF", type="primary"):
                with st.spinner("Processing PDF..."):
                    user_id = SessionManager.get_user_id()
                    
                    success, error, doc_id = agent.process_pdf_upload(
                        pdf_file=uploaded_file,
                        filename=uploaded_file.name,
                        user_id=user_id
                    )
                    
                    if success:
                        st.success(f"Successfully processed: {uploaded_file.name}")
                        SessionManager.add_uploaded_document(
                            document_id=doc_id,
                            filename=uploaded_file.name
                        )
                    else:
                        st.error(f"Failed to process PDF: {error}")


def show_horoscope_settings():
    """Show horoscope settings."""
    with st.expander("⚙️ Horoscope Settings", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            birth_date = st.date_input("Birth Date (Optional)")
        
        with col2:
            zodiac_signs = [
                "", "Aries", "Taurus", "Gemini", "Cancer",
                "Leo", "Virgo", "Libra", "Scorpio",
                "Sagittarius", "Capricorn", "Aquarius", "Pisces"
            ]
            zodiac_sign = st.selectbox("Or Select Zodiac Sign", zodiac_signs)
        
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


def process_user_message(agent, user_message: str):
    """
    Process user message with the current agent.
    
    Args:
        agent: Current agent instance
        user_message: User's message
    """
    try:
        user_id = SessionManager.get_user_id()
        history = SessionManager.get_conversation_history()[:-1]  # Exclude last (current) message
        
        # Prepare kwargs for agent
        kwargs = {}
        
        # Add horoscope parameters if applicable
        if agent.agent_type == "horoscope":
            horoscope_params = st.session_state.get('horoscope_params', {})
            kwargs.update(horoscope_params)
        
        # Display assistant message with streaming
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Stream response
            for chunk in agent.process_message_stream(
                user_message=user_message,
                conversation_history=history,
                user_id=user_id,
                **kwargs
            ):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
            
            # Final response without cursor
            message_placeholder.markdown(full_response)
            
            # Add export buttons
            render_export_buttons(
                content=full_response,
                agent_name=agent.name,
                user_query=user_message
            )
        
        # Add to conversation history
        SessionManager.add_message_to_history('assistant', full_response)
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        st.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        st.error(f"An unexpected error occurred. Please refresh the page or contact support.")
