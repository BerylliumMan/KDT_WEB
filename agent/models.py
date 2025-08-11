"""
Agent communication protocol models.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class AgentStatus(str, Enum):
    """Agent status enumeration."""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"

class AgentCommand(str, Enum):
    """Agent command enumeration."""
    RUN_TEST_CASE = "run_test_case"
    RUN_MODULE = "run_module"
    RUN_PROJECT = "run_project"
    PING = "ping"
    SHUTDOWN = "shutdown"

class AgentInfo(BaseModel):
    """Information about an agent."""
    id: str
    name: str
    hostname: str
    ip_address: str
    status: AgentStatus
    last_seen: datetime
    capabilities: List[str] = []
    current_task: Optional[str] = None
    created_at: datetime

class AgentRegistration(BaseModel):
    """Agent registration request."""
    name: str
    hostname: str
    ip_address: str
    capabilities: List[str] = []

class AgentCommandRequest(BaseModel):
    """Command sent to an agent."""
    command: AgentCommand
    payload: Dict[str, Any] = {}
    timeout: int = 300  # Default timeout in seconds

class AgentCommandResponse(BaseModel):
    """Response from an agent."""
    success: bool
    message: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class TestCaseExecutionRequest(BaseModel):
    """Request to execute a test case."""
    case_id: int
    project_config: Dict[str, Any]  # Project configuration needed for execution

class ModuleExecutionRequest(BaseModel):
    """Request to execute all test cases in a module."""
    module_id: int
    project_config: Dict[str, Any]  # Project configuration needed for execution

class ProjectExecutionRequest(BaseModel):
    """Request to execute all test cases in a project."""
    project_id: int
    project_config: Dict[str, Any]  # Project configuration needed for execution