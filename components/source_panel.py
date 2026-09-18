"""
Source panel component for aRe_Agent application.
Displays research sources and citations.
"""

import streamlit as st
from typing import List, Dict, Any
from utils.logging import get_logger

logger = get_logger(__name__)


def render_source_panel(sources: List[Dict[str, Any]], title: str = "Sources"):
    """
    Render a panel displaying research sources.
    
    Args:
        sources: List of source dictionaries
        title: Panel title
    """
    if not sources:
        return
    
    with st.expander(f"📚 {title} ({len(sources)})"):
        render_source_list(sources)


def render_source_list(sources: List[Dict[str, Any]]):
    """
    Render list of sources.
    
    Args:
        sources: List of source dictionaries
    """
    for i, source in enumerate(sources, 1):
        render_single_source(i, source)


def render_single_source(index: int, source: Dict[str, Any]):
    """
    Render a single source.
    
    Args:
        index: Source number
        source: Source dictionary
    """
    title = source.get('title', 'Unknown Source')
    url = source.get('url', '')
    domain = source.get('domain', '')
    snippet = source.get('snippet', '')
    
    # Source header
    if url:
        st.markdown(f"**{index}. [{title}]({url})**")
    else:
        st.markdown(f"**{index}. {title}**")
    
    # Domain
    if domain:
        st.caption(f"Source: {domain}")
    
    # Snippet
    if snippet:
        with st.container():
            st.text(snippet[:200] + "..." if len(snippet) > 200 else snippet)
    
    st.markdown("---")


def render_pdf_citations(citations: List[Dict[str, Any]]):
    """
    Render PDF document citations.
    
    Args:
        citations: List of citation dictionaries with filename, page, text
    """
    if not citations:
        return
    
    with st.expander(f"📄 Document Citations ({len(citations)})"):
        for i, citation in enumerate(citations, 1):
            filename = citation.get('filename', 'Unknown Document')
            page = citation.get('page', 'Unknown')
            text = citation.get('text', '')
            
            st.markdown(f"**Citation {i}**")
            st.caption(f"Document: {filename} | Page: {page}")
            
            if text:
                with st.container():
                    st.text(text[:200] + "..." if len(text) > 200 else text)
            
            st.markdown("---")


def render_source_summary(source_count: int, research_type: str = "web"):
    """
    Render a summary of sources used.
    
    Args:
        source_count: Number of sources
        research_type: Type of research (web, pdf, etc.)
    """
    if source_count > 0:
        icon = "🌐" if research_type == "web" else "📄"
        st.info(f"{icon} This response is based on research from {source_count} {research_type} sources.")


def render_research_metadata(metadata: Dict[str, Any]):
    """
    Render research metadata.
    
    Args:
        metadata: Research metadata dictionary
    """
    with st.expander("Research Details"):
        if 'queries_used' in metadata:
            st.markdown("**Search Queries Used:**")
            for query in metadata['queries_used']:
                st.caption(f"• {query}")
        
        if 'source_count' in metadata:
            st.caption(f"Total sources: {metadata['source_count']}")
        
        if 'timestamp' in metadata:
            st.caption(f"Retrieved: {metadata['timestamp']}")


def render_empty_sources_message():
    """Render message when no sources are available."""
    st.info("No sources were used for this response. The answer is based on general knowledge.")
