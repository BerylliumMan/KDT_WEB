"""
Agent manager for handling agent communication and coordination.
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid

from .models import AgentInfo, AgentStatus, AgentCommand, AgentCommandRequest, AgentCommandResponse
from app import crud, models

logger = logging.getLogger(__name__)

class AgentManager:
    """Manages registered agents and their communication."""
    
    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
        self.agent_connections: Dict[str, asyncio.Queue] = {}
        self.command_queues: Dict[str, asyncio.Queue] = {}
        
    def register_agent(self, agent_info: AgentInfo) -> str:
        """Register a new agent."""
        agent_id = str(uuid.uuid4())
        agent_info.id = agent_id
        agent_info.created_at = datetime.now()
        agent_info.last_seen = datetime.now()
        agent_info.status = AgentStatus.ONLINE
        
        self.agents[agent_id] = agent_info
        self.agent_connections[agent_id] = asyncio.Queue()
        self.command_queues[agent_id] = asyncio.Queue()
        
        logger.info(f"Registered new agent: {agent_info.name} ({agent_id})")
        return agent_id
        
    def unregister_agent(self, agent_id: str):
        """Unregister an agent."""
        if agent_id in self.agents:
            del self.agents[agent_id]
        if agent_id in self.agent_connections:
            del self.agent_connections[agent_id]
        if agent_id in self.command_queues:
            del self.command_queues[agent_id]
            
        logger.info(f"Unregistered agent: {agent_id}")
        
    def update_agent_status(self, agent_id: str, status: AgentStatus):
        """Update agent status."""
        if agent_id in self.agents:
            self.agents[agent_id].status = status
            self.agents[agent_id].last_seen = datetime.now()
            
    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent information."""
        return self.agents.get(agent_id)
        
    def get_all_agents(self) -> List[AgentInfo]:
        """Get all registered agents."""
        return list(self.agents.values())
        
    def get_available_agents(self) -> List[AgentInfo]:
        """Get all available (online and not busy) agents."""
        return [
            agent for agent in self.agents.values() 
            if agent.status == AgentStatus.ONLINE
        ]
        
    async def send_command(self, agent_id: str, command: AgentCommandRequest) -> AgentCommandResponse:
        """Send a command to an agent."""
        if agent_id not in self.command_queues:
            return AgentCommandResponse(
                success=False,
                message="Agent not found or not connected",
                error="Agent not found"
            )
            
        # Update agent status to busy if it's a execution command
        if command.command in [AgentCommand.RUN_TEST_CASE, AgentCommand.RUN_MODULE, AgentCommand.RUN_PROJECT]:
            self.update_agent_status(agent_id, AgentStatus.BUSY)
            
        try:
            # Send command to agent
            await self.command_queues[agent_id].put(command)
            
            # Wait for response with timeout
            try:
                response = await asyncio.wait_for(
                    self.agent_connections[agent_id].get(), 
                    timeout=command.timeout
                )
                return response
            except asyncio.TimeoutError:
                self.update_agent_status(agent_id, AgentStatus.ERROR)
                return AgentCommandResponse(
                    success=False,
                    message="Command timeout",
                    error="Timeout waiting for agent response"
                )
                
        except Exception as e:
            logger.error(f"Error sending command to agent {agent_id}: {e}")
            self.update_agent_status(agent_id, AgentStatus.ERROR)
            return AgentCommandResponse(
                success=False,
                message="Failed to send command",
                error=str(e)
            )
        finally:
            # Reset agent status to online after command execution
            if command.command in [AgentCommand.RUN_TEST_CASE, AgentCommand.RUN_MODULE, AgentCommand.RUN_PROJECT]:
                self.update_agent_status(agent_id, AgentStatus.ONLINE)
                
    async def handle_agent_response(self, agent_id: str, response: AgentCommandResponse):
        """Handle response from an agent."""
        if agent_id in self.agent_connections:
            await self.agent_connections[agent_id].put(response)
            
    def cleanup_inactive_agents(self, threshold_minutes: int = 5):
        """Remove agents that haven't been seen for a while."""
        cutoff_time = datetime.now() - timedelta(minutes=threshold_minutes)
        inactive_agents = [
            agent_id for agent_id, agent in self.agents.items()
            if agent.last_seen < cutoff_time
        ]
        
        for agent_id in inactive_agents:
            self.unregister_agent(agent_id)
            logger.info(f"Removed inactive agent: {agent_id}")

# Global agent manager instance
agent_manager = AgentManager()