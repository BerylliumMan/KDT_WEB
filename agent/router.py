"""
Agent router for managing remote test execution agents.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
import logging

from .models import AgentInfo, AgentRegistration, AgentCommandRequest, AgentCommandResponse, TestCaseExecutionRequest
from .manager import agent_manager
from app import crud

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/agents",
    tags=["Agents"],
)

# Store pending commands for agents
agent_commands: Dict[str, List[AgentCommandRequest]] = {}

@router.post("/register", response_model=str)
async def register_agent(agent_info: AgentRegistration):
    """
    Register a new agent.
    """
    from .manager import AgentInfo, AgentStatus
    from datetime import datetime
    
    full_agent_info = AgentInfo(
        id="",  # Will be assigned by manager
        name=agent_info.name,
        hostname=agent_info.hostname,
        ip_address=agent_info.ip_address,
        status=AgentStatus.ONLINE,
        last_seen=datetime.now(),
        capabilities=agent_info.capabilities,
        created_at=datetime.now()
    )
    
    agent_id = agent_manager.register_agent(full_agent_info)
    agent_commands[agent_id] = []
    return agent_id

@router.post("/{agent_id}/unregister")
async def unregister_agent(agent_id: str):
    """
    Unregister an agent.
    """
    agent_manager.unregister_agent(agent_id)
    if agent_id in agent_commands:
        del agent_commands[agent_id]
    return {"message": f"Agent {agent_id} unregistered"}

@router.get("/", response_model=List[AgentInfo])
async def list_agents():
    """
    List all registered agents.
    """
    return agent_manager.get_all_agents()

@router.get("/{agent_id}", response_model=AgentInfo)
async def get_agent(agent_id: str):
    """
    Get information about a specific agent.
    """
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.post("/{agent_id}/command", response_model=AgentCommandResponse)
async def send_command_to_agent(agent_id: str, command: AgentCommandRequest):
    """
    Send a command to a specific agent.
    """
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Add command to agent's queue
    if agent_id not in agent_commands:
        agent_commands[agent_id] = []
    agent_commands[agent_id].append(command)
    
    return AgentCommandResponse(
        success=True,
        message=f"Command queued for agent {agent_id}"
    )

@router.get("/{agent_id}/commands")
async def get_agent_commands(agent_id: str):
    """
    Get pending commands for an agent (for polling).
    """
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update last seen time
    agent_manager.update_agent_status(agent_id, agent.status)
    
    # Return and clear pending commands
    if agent_id in agent_commands and agent_commands[agent_id]:
        command = agent_commands[agent_id].pop(0)  # FIFO
        return command.dict()
    
    return {}

@router.post("/{agent_id}/run/testcase/{case_id}", response_model=AgentCommandResponse)
async def run_test_case_on_agent(agent_id: str, case_id: int):
    """
    Run a specific test case on a remote agent.
    """
    # Get test case and project information
    case_data = crud.get_test_case(case_id)
    if not case_data:
        raise HTTPException(status_code=404, detail="Test case not found")
        
    project_data = crud.get_project(case_data['project_id'])
    if not project_data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Prepare execution request
    execution_request = TestCaseExecutionRequest(
        case_id=case_id,
        project_config={
            "id": project_data.id,
            "name": project_data.name,
            "base_url": project_data.base_url,
            "browser": project_data.browser,
            "headless": project_data.headless
        }
    )
    
    # Send command to agent
    from .models import AgentCommandRequest, AgentCommand
    command = AgentCommandRequest(
        command=AgentCommand.RUN_TEST_CASE,
        payload=execution_request.dict()
    )
    
    # Add command to agent's queue
    if agent_id not in agent_commands:
        agent_commands[agent_id] = []
    agent_commands[agent_id].append(command)
    
    return AgentCommandResponse(
        success=True,
        message=f"Test case {case_id} queued for execution on agent {agent_id}"
    )

@router.get("/available", response_model=List[AgentInfo])
async def list_available_agents():
    """
    List all available agents (online and not busy).
    """
    return agent_manager.get_available_agents()