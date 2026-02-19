"""
Agent Swarm Deployment System
==============================
Deploy and orchestrate the 64-agent swarm with YOLO mode.

YOLO Mode: Zero human confirmation, autonomous execution.
Wave Execution: Groups of 5 agents running in parallel.

Usage:
    from archonx.orchestration.swarm import SwarmOrchestrator

    orchestrator = SwarmOrchestrator()
    await orchestrator.deploy_swarm(task="Upgrade repository", yolo=True)
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from archonx.logs.canonical_log import EventType, get_logger

logger = logging.getLogger("archonx.orchestration")


class CrewType(str, Enum):
    """Agent crew types."""
    WHITE = "white"  # Constructive, building
    BLACK = "black"  # Adversarial, testing


class AgentRole(str, Enum):
    """Agent roles within crews."""
    # White Crew - Constructive
    QUEEN = "queen"  # Strategic leader
    ARCHITECT = "architect"  # System design
    BUILDER = "builder"  # Implementation
    HEALER = "healer"  # Bug fixing
    MENTOR = "mentor"  # Documentation

    # Black Crew - Adversarial
    KING = "king"  # Attack coordinator
    ASSASSIN = "assassin"  # Security testing
    SABOTEUR = "saboteur"  # Stress testing
    SPY = "spy"  # Reconnaissance
    NEMESIS = "nemesis"  # Quality assurance


@dataclass
class Agent:
    """Represents a single agent in the swarm."""
    agent_id: str
    crew: CrewType
    role: AgentRole
    skills: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    status: str = "idle"
    current_task: str | None = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "crew": self.crew.value,
            "role": self.role.value,
            "skills": self.skills,
            "tools": self.tools,
            "status": self.status,
            "current_task": self.current_task,
            "created_at": self.created_at,
        }


@dataclass
class WaveResult:
    """Result from a wave of agents."""
    wave_id: str
    agents: list[str]
    results: dict[str, Any]
    success: bool
    duration_ms: int
    errors: list[str] = field(default_factory=list)


class SwarmOrchestrator:
    """
    Orchestrates the 64-agent swarm with wave-based execution.

    Features:
    - YOLO mode for autonomous execution
    - Wave-based parallel execution (5 agents per wave)
    - Crew coordination (White + Black)
    - Canonical logging for oversight
    """

    # Agent configurations
    WHITE_CREW_ROLES = [
        (AgentRole.QUEEN, ["orchestration", "strategy", "decision_making"]),
        (AgentRole.ARCHITECT, ["design", "architecture", "planning"]),
        (AgentRole.BUILDER, ["implementation", "coding", "building"]),
        (AgentRole.HEALER, ["debugging", "fixing", "optimization"]),
        (AgentRole.MENTOR, ["documentation", "teaching", "explanation"]),
    ]

    BLACK_CREW_ROLES = [
        (AgentRole.KING, ["attack_coordination", "security_strategy"]),
        (AgentRole.ASSASSIN, ["security_testing", "penetration", "vulnerability"]),
        (AgentRole.SABOTEUR, ["stress_testing", "chaos", "resilience"]),
        (AgentRole.SPY, ["reconnaissance", "research", "intelligence"]),
        (AgentRole.NEMESIS, ["quality_assurance", "critique", "review"]),
    ]

    def __init__(
        self,
        yolo: bool = False,
        wave_size: int = 5,
        max_waves: int = 13,  # 64 agents / 5 per wave ≈ 13 waves
        log_dir: str | None = None
    ):
        """
        Initialize the swarm orchestrator.

        Args:
            yolo: Enable YOLO mode (zero confirmation)
            wave_size: Number of agents per wave
            max_waves: Maximum number of waves
            log_dir: Directory for logs
        """
        self.yolo = yolo
        self.wave_size = wave_size
        self.max_waves = max_waves
        self.logger = get_logger(log_dir=log_dir)
        self.agents: list[Agent] = []
        self.active_waves: dict[str, list[Agent]] = {}
        self.session_id = self.logger.session_id

        # Initialize agents
        self._initialize_agents()

        logger.info(
            "Swarm orchestrator initialized with %d agents (YOLO: %s)",
            len(self.agents), yolo
        )

    def _initialize_agents(self) -> None:
        """Initialize all 64 agents."""
        agent_id = 0

        # White Crew (32 agents)
        for i in range(32):
            role, skills = self.WHITE_CREW_ROLES[i % len(self.WHITE_CREW_ROLES)]
            agent = Agent(
                agent_id=f"White-{role.value[:3]}-{agent_id:02d}",
                crew=CrewType.WHITE,
                role=role,
                skills=skills,
                tools=["chrome-devtools", "remotion", "computer_use"],
            )
            self.agents.append(agent)
            agent_id += 1

        # Black Crew (32 agents)
        for i in range(32):
            role, skills = self.BLACK_CREW_ROLES[i % len(self.BLACK_CREW_ROLES)]
            agent = Agent(
                agent_id=f"Black-{role.value[:3]}-{agent_id:02d}",
                crew=CrewType.BLACK,
                role=role,
                skills=skills,
                tools=["brightdata", "orgo", "analytics"],
            )
            self.agents.append(agent)
            agent_id += 1

    async def deploy_swarm(
        self,
        task: str,
        yolo: bool | None = None,
        crews: list[CrewType] | None = None,
        skills_filter: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Deploy the agent swarm for a task.

        Args:
            task: Task description
            yolo: Override YOLO mode setting
            crews: Filter by crew types
            skills_filter: Filter by required skills

        Returns:
            Deployment results
        """
        yolo_mode = yolo if yolo is not None else self.yolo

        # Log swarm deployment
        self.logger.log_system(f"Deploying swarm for task: {task}")

        # Filter agents
        filtered_agents = self._filter_agents(crews, skills_filter)

        if not filtered_agents:
            return {"error": "No agents match the filter criteria"}

        # Create waves
        waves = self._create_waves(filtered_agents)

        # Execute waves
        results = []
        for wave_id, wave_agents in enumerate(waves, 1):
            wave_result = await self._execute_wave(
                f"wave_{wave_id:02d}", wave_agents, task, yolo_mode
            )
            results.append(wave_result)

            # Log wave completion
            self.logger.log_wave_complete(
                wave_id=f"wave_{wave_id:02d}",
                results=wave_result.results
            )

        # Compile final results
        final_result = {
            "task": task,
            "yolo_mode": yolo_mode,
            "total_agents": len(filtered_agents),
            "total_waves": len(waves),
            "wave_results": [r.__dict__ for r in results],
            "success": all(r.success for r in results),
            "session_id": self.session_id,
        }

        return final_result

    def _filter_agents(
        self,
        crews: list[CrewType] | None,
        skills: list[str] | None
    ) -> list[Agent]:
        """Filter agents by crew and skills."""
        filtered = self.agents

        if crews:
            filtered = [a for a in filtered if a.crew in crews]

        if skills:
            filtered = [
                a for a in filtered
                if any(skill in a.skills for skill in skills)
            ]

        return filtered

    def _create_waves(self, agents: list[Agent]) -> list[list[Agent]]:
        """Create waves of agents."""
        waves = []
        for i in range(0, len(agents), self.wave_size):
            wave = agents[i:i + self.wave_size]
            waves.append(wave)
        return waves[:self.max_waves]

    async def _execute_wave(
        self,
        wave_id: str,
        agents: list[Agent],
        task: str,
        yolo: bool
    ) -> WaveResult:
        """Execute a wave of agents in parallel."""
        start_time = datetime.utcnow()

        # Log wave start
        self.logger.log_wave_start(
            wave_id=wave_id,
            agent_ids=[a.agent_id for a in agents]
        )

        # Update agent status
        for agent in agents:
            agent.status = "active"
            agent.current_task = task

        # Execute agents in parallel
        tasks = [
            self._execute_agent(agent, task, yolo)
            for agent in agents
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        agent_results = {}
        errors = []
        for agent, result in zip(agents, results):
            if isinstance(result, Exception):
                errors.append(f"{agent.agent_id}: {str(result)}")
                agent_results[agent.agent_id] = {"error": str(result)}
            else:
                agent_results[agent.agent_id] = result

        # Update agent status
        for agent in agents:
            agent.status = "completed"
            agent.current_task = None

        # Calculate duration
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        return WaveResult(
            wave_id=wave_id,
            agents=[a.agent_id for a in agents],
            results=agent_results,
            success=len(errors) == 0,
            duration_ms=duration_ms,
            errors=errors,
        )

    async def _execute_agent(
        self,
        agent: Agent,
        task: str,
        yolo: bool
    ) -> dict[str, Any]:
        """Execute a single agent's task."""
        # Log agent start
        self.logger.log_agent_start(
            agent_id=agent.agent_id,
            task_type=agent.role.value,
            params={"task": task, "yolo": yolo}
        )

        try:
            # Simulate agent execution
            # In production, this would invoke the actual agent
            result = await self._run_agent_logic(agent, task, yolo)

            # Log completion
            self.logger.log_task_complete(
                agent_id=agent.agent_id,
                task_id=f"task_{agent.agent_id}",
                result=result
            )

            return result

        except Exception as e:
            # Log error
            self.logger.log_agent_error(
                agent_id=agent.agent_id,
                error=str(e)
            )
            raise

    async def _run_agent_logic(
        self,
        agent: Agent,
        task: str,
        yolo: bool
    ) -> dict[str, Any]:
        """
        Run the actual agent logic.

        This is a placeholder that should be replaced with actual
        agent execution logic.
        """
        # Simulate processing time
        await asyncio.sleep(0.1)

        return {
            "agent_id": agent.agent_id,
            "crew": agent.crew.value,
            "role": agent.role.value,
            "task": task,
            "status": "completed",
            "yolo_mode": yolo,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_agent_status(self, agent_id: str | None = None) -> dict[str, Any]:
        """Get status of agents."""
        if agent_id:
            agent = next((a for a in self.agents if a.agent_id == agent_id), None)
            if agent:
                return agent.to_dict()
            return {"error": f"Agent {agent_id} not found"}

        return {
            "total_agents": len(self.agents),
            "by_crew": {
                "white": len([a for a in self.agents if a.crew == CrewType.WHITE]),
                "black": len([a for a in self.agents if a.crew == CrewType.BLACK]),
            },
            "by_status": {
                "idle": len([a for a in self.agents if a.status == "idle"]),
                "active": len([a for a in self.agents if a.status == "active"]),
                "completed": len([a for a in self.agents if a.status == "completed"]),
            },
            "agents": [a.to_dict() for a in self.agents],
        }

    def get_swarm_stats(self) -> dict[str, Any]:
        """Get swarm statistics."""
        return {
            "session_id": self.session_id,
            "yolo_mode": self.yolo,
            "wave_size": self.wave_size,
            "max_waves": self.max_waves,
            "total_agents": len(self.agents),
            "active_waves": len(self.active_waves),
            "log_file": str(self.logger.log_file),
            "log_stats": self.logger.get_stats(),
        }


async def deploy_yolo_swarm(task: str) -> dict[str, Any]:
    """
    Quick function to deploy a YOLO mode swarm.

    Args:
        task: Task description

    Returns:
        Deployment results
    """
    orchestrator = SwarmOrchestrator(yolo=True)
    return await orchestrator.deploy_swarm(task=task, yolo=True)


def create_swarm(yolo: bool = False) -> SwarmOrchestrator:
    """
    Create a new swarm orchestrator.

    Args:
        yolo: Enable YOLO mode

    Returns:
        SwarmOrchestrator instance
    """
    return SwarmOrchestrator(yolo=yolo)
