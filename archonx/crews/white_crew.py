"""
White Crew - 32 Agent Orchestrator
"""

from __future__ import annotations
import logging
from typing import Any
from archonx.core.agents import AgentRegistry, Agent, Crew, AgentStatus
from archonx.tools.base import ToolRegistry
from archonx.skills.registry import SkillRegistry
from archonx.skills.base import SkillContext

logger = logging.getLogger("archonx.crews.white")

class WhiteCrew:
    def __init__(
        self,
        registry: AgentRegistry,
        tools: ToolRegistry | None = None,
        skills: SkillRegistry | None = None,
    ) -> None:
        self.registry = registry
        self.tools = tools or ToolRegistry()
        self.skills = skills or SkillRegistry()
        self.agents = registry.get_by_crew(Crew.WHITE)
        self.pauli = registry.get("pauli_king_white")
        self.synthia = registry.get("synthia_queen_white")
        logger.info("White Crew initialized with %d agents", len(self.agents))
    
    async def initialize(self) -> None:
        for agent in self.agents:
            agent.activate()
        logger.info("White Crew online")
    
    async def shutdown(self) -> None:
        for agent in self.agents:
            agent.deactivate()
        logger.info("White Crew offline")
    
    async def execute(self, task: dict[str, Any], decision: Any) -> dict[str, Any]:
        self.synthia.status = AgentStatus.BUSY
        specialists = self._select_specialists(task)
        results = await self._delegate_task(task, specialists)
        self.synthia.record_task(points=1.0)
        self.synthia.status = AgentStatus.ACTIVE
        return {
            "crew": "white",
            "executed_by": [a.name for a in specialists],
            "results": results,
        }
    
    def _select_specialists(self, task: dict[str, Any]) -> list[Agent]:
        routing = {
            "deployment": ["blitz_knight_white_b"],
            "security_scan": ["sentinel_rook_white_h"],
            "analytics": ["oracle_bishop_white_c"],
        }
        agent_ids = routing.get(task.get("type"), ["synthia_queen_white"])
        return [self.registry.get(aid) for aid in agent_ids if aid in self.registry._agents]
    
    async def _delegate_task(self, task: dict[str, Any], specialists: list[Agent]) -> dict[str, Any]:
        for agent in specialists:
            agent.status = AgentStatus.BUSY

        # Dispatch through tool/skill registries when applicable
        tool_name = task.get("tool")
        if tool_name and self.tools.get(tool_name):
            tool_result = await self.tools.execute(tool_name, task.get("params", {}))
            for agent in specialists:
                agent.status = AgentStatus.ACTIVE
            return {"status": tool_result.status, "task_type": task.get("type"), "data": tool_result.data, "via": "tool"}

        skill_name = task.get("skill")
        if skill_name and self.skills.get(skill_name):
            ctx = SkillContext(
                task=task,
                agent_id=specialists[0].agent_id if specialists else "",
                session_id=task.get("session_id", ""),
                params=task.get("params", {}),
                tools=self.tools,
                skills=self.skills,
            )
            skill_result = await self.skills.execute(skill_name, ctx)
            for agent in specialists:
                agent.status = AgentStatus.ACTIVE
            return {"status": skill_result.status, "task_type": task.get("type"), "data": skill_result.data, "via": "skill"}

        result = {"status": "success", "task_type": task.get("type")}
        for agent in specialists:
            agent.status = AgentStatus.ACTIVE
        return result
