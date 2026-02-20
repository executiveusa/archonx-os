"""
Orchestrator Agent
==================
Central command agent for the 64-agent swarm.

Commands:
- CREATE: Create a new task
- ASSIGN: Assign task to agent(s)
- STATUS: Get task/agent status
- PAUSE: Pause a task
- RESUME: Resume a paused task
- TERMINATE: End a task

BEAD-004: Orchestrator Agent Implementation
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

from archonx.core.agents import (
    Agent, AgentRegistry, AgentStatus, Crew, Role,
    build_all_agents
)
from archonx.beads.viewer import TaskManager, Task, TaskStatus, TaskPriority
from archonx.mail.server import AgentMailServer, MessageType

logger = logging.getLogger("archonx.orchestration.orchestrator")


class OrchestratorCommand(str, Enum):
    """Orchestrator commands."""
    CREATE = "CREATE"
    ASSIGN = "ASSIGN"
    STATUS = "STATUS"
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    TERMINATE = "TERMINATE"
    LIST = "LIST"
    DELEGATE = "DELEGATE"


class TaskType(str, Enum):
    """Types of tasks the orchestrator can create."""
    CODE = "code"
    REVIEW = "review"
    DEPLOY = "deploy"
    TEST = "test"
    ANALYSIS = "analysis"
    SECURITY = "security"
    DOCUMENTATION = "documentation"
    INTEGRATION = "integration"
    OPTIMIZATION = "optimization"
    CUSTOM = "custom"


@dataclass
class OrchestratorResult:
    """Result from an orchestrator command."""
    success: bool
    command: OrchestratorCommand
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "command": self.command.value,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp
        }


class Orchestrator:
    """
    Central command agent for the 64-agent swarm.
    
    The Orchestrator sits at the top of the hierarchy and can:
    - Create and manage tasks
    - Assign tasks to agents
    - Monitor agent and task status
    - Coordinate between White and Black crews
    - Delegate to Queens (Synthia/Shadow) for tactical execution
    
    Usage:
        orchestrator = Orchestrator()
        await orchestrator.initialize()
        
        # Create a task
        result = await orchestrator.create_task(
            title="Build API endpoint",
            task_type=TaskType.CODE,
            priority=TaskPriority.HIGH
        )
        
        # Assign to agent
        result = await orchestrator.assign_task(
            task_id=result.data["task_id"],
            agent_id="synthia_queen_white"
        )
        
        # Check status
        status = await orchestrator.get_status(task_id="task-000001")
    """

    def __init__(
        self,
        registry: Optional[AgentRegistry] = None,
        task_manager: Optional[TaskManager] = None,
        mail_server: Optional[AgentMailServer] = None
    ) -> None:
        """
        Initialize the Orchestrator.
        
        Args:
            registry: Agent registry (will be created if not provided)
            task_manager: Task manager (will be created if not provided)
            mail_server: Mail server for agent communication
        """
        self.registry = registry or AgentRegistry()
        self.task_manager = task_manager or TaskManager()
        self.mail_server = mail_server
        
        self._initialized = False
        self._command_handlers: dict[
            OrchestratorCommand,
            callable
        ] = {
            OrchestratorCommand.CREATE: self._handle_create,
            OrchestratorCommand.ASSIGN: self._handle_assign,
            OrchestratorCommand.STATUS: self._handle_status,
            OrchestratorCommand.PAUSE: self._handle_pause,
            OrchestratorCommand.RESUME: self._handle_resume,
            OrchestratorCommand.TERMINATE: self._handle_terminate,
            OrchestratorCommand.LIST: self._handle_list,
            OrchestratorCommand.DELEGATE: self._handle_delegate,
        }
        
        logger.info("Orchestrator initialized")

    async def initialize(self) -> None:
        """Initialize the orchestrator and all agents."""
        if self._initialized:
            return
        
        # Build all 64 agents if registry is empty
        if len(self.registry) == 0:
            build_all_agents(self.registry)
        
        # Activate all agents
        for agent in self.registry.all():
            agent.activate()
        
        self._initialized = True
        logger.info(f"Orchestrator ready with {len(self.registry)} agents")

    # --- Command Handlers ---

    async def execute_command(
        self,
        command: Union[OrchestratorCommand, str],
        **kwargs
    ) -> OrchestratorResult:
        """
        Execute an orchestrator command.
        
        Args:
            command: The command to execute
            **kwargs: Command-specific arguments
            
        Returns:
            OrchestratorResult with command outcome
        """
        if isinstance(command, str):
            try:
                command = OrchestratorCommand(command.upper())
            except ValueError:
                return OrchestratorResult(
                    success=False,
                    command=OrchestratorCommand(command.upper()),
                    message=f"Unknown command: {command}"
                )
        
        handler = self._command_handlers.get(command)
        if not handler:
            return OrchestratorResult(
                success=False,
                command=command,
                message=f"No handler for command: {command}"
            )
        
        try:
            return await handler(**kwargs)
        except Exception as e:
            logger.exception(f"Error executing {command}")
            return OrchestratorResult(
                success=False,
                command=command,
                message=f"Error: {str(e)}"
            )

    async def _handle_create(
        self,
        title: str,
        task_type: TaskType = TaskType.CODE,
        description: str = "",
        priority: TaskPriority = TaskPriority.NORMAL,
        assigned_agent: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        **kwargs
    ) -> OrchestratorResult:
        """Handle CREATE command."""
        # Add task type to tags
        all_tags = tags or []
        if task_type.value not in all_tags:
            all_tags.append(task_type.value)
        
        # Create task
        task = self.task_manager.create_task(
            title=title,
            description=description,
            priority=priority,
            assigned_agent=assigned_agent,
            tags=all_tags,
            metadata=metadata or {}
        )
        
        # Notify via mail if agent assigned
        if assigned_agent and self.mail_server:
            await self.mail_server.send_message(
                sender="orchestrator",
                recipient=assigned_agent,
                subject=f"New Task: {title}",
                payload={"task_id": task.id, "command": "CREATE"},
                message_type=MessageType.COMMAND
            )
        
        logger.info(f"Created task {task.id}: {title}")
        
        return OrchestratorResult(
            success=True,
            command=OrchestratorCommand.CREATE,
            message=f"Task {task.id} created",
            data={"task_id": task.id, "task": task.to_dict()}
        )

    async def _handle_assign(
        self,
        task_id: str,
        agent_id: str,
        **kwargs
    ) -> OrchestratorResult:
        """Handle ASSIGN command."""
        # Verify agent exists
        agent = self.registry.get(agent_id)
        if not agent:
            return OrchestratorResult(
                success=False,
                command=OrchestratorCommand.ASSIGN,
                message=f"Agent not found: {agent_id}"
            )
        
        # Verify agent is available
        if agent.status == AgentStatus.BUSY:
            return OrchestratorResult(
                success=False,
                command=OrchestratorCommand.ASSIGN,
                message=f"Agent {agent_id} is busy"
            )
        
        # Assign task
        task = self.task_manager.assign_task(task_id, agent_id)
        if not task:
            return OrchestratorResult(
                success=False,
                command=OrchestratorCommand.ASSIGN,
                message=f"Task not found: {task_id}"
            )
        
        # Notify agent
        if self.mail_server:
            await self.mail_server.send_message(
                sender="orchestrator",
                recipient=agent_id,
                subject=f"Assigned: {task.title}",
                payload={"task_id": task_id, "command": "ASSIGN"},
                message_type=MessageType.COMMAND
            )
        
        logger.info(f"Assigned task {task_id} to {agent_id}")
        
        return OrchestratorResult(
            success=True,
            command=OrchestratorCommand.ASSIGN,
            message=f"Task {task_id} assigned to {agent_id}",
            data={"task_id": task_id, "agent_id": agent_id}
        )

    async def _handle_status(
        self,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        **kwargs
    ) -> OrchestratorResult:
        """Handle STATUS command."""
        data = {}
        
        if task_id:
            task = self.task_manager.get_task(task_id)
            if not task:
                return OrchestratorResult(
                    success=False,
                    command=OrchestratorCommand.STATUS,
                    message=f"Task not found: {task_id}"
                )
            data["task"] = task.to_dict()
        
        if agent_id:
            agent = self.registry.get(agent_id)
            if not agent:
                return OrchestratorResult(
                    success=False,
                    command=OrchestratorCommand.STATUS,
                    message=f"Agent not found: {agent_id}"
                )
            data["agent"] = {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "status": agent.status.value,
                "health": agent.health,
                "tasks_completed": agent.tasks_completed,
                "score": agent.score
            }
        
        if not task_id and not agent_id:
            # Return overall status
            data["agents"] = {
                "total": len(self.registry),
                "by_status": self._get_agent_status_counts(),
                "by_crew": {
                    "white": len(self.registry.get_by_crew(Crew.WHITE)),
                    "black": len(self.registry.get_by_crew(Crew.BLACK))
                }
            }
            data["tasks"] = self.task_manager.get_stats()
        
        return OrchestratorResult(
            success=True,
            command=OrchestratorCommand.STATUS,
            message="Status retrieved",
            data=data
        )

    async def _handle_pause(
        self,
        task_id: str,
        reason: Optional[str] = None,
        **kwargs
    ) -> OrchestratorResult:
        """Handle PAUSE command."""
        task = self.task_manager.update_status(
            task_id,
            TaskStatus.PAUSED,
            result=reason
        )
        
        if not task:
            return OrchestratorResult(
                success=False,
                command=OrchestratorCommand.PAUSE,
                message=f"Task not found: {task_id}"
            )
        
        # Notify assigned agent
        if task.assigned_agent and self.mail_server:
            await self.mail_server.send_message(
                sender="orchestrator",
                recipient=task.assigned_agent,
                subject=f"Task Paused: {task.title}",
                payload={"task_id": task_id, "reason": reason, "command": "PAUSE"},
                message_type=MessageType.COMMAND
            )
        
        logger.info(f"Paused task {task_id}")
        
        return OrchestratorResult(
            success=True,
            command=OrchestratorCommand.PAUSE,
            message=f"Task {task_id} paused",
            data={"task_id": task_id, "reason": reason}
        )

    async def _handle_resume(
        self,
        task_id: str,
        **kwargs
    ) -> OrchestratorResult:
        """Handle RESUME command."""
        task = self.task_manager.get_task(task_id)
        if not task:
            return OrchestratorResult(
                success=False,
                command=OrchestratorCommand.RESUME,
                message=f"Task not found: {task_id}"
            )
        
        if task.status != TaskStatus.PAUSED:
            return OrchestratorResult(
                success=False,
                command=OrchestratorCommand.RESUME,
                message=f"Task {task_id} is not paused (status: {task.status.value})"
            )
        
        # Resume to implementing status
        task = self.task_manager.update_status(task_id, TaskStatus.IMPLEMENTING)
        
        # Notify assigned agent
        if task and task.assigned_agent and self.mail_server:
            await self.mail_server.send_message(
                sender="orchestrator",
                recipient=task.assigned_agent,
                subject=f"Task Resumed: {task.title}",
                payload={"task_id": task_id, "command": "RESUME"},
                message_type=MessageType.COMMAND
            )
        
        logger.info(f"Resumed task {task_id}")
        
        return OrchestratorResult(
            success=True,
            command=OrchestratorCommand.RESUME,
            message=f"Task {task_id} resumed",
            data={"task_id": task_id}
        )

    async def _handle_terminate(
        self,
        task_id: str,
        reason: Optional[str] = None,
        **kwargs
    ) -> OrchestratorResult:
        """Handle TERMINATE command."""
        task = self.task_manager.get_task(task_id)
        if not task:
            return OrchestratorResult(
                success=False,
                command=OrchestratorCommand.TERMINATE,
                message=f"Task not found: {task_id}"
            )
        
        # Mark as failed with reason
        task = self.task_manager.update_status(
            task_id,
            TaskStatus.FAILED,
            error=reason or "Terminated by orchestrator"
        )
        
        # Notify assigned agent
        if task and task.assigned_agent and self.mail_server:
            await self.mail_server.send_message(
                sender="orchestrator",
                recipient=task.assigned_agent,
                subject=f"Task Terminated: {task.title}",
                payload={"task_id": task_id, "reason": reason, "command": "TERMINATE"},
                message_type=MessageType.ALERT
            )
        
        logger.info(f"Terminated task {task_id}")
        
        return OrchestratorResult(
            success=True,
            command=OrchestratorCommand.TERMINATE,
            message=f"Task {task_id} terminated",
            data={"task_id": task_id, "reason": reason}
        )

    async def _handle_list(
        self,
        status: Optional[str] = None,
        agent_id: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 50,
        **kwargs
    ) -> OrchestratorResult:
        """Handle LIST command."""
        filters = {}
        
        if status:
            filters["status"] = TaskStatus(status)
        if agent_id:
            filters["agent"] = agent_id
        if priority:
            filters["priority"] = TaskPriority(priority)
        
        tasks = self.task_manager.get_all_tasks(**filters)[:limit]
        
        return OrchestratorResult(
            success=True,
            command=OrchestratorCommand.LIST,
            message=f"Found {len(tasks)} tasks",
            data={
                "tasks": [t.to_dict() for t in tasks],
                "count": len(tasks),
                "filters": {k: v.value if hasattr(v, 'value') else v for k, v in filters.items()}
            }
        )

    async def _handle_delegate(
        self,
        task_id: str,
        crew: str = "white",
        **kwargs
    ) -> OrchestratorResult:
        """
        Handle DELEGATE command.
        
        Delegates a task to a Queen (Synthia for White, Shadow for Black)
        for tactical execution and coordination.
        """
        task = self.task_manager.get_task(task_id)
        if not task:
            return OrchestratorResult(
                success=False,
                command=OrchestratorCommand.DELEGATE,
                message=f"Task not found: {task_id}"
            )
        
        # Select Queen based on crew
        queen_id = "synthia_queen_white" if crew.lower() == "white" else "shadow_queen_black"
        queen = self.registry.get(queen_id)
        
        if not queen:
            return OrchestratorResult(
                success=False,
                command=OrchestratorCommand.DELEGATE,
                message=f"Queen not found: {queen_id}"
            )
        
        # Assign to Queen
        task = self.task_manager.assign_task(task_id, queen_id)
        
        # Send delegation message
        if self.mail_server:
            await self.mail_server.send_message(
                sender="orchestrator",
                recipient=queen_id,
                subject=f"Delegated: {task.title}",
                payload={
                    "task_id": task_id,
                    "command": "DELEGATE",
                    "crew": crew
                },
                message_type=MessageType.COMMAND,
                priority=1  # High priority
            )
        
        logger.info(f"Delegated task {task_id} to {queen_id}")
        
        return OrchestratorResult(
            success=True,
            command=OrchestratorCommand.DELEGATE,
            message=f"Task {task_id} delegated to {queen.name}",
            data={"task_id": task_id, "queen_id": queen_id, "crew": crew}
        )

    # --- Convenience Methods ---

    async def create_task(
        self,
        title: str,
        task_type: TaskType = TaskType.CODE,
        **kwargs
    ) -> OrchestratorResult:
        """Create a new task."""
        return await self.execute_command(
            OrchestratorCommand.CREATE,
            title=title,
            task_type=task_type,
            **kwargs
        )

    async def assign_task(
        self,
        task_id: str,
        agent_id: str
    ) -> OrchestratorResult:
        """Assign a task to an agent."""
        return await self.execute_command(
            OrchestratorCommand.ASSIGN,
            task_id=task_id,
            agent_id=agent_id
        )

    async def get_status(
        self,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> OrchestratorResult:
        """Get status of task or agent."""
        return await self.execute_command(
            OrchestratorCommand.STATUS,
            task_id=task_id,
            agent_id=agent_id
        )

    async def pause_task(
        self,
        task_id: str,
        reason: Optional[str] = None
    ) -> OrchestratorResult:
        """Pause a task."""
        return await self.execute_command(
            OrchestratorCommand.PAUSE,
            task_id=task_id,
            reason=reason
        )

    async def resume_task(self, task_id: str) -> OrchestratorResult:
        """Resume a paused task."""
        return await self.execute_command(
            OrchestratorCommand.RESUME,
            task_id=task_id
        )

    async def terminate_task(
        self,
        task_id: str,
        reason: Optional[str] = None
    ) -> OrchestratorResult:
        """Terminate a task."""
        return await self.execute_command(
            OrchestratorCommand.TERMINATE,
            task_id=task_id,
            reason=reason
        )

    async def list_tasks(
        self,
        status: Optional[str] = None,
        agent_id: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 50
    ) -> OrchestratorResult:
        """List tasks with optional filters."""
        return await self.execute_command(
            OrchestratorCommand.LIST,
            status=status,
            agent_id=agent_id,
            priority=priority,
            limit=limit
        )

    async def delegate_task(
        self,
        task_id: str,
        crew: str = "white"
    ) -> OrchestratorResult:
        """Delegate a task to a Queen."""
        return await self.execute_command(
            OrchestratorCommand.DELEGATE,
            task_id=task_id,
            crew=crew
        )

    # --- Helper Methods ---

    def _get_agent_status_counts(self) -> dict[str, int]:
        """Get count of agents by status."""
        counts = {}
        for agent in self.registry.all():
            status = agent.status.value
            counts[status] = counts.get(status, 0) + 1
        return counts

    def get_available_agents(
        self,
        role: Optional[Role] = None,
        crew: Optional[Crew] = None
    ) -> list[Agent]:
        """Get list of available agents."""
        agents = self.registry.all()
        
        if role:
            agents = [a for a in agents if a.role == role]
        if crew:
            agents = [a for a in agents if a.crew == crew]
        
        return [a for a in agents if a.status == AgentStatus.ACTIVE]

    def get_agent_for_task(
        self,
        task_type: TaskType,
        crew: Crew = Crew.WHITE
    ) -> Optional[Agent]:
        """
        Find the best available agent for a task type.
        
        Uses role-based routing:
        - CODE: Knights (rapid deployment)
        - DEPLOY: Knights (rapid deployment)
        - TEST: Pawns (Probe/Trace)
        - SECURITY: Rooks (Sentinel/Warden)
        - ANALYSIS: Bishops (Oracle/Seer)
        - DOCUMENTATION: Pawns (Quill/Inker)
        """
        role_mapping = {
            TaskType.CODE: Role.KNIGHT,
            TaskType.DEPLOY: Role.KNIGHT,
            TaskType.TEST: Role.PAWN,
            TaskType.SECURITY: Role.ROOK,
            TaskType.ANALYSIS: Role.BISHOP,
            TaskType.DOCUMENTATION: Role.PAWN,
            TaskType.REVIEW: Role.BISHOP,
            TaskType.INTEGRATION: Role.PAWN,
            TaskType.OPTIMIZATION: Role.KNIGHT,
        }
        
        preferred_role = role_mapping.get(task_type, Role.PAWN)
        
        # Get available agents with preferred role
        agents = self.get_available_agents(role=preferred_role, crew=crew)
        
        if agents:
            # Return agent with lowest task count
            return min(agents, key=lambda a: a.tasks_completed)
        
        # Fallback to any available agent in crew
        agents = self.get_available_agents(crew=crew)
        return agents[0] if agents else None


# Singleton instance
_orchestrator: Optional[Orchestrator] = None


def get_orchestrator() -> Orchestrator:
    """Get the singleton Orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator
