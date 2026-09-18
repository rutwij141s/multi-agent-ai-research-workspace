"""
Agent selection cards component for aRe_Agent application.
Displays available agents as interactive cards.
"""

import streamlit as st
from agents.agent_router import get_agent_router
from auth.session import SessionManager
from utils.logging import get_logger

logger = get_logger(__name__)


def render_agent_cards():
    """Render agent selection cards."""
    st.markdown("## Select an Agent")
    st.markdown("Choose a specialized AI agent for your task:")
    
    router = get_agent_router()
    agents = router.list_agents()
    
    if not agents:
        st.error("No agents available. Please contact support.")
        return
    
    # Display agents in a grid
    cols = st.columns(2)
    
    for i, agent in enumerate(agents):
        col = cols[i % 2]
        
        with col:
            render_agent_card(agent)


def render_agent_card(agent: dict):
    """
    Render a single agent card.
    
    Args:
        agent: Agent metadata dictionary
    """
    agent_type = agent['agent_type']
    name = agent['name']
    description = agent['description']
    capabilities = agent.get('capabilities', [])
    
    # Agent icons (emoji)
    icons = {
        'pdf_research': '📄',
        'horoscope': '⭐',
        'general_chat': '💬',
        'history_geopolitics': '🌍'
    }
    
    icon = icons.get(agent_type, '🤖')
    
    # Card container
    with st.container():
        st.markdown(f"### {icon} {name}")
        st.markdown(description)
        
        # Show capabilities
        if capabilities:
            with st.expander("View Capabilities"):
                for cap in capabilities[:5]:  # Show first 5
                    st.markdown(f"• {cap}")
        
        # Select button
        if st.button(f"Select {name}", key=f"select_{agent_type}", use_container_width=True):
            SessionManager.set_current_agent(agent_type)
            st.success(f"Selected {name}")
            st.rerun()
        
        st.markdown("---")


def render_compact_agent_selector():
    """Render a compact agent selector dropdown."""
    router = get_agent_router()
    agents = router.list_agents()
    
    if not agents:
        st.warning("No agents available")
        return
    
    current_agent = SessionManager.get_current_agent()
    
    # Create options
    agent_options = {f"{a['name']}": a['agent_type'] for a in agents}
    agent_names = list(agent_options.keys())
    
    # Find current index
    current_index = 0
    if current_agent:
        for i, (name, atype) in enumerate(agent_options.items()):
            if atype == current_agent:
                current_index = i
                break
    
    # Selector
    selected_name = st.selectbox(
        "Agent:",
        agent_names,
        index=current_index,
        key="compact_agent_selector"
    )
    
    selected_type = agent_options[selected_name]
    
    # Update if changed
    if selected_type != current_agent:
        SessionManager.set_current_agent(selected_type)
        st.rerun()
