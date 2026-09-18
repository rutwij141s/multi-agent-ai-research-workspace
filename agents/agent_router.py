"""
Agent router for aRe_Agent application.
Manages registration and routing to different agents.
"""

from typing import Optional, Dict, List
from agents.base_agent import BaseAgent
from utils.logging import get_logger

logger = get_logger(__name__)


class AgentRouter:
    """Routes requests to appropriate agents."""
    
    def __init__(self):
        """Initialize agent router."""
        self._agents: Dict[str, BaseAgent] = {}
        logger.info("Agent router initialized")
    
    def register_agent(self, agent: BaseAgent):
        """
        Register an agent.
        
        Args:
            agent: Agent instance to register
        """
        if agent.agent_type in self._agents:
            logger.warning(f"Overwriting existing agent: {agent.agent_type}")
        
        self._agents[agent.agent_type] = agent
        logger.info(f"Registered agent: {agent.name} ({agent.agent_type})")
    
    def unregister_agent(self, agent_type: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            agent_type: Agent type identifier
            
        Returns:
            True if agent was unregistered, False if not found
        """
        if agent_type in self._agents:
            agent = self._agents[agent_type]
            del self._agents[agent_type]
            logger.info(f"Unregistered agent: {agent.name}")
            return True
        else:
            logger.warning(f"Attempted to unregister non-existent agent: {agent_type}")
            return False
    
    def get_agent(self, agent_type: str) -> Optional[BaseAgent]:
        """
        Get agent by type.
        
        Args:
            agent_type: Agent type identifier
            
        Returns:
            Agent instance or None if not found
        """
        agent = self._agents.get(agent_type)
        if not agent:
            logger.warning(f"Agent not found: {agent_type}")
        return agent
    
    def list_agents(self) -> List[Dict[str, any]]:
        """
        List all registered agents.
        
        Returns:
            List of agent metadata dictionaries
        """
        return [agent.get_metadata() for agent in self._agents.values()]
    
    def get_agent_types(self) -> List[str]:
        """
        Get list of registered agent types.
        
        Returns:
            List of agent type identifiers
        """
        return list(self._agents.keys())
    
    def agent_exists(self, agent_type: str) -> bool:
        """
        Check if an agent type is registered.
        
        Args:
            agent_type: Agent type identifier
            
        Returns:
            True if agent exists, False otherwise
        """
        return agent_type in self._agents
    
    def get_agent_count(self) -> int:
        """
        Get number of registered agents.
        
        Returns:
            Number of agents
        """
        return len(self._agents)
    
    def clear_agents(self):
        """Clear all registered agents."""
        count = len(self._agents)
        self._agents.clear()
        logger.info(f"Cleared {count} agents from router")


# Singleton instance
_agent_router = None


def get_agent_router() -> AgentRouter:
    """Get or create agent router instance."""
    global _agent_router
    if _agent_router is None:
        _agent_router = AgentRouter()
    return _agent_router


def initialize_agents():
    """
    Initialize and register all available agents.
    This function should be called at application startup.
    """
    from agents.pdf_research.pdf_agent import PDFResearchAgent
    from agents.horoscope.horoscope_agent import HoroscopeAgent
    from agents.general_chat.chat_agent import GeneralChatAgent
    from agents.history_geopolitics.history_agent import HistoryGeopoliticsAgent
    
    router = get_agent_router()
    
    # Register all agents
    router.register_agent(PDFResearchAgent())
    router.register_agent(HoroscopeAgent())
    router.register_agent(GeneralChatAgent())
    router.register_agent(HistoryGeopoliticsAgent())
    
    logger.info(f"Initialized {router.get_agent_count()} agents")
    
    return router
