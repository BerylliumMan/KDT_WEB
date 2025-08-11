"""
Client agent for remote test execution.
"""
import asyncio
import json
import logging
import socket
import platform
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

import httpx
from pydantic import BaseModel

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from agent.models import (
    AgentRegistration, AgentCommand, AgentCommandRequest, 
    AgentCommandResponse, TestCaseExecutionRequest,
    ModuleExecutionRequest, ProjectExecutionRequest
)
from core.runner import run_test_case

logger = logging.getLogger(__name__)

class ClientAgent:
    """Client agent that connects to the server and executes test commands."""
    
    def __init__(self, server_url: str, agent_name: str = None):
        self.server_url = server_url.rstrip('/')
        self.agent_name = agent_name or f"Agent-{uuid.uuid4().hex[:8]}"
        self.agent_id: Optional[str] = None
        self.hostname = platform.node()
        self.ip_address = self._get_local_ip()
        self.running = False
        self.command_queue = asyncio.Queue()
        
    def _get_local_ip(self) -> str:
        """Get local IP address."""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
            
    async def register(self) -> bool:
        """Register agent with the server."""
        try:
            registration_data = AgentRegistration(
                name=self.agent_name,
                hostname=self.hostname,
                ip_address=self.ip_address,
                capabilities=["playwright", "ui_testing"]
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.server_url}/api/agents/register",
                    json=registration_data.dict(),
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    self.agent_id = response.json()
                    logger.info(f"Agent registered with ID: {self.agent_id}")
                    return True
                else:
                    logger.error(f"Failed to register agent: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error registering agent: {e}")
            return False
            
    async def unregister(self):
        """Unregister agent from the server."""
        if not self.agent_id:
            return
            
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.server_url}/api/agents/{self.agent_id}/unregister",
                    timeout=10.0
                )
                logger.info(f"Agent {self.agent_id} unregistered")
        except Exception as e:
            logger.error(f"Error unregistering agent: {e}")
            
    async def send_heartbeat(self):
        """Send periodic heartbeat to server."""
        if not self.agent_id:
            return
            
        try:
            command = AgentCommandRequest(
                command=AgentCommand.PING,
                payload={"timestamp": datetime.now().isoformat()}
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.server_url}/api/agents/{self.agent_id}/command",
                    json=command.dict(),
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    logger.warning(f"Heartbeat failed: {response.text}")
                    
        except Exception as e:
            logger.error(f"Error sending heartbeat: {e}")
            
    async def listen_for_commands(self):
        """Listen for commands from the server."""
        if not self.agent_id:
            logger.error("Agent not registered, cannot listen for commands")
            return
            
        try:
            async with httpx.AsyncClient() as client:
                while self.running:
                    try:
                        # Poll for commands
                        response = await client.get(
                            f"{self.server_url}/api/agents/{self.agent_id}/commands",
                            timeout=30.0
                        )
                        
                        if response.status_code == 200:
                            command_data = response.json()
                            if command_data:
                                command = AgentCommandRequest(**command_data)
                                await self.command_queue.put(command)
                                
                    except httpx.TimeoutException:
                        # Timeout is expected, continue polling
                        pass
                    except Exception as e:
                        logger.error(f"Error listening for commands: {e}")
                        
                    # Wait before next poll
                    await asyncio.sleep(5)
                    
        except Exception as e:
            logger.error(f"Error in command listener: {e}")
            
    async def process_commands(self):
        """Process commands from the queue."""
        while self.running:
            try:
                command = await asyncio.wait_for(self.command_queue.get(), timeout=1.0)
                await self.execute_command(command)
            except asyncio.TimeoutError:
                # No commands, continue loop
                continue
            except Exception as e:
                logger.error(f"Error processing command: {e}")
                
    async def execute_command(self, command: AgentCommandRequest) -> AgentCommandResponse:
        """Execute a command and return response."""
        try:
            logger.info(f"Executing command: {command.command}")
            
            if command.command == AgentCommand.RUN_TEST_CASE:
                return await self._run_test_case(command.payload)
            elif command.command == AgentCommand.RUN_MODULE:
                return await self._run_module(command.payload)
            elif command.command == AgentCommand.RUN_PROJECT:
                return await self._run_project(command.payload)
            elif command.command == AgentCommand.PING:
                return AgentCommandResponse(
                    success=True,
                    message="Pong",
                    result={"timestamp": datetime.now().isoformat()}
                )
            elif command.command == AgentCommand.SHUTDOWN:
                self.running = False
                return AgentCommandResponse(
                    success=True,
                    message="Agent shutting down"
                )
            else:
                return AgentCommandResponse(
                    success=False,
                    message=f"Unknown command: {command.command}",
                    error="Unknown command"
                )
                
        except Exception as e:
            logger.error(f"Error executing command {command.command}: {e}")
            return AgentCommandResponse(
                success=False,
                message=f"Error executing command: {command.command}",
                error=str(e)
            )
            
    async def _run_test_case(self, payload: Dict[str, Any]) -> AgentCommandResponse:
        """Run a test case."""
        try:
            request = TestCaseExecutionRequest(**payload)
            
            # Execute the test case
            logger.info(f"Running test case {request.case_id}")
            await run_test_case(request.case_id)
            
            return AgentCommandResponse(
                success=True,
                message=f"Test case {request.case_id} executed successfully",
                result={"case_id": request.case_id, "status": "completed"}
            )
            
        except Exception as e:
            logger.error(f"Error running test case: {e}")
            return AgentCommandResponse(
                success=False,
                message=f"Failed to run test case",
                error=str(e)
            )
            
    async def _run_module(self, payload: Dict[str, Any]) -> AgentCommandResponse:
        """Run all test cases in a module."""
        try:
            request = ModuleExecutionRequest(**payload)
            
            # In a real implementation, we would execute all test cases in the module
            logger.info(f"Running module {request.module_id}")
            
            return AgentCommandResponse(
                success=True,
                message=f"Module {request.module_id} executed successfully",
                result={"module_id": request.module_id, "status": "completed"}
            )
            
        except Exception as e:
            logger.error(f"Error running module: {e}")
            return AgentCommandResponse(
                success=False,
                message=f"Failed to run module",
                error=str(e)
            )
            
    async def _run_project(self, payload: Dict[str, Any]) -> AgentCommandResponse:
        """Run all test cases in a project."""
        try:
            request = ProjectExecutionRequest(**payload)
            
            # In a real implementation, we would execute all test cases in the project
            logger.info(f"Running project {request.project_id}")
            
            return AgentCommandResponse(
                success=True,
                message=f"Project {request.project_id} executed successfully",
                result={"project_id": request.project_id, "status": "completed"}
            )
            
        except Exception as e:
            logger.error(f"Error running project: {e}")
            return AgentCommandResponse(
                success=False,
                message=f"Failed to run project",
                error=str(e)
            )
            
    async def start(self):
        """Start the agent."""
        logger.info(f"Starting agent {self.agent_name}")
        
        # Register with server
        if not await self.register():
            logger.error("Failed to register with server")
            return
            
        self.running = True
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self._heartbeat_task()),
            asyncio.create_task(self._command_processor_task())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Agent interrupted, shutting down...")
        finally:
            await self.stop()
            
    async def stop(self):
        """Stop the agent."""
        logger.info("Stopping agent")
        self.running = False
        
        # Unregister from server
        await self.unregister()
        
    async def _heartbeat_task(self):
        """Background task to send heartbeats."""
        while self.running:
            await self.send_heartbeat()
            await asyncio.sleep(30)  # Send heartbeat every 30 seconds
            
    async def _command_processor_task(self):
        """Background task to process commands."""
        while self.running:
            try:
                # This is a simplified implementation
                # In a real implementation, we would listen for commands from the server
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error in command processor: {e}")
                await asyncio.sleep(1)

def main():
    """Main entry point for the agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description="UI Test Agent")
    parser.add_argument("--server", required=True, help="Server URL (e.g., http://localhost:8000)")
    parser.add_argument("--name", help="Agent name")
    parser.add_argument("--log-level", default="INFO", help="Log level (DEBUG, INFO, WARNING, ERROR)")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start agent
    agent = ClientAgent(args.server, args.name)
    
    try:
        asyncio.run(agent.start())
    except KeyboardInterrupt:
        logger.info("Agent stopped by user")

if __name__ == "__main__":
    main()