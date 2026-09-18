"""
Export buttons component for aRe_Agent application.
Provides buttons for copying, downloading, and generating audio.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
from typing import Optional
from services.tts_service import get_tts_service
from utils.logging import get_logger
from utils.helpers import format_timestamp

logger = get_logger(__name__)


def render_export_buttons(
    content: str,
    agent_name: str,
    user_query: Optional[str] = None,
    sources: Optional[list] = None
):
    """
    Render export action buttons for a response.
    
    Args:
        content: Response content to export
        agent_name: Name of the agent that generated the response
        user_query: Optional user query that prompted the response
        sources: Optional list of sources
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_copy_button(content)
    
    with col2:
        render_download_markdown_button(content, agent_name, user_query, sources)
    
    with col3:
        render_generate_audio_button(content, agent_name)
    
    with col4:
        if st.button("🔄 Regenerate", use_container_width=True):
            st.session_state['regenerate_requested'] = True
            st.rerun()


def render_copy_button(content: str):
    """
    Render copy to clipboard button.
    
    Args:
        content: Content to copy
    """
    # Note: Actual clipboard copy requires JavaScript, 
    # so we provide the content in a way that's easy to copy
    if st.button("📋 Copy", use_container_width=True):
        st.session_state['show_copy_modal'] = True
        st.session_state['copy_content'] = content


def render_download_markdown_button(
    content: str,
    agent_name: str,
    user_query: Optional[str] = None,
    sources: Optional[list] = None
):
    """
    Render download as markdown button.
    
    Args:
        content: Response content
        agent_name: Agent name
        user_query: User query
        sources: List of sources
    """
    markdown_content = format_markdown_export(content, agent_name, user_query, sources)
    
    filename = f"are_agent_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    st.download_button(
        label="⬇️ Markdown",
        data=markdown_content,
        file_name=filename,
        mime="text/markdown",
        use_container_width=True
    )


def render_generate_audio_button(content: str, agent_name: str):
    """
    Render generate audio button.
    
    Args:
        content: Content to convert to speech
        agent_name: Agent name for filename
    """
    if st.button("🔊 Audio", use_container_width=True):
        with st.spinner("Generating audio..."):
            try:
                tts_service = get_tts_service()
                
                # Generate audio file
                filename_base = f"{agent_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                audio_path = tts_service.generate_speech(content, filename=filename_base)
                
                # Read audio file
                with open(audio_path, 'rb') as audio_file:
                    audio_bytes = audio_file.read()
                
                # Display audio player
                st.audio(audio_bytes, format='audio/mp3')
                
                # Provide download button
                st.download_button(
                    label="Download Audio",
                    data=audio_bytes,
                    file_name=f"{filename_base}.mp3",
                    mime="audio/mp3"
                )
                
                st.success("Audio generated successfully!")
                
            except Exception as e:
                logger.error(f"Error generating audio: {e}")
                st.error(f"Failed to generate audio: {str(e)}")


def format_markdown_export(
    content: str,
    agent_name: str,
    user_query: Optional[str] = None,
    sources: Optional[list] = None
) -> str:
    """
    Format response as markdown for export.
    
    Args:
        content: Response content
        agent_name: Agent name
        user_query: User query
        sources: List of sources
        
    Returns:
        Formatted markdown string
    """
    parts = []
    
    # Header
    parts.append(f"# aRe_Agent Response\n")
    parts.append(f"**Agent:** {agent_name}\n")
    parts.append(f"**Generated:** {format_timestamp()}\n")
    parts.append("\n---\n")
    
    # User query
    if user_query:
        parts.append(f"\n## User Query\n")
        parts.append(f"{user_query}\n")
        parts.append("\n---\n")
    
    # Response
    parts.append(f"\n## Response\n")
    parts.append(f"{content}\n")
    
    # Sources
    if sources:
        parts.append("\n---\n")
        parts.append(f"\n## Sources ({len(sources)})\n")
        for i, source in enumerate(sources, 1):
            title = source.get('title', 'Unknown')
            url = source.get('url', '')
            domain = source.get('domain', '')
            
            if url:
                parts.append(f"{i}. [{title}]({url})")
            else:
                parts.append(f"{i}. {title}")
            
            if domain:
                parts.append(f" ({domain})")
            
            parts.append("\n")
    
    # Footer
    parts.append("\n---\n")
    parts.append("\n*Generated by aRe_Agent - Multi-Agent AI Research Workspace*\n")
    
    return ''.join(parts)


def show_copy_modal():
    """Show modal for copying content."""
    if st.session_state.get('show_copy_modal'):
        content = st.session_state.get('copy_content', '')
        
        with st.container():
            st.text_area(
                "Copy the text below:",
                value=content,
                height=200,
                key="copy_text_area"
            )
            
            if st.button("Close"):
                st.session_state['show_copy_modal'] = False
                st.rerun()
