import asyncio
import logging
import os
import subprocess
import time
from dataclasses import dataclass
from typing import Any, Optional

from archonx.core.agents import Agent, AgentStatus
from archonx.beads.viewer import Task, TaskStatus
from archonx.security.vault import ArchonXVault

logger = logging.getLogger("archonx.orchestration.agent_controller")

@dataclass
class AgentExecutionResult:
    """Result of an agent task execution."""
    success: bool
    output: str
    error: Optional[str] = None
    duration: float = 0.0
    tokens_used: int = 0
    cost: float = 0.0

class AgentController:
    """
    Coordinates real-world execution of agent tasks using the Ralphy loop.
    Bridges the strategic Orchestrator with the tactical Ralphy engine.
    """

    def __init__(self, workspace_root: str = "c:/archonx-os-main", ralphy_path: str = "c:/archonx-os-main/.ralphy-repo/ralphy.sh"):
        self.workspace_root = workspace_root
        self.ralphy_path = ralphy_path
        self.vault = ArchonXVault()
        self._ensure_ralphy_executable()

    def _ensure_ralphy_executable(self):
        """Ensure the ralphy script is executable (primarily for Unix-like environments)."""
        if os.name != 'nt':  # Non-windows
            try:
                subprocess.run(["chmod", "+x", self.ralphy_path], check=True)
            except Exception as e:
                logger.warning(f"Failed to set execution bits on {self.ralphy_path}: {e}")

    async def execute_task(self, agent: Agent, task: Task, use_jcodemunch: bool = True) -> AgentExecutionResult:
        """
        Executes a task using the specified agent and the Ralphy autonomous loop.
        """
        start_time = time.time()
        logger.info(f"Agent {agent.name} ({agent.agent_id}) starting task: {task.title}")
        
        # 1. Prepare Environment
        agent.status = AgentStatus.BUSY
        task.status = TaskStatus.IMPLEMENTING
        
        # Load secrets from vault
        secrets = self.vault.load_secrets()
        env = os.environ.copy()
        env.update(secrets)
        
        # 2. Build command
        # Syntax: ./ralphy.sh "prompt" --engine --model ...
        cmd = [
            "bash", self.ralphy_path,
            f"Task: {task.title}\nDescription: {task.description}",
            "--claude", 
            "--model", agent.model,
        ]
        
        if use_jcodemunch:
            # We assume jcodemunch-mcp is in the PATH or configured in .ralphy/config.yaml
            # For this implementation, we add a rule to use it
            cmd.extend(["--add-rule", "Use jcodemunch-mcp for code retrieval to save tokens"])

        # 3. Execution
        try:
            # Run ralphy as a subprocess
            # Note: In a production env, we'd want to stream logs via WebSocket
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.workspace_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await process.communicate()
            
            duration = time.time() - start_time
            success = process.returncode == 0
            
            output_str = stdout.decode()
            error_str = stderr.decode() if stderr else None
            
            if success:
                logger.info(f"Task {task.id} completed successfully by {agent.name}")
                task.status = TaskStatus.COMPLETED
                agent.record_task(points=10.0)
            else:
                logger.error(f"Task {task.id} failed: {error_str}")
                task.status = TaskStatus.FAILED
                task.error = error_str
            
            agent.status = AgentStatus.ACTIVE
            
            return AgentExecutionResult(
                success=success,
                output=output_str,
                error=error_str,
                duration=duration
            )

        except Exception as e:
            logger.exception(f"Exception during task execution for {task.id}")
            agent.status = AgentStatus.ERROR
            task.status = TaskStatus.FAILED
            task.error = str(e)
            return AgentExecutionResult(
                success=False,
                output="",
                error=str(e),
                duration=time.time() - start_time
            )

def get_agent_controller() -> AgentController:
    """Helper to get a configured controller instance."""
    return AgentController()
