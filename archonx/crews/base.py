"""
Base Crew
=========
Shared logic for both White and Black crews.
"""

from __future__ import annotations

import logging
from typing import Any

from archonx.core.agents import Agent, AgentRegistry, AgentStatus, Crew, Role
from archonx.core.protocol import Decision
from archonx.tools.base import ToolRegistry
from archonx.skills.registry import SkillRegistry
from archonx.skills.base import SkillContext

logger = logging.getLogger("archonx.crews.base")


class BaseCrew:
    """Abstract base for a 32-agent crew."""

    crew_side: Crew  # Override in subclass

    def __init__(
        self,
        registry: AgentRegistry,
        tools: ToolRegistry | None = None,
        skills: SkillRegistry | None = None,
    ) -> None:
        self.registry = registry
        self.tools = tools or ToolRegistry()
        self.skills = skills or SkillRegistry()
        self._agents: list[Agent] = []

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def initialize(self) -> None:
        self._agents = self.registry.get_by_crew(self.crew_side)
        for agent in self._agents:
            agent.status = AgentStatus.IDLE
        logger.info(
            "%s crew initialised — %d agents online.",
            self.crew_side.value.title(),
            len(self._agents),
        )

    async def shutdown(self) -> None:
        for agent in self._agents:
            agent.status = AgentStatus.OFFLINE
        logger.info("%s crew shut down.", self.crew_side.value.title())

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def king(self) -> Agent:
        kings = [a for a in self._agents if a.role == Role.KING]
        assert kings, f"No king found in {self.crew_side.value} crew!"
        return kings[0]

    @property
    def queen(self) -> Agent:
        queens = [a for a in self._agents if a.role == Role.QUEEN]
        assert queens, f"No queen found in {self.crew_side.value} crew!"
        return queens[0]

    @property
    def agents(self) -> list[Agent]:
        return list(self._agents)

    # ------------------------------------------------------------------
    # Task execution
    # ------------------------------------------------------------------

    async def execute(self, task: dict[str, Any], decision: Decision) -> dict[str, Any]:
        """
        Execute a task that has already been approved by the Fischer protocol.

        1. Queen decomposes into subtasks
        2. Best specialist is chosen per subtask
        3. Results aggregated and returned
        """
        queen = self.queen
        queen.activate()

        subtasks = self._decompose(task)
        results: list[dict[str, Any]] = []

        for subtask in subtasks:
            agent = self._find_best_agent(subtask)
            agent.activate()
            result = await self._run_subtask(agent, subtask)
            agent.record_task(points=1.0)
            agent.deactivate()
            results.append(result)

        queen.deactivate()

        return {
            "crew": self.crew_side.value,
            "subtasks_executed": len(results),
            "results": results,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _decompose(self, task: dict[str, Any]) -> list[dict[str, Any]]:
        """Break a task into specialist subtasks."""
        # Default: single subtask.  Override for smarter decomposition.
        return [task]

    def _find_best_agent(self, subtask: dict[str, Any]) -> Agent:
        """
        Pick the best idle agent whose specialty matches the subtask.
        Falls back to first idle pawn.
        """
        keyword = subtask.get("specialty_hint", "").lower()
        idle = [a for a in self._agents if a.status == AgentStatus.IDLE]

        # Try specialty match
        for agent in idle:
            if keyword and keyword in agent.specialty.lower():
                return agent

        # Fallback: first idle agent that isn't king
        for agent in idle:
            if agent.role != Role.KING:
                return agent

        # Last resort: queen handles it herself
        return self.queen

    async def _run_subtask(
        self, agent: Agent, subtask: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Execute a single subtask on the given agent.

        Dispatch order:
        1. If subtask specifies a "tool", run it through ToolRegistry.
        2. If subtask specifies a "skill", run it through SkillRegistry.
        3. Otherwise fall back to agent-only placeholder.
        """
        task_type = subtask.get("type", "unknown")
        logger.info(
            "[%s] %s (%s) executing subtask: %s",
            self.crew_side.value,
            agent.name,
            agent.role.value,
            task_type,
        )

        # --- Tool dispatch ---
        tool_name = subtask.get("tool")
        if tool_name and self.tools.get(tool_name):
            tool_result = await self.tools.execute(tool_name, subtask.get("params", {}))
            return {
                "agent": agent.agent_id,
                "agent_name": agent.name,
                "subtask": task_type,
                "status": tool_result.status,
                "data": tool_result.data,
                "via": "tool",
            }

        # --- Skill dispatch ---
        skill_name = subtask.get("skill")
        if skill_name and self.skills.get(skill_name):
            ctx = SkillContext(
                task=subtask,
                agent_id=agent.agent_id,
                session_id=subtask.get("session_id", ""),
                params=subtask.get("params", {}),
                tools=self.tools,
                skills=self.skills,
            )
            skill_result = await self.skills.execute(skill_name, ctx)
            return {
                "agent": agent.agent_id,
                "agent_name": agent.name,
                "subtask": task_type,
                "status": skill_result.status,
                "data": skill_result.data,
                "improvements_found": skill_result.improvements_found,
                "via": "skill",
            }

        # --- Fallback (LLM call placeholder) ---
        return {
            "agent": agent.agent_id,
            "agent_name": agent.name,
            "subtask": task_type,
            "status": "completed",
            "via": "placeholder",
        }
