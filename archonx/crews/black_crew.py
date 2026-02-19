"""
Black Crew - 32 Agent Orchestrator (Mirror of White)
"""

from __future__ import annotations
import logging
from typing import Any
from archonx.core.agents import AgentRegistry, Agent, Crew, AgentStatus
from archonx.tools.base import ToolRegistry
from archonx.skills.registry import SkillRegistry
from archonx.skills.base import SkillContext

logger = logging.getLogger("archonx.crews.black")

class BlackCrew:
    def __init__(
        self,
        registry: AgentRegistry,
        tools: ToolRegistry | None = None,
        skills: SkillRegistry | None = None,
    ) -> None:
        self.registry = registry
        self.tools = tools or ToolRegistry()
        self.skills = skills or SkillRegistry()
        self.agents = registry.get_by_crew(Crew.BLACK)
        self.mirror = registry.get("mirror_king_black")
        self.shadow = registry.get("shadow_queen_black")
        logger.info("Black Crew initialized with %d agents", len(self.agents))
    
    async def initialize(self) -> None:
        for agent in self.agents:
            agent.activate()
        logger.info("Black Crew online")
    
    async def shutdown(self) -> None:
        for agent in self.agents:
            agent.deactivate()
        logger.info("Black Crew offline")
    
    async def execute(self, task: dict[str, Any], decision: Any) -> dict[str, Any]:
        self.shadow.status = AgentStatus.BUSY
        specialists = self._select_specialists(task)
        results = await self._delegate_task(task, specialists)
        self.shadow.record_task(points=1.0)
        self.shadow.status = AgentStatus.ACTIVE
        return {
            "crew": "black",
            "executed_by": [a.name for a in specialists],
            "results": results,
        }
    
    def _select_specialists(self, task: dict[str, Any]) -> list[Agent]:
        routing = {
            "deployment": ["flash_knight_black_b"],
            "security_scan": ["warden_rook_black_h"],
            "analytics": ["seer_bishop_black_c"],
        }
        agent_ids = routing.get(task.get("type"), ["shadow_queen_black"])
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
