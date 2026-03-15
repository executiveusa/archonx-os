"""
Workflow Automation Skill
=========================
Multi-step workflow orchestration — chain skills and tools together.
Podcast use case: "create workflows — chain multiple tasks like Zapier but smarter"
"""

from __future__ import annotations
from typing import Any
from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult


class WorkflowAutomationSkill(BaseSkill):
    name = "workflow_automation"
    description = "Chain skills and tools into multi-step automated workflows"
    category = SkillCategory.AUTOMATION

    async def execute(self, context: SkillContext) -> SkillResult:
        steps = context.params.get("steps", [])
        results = []
        for step in steps:
            skill_name = step.get("skill")
            if skill_name and context.skills:
                skill = context.skills.get(skill_name)
                if skill:
                    step_ctx = SkillContext(
                        task=step,
                        agent_id=context.agent_id,
                        session_id=context.session_id,
                        params=step.get("params", {}),
                        tools=context.tools,
                        skills=context.skills,
                    )
                    step_result = await skill.execute(step_ctx)
                    results.append({"skill": skill_name, "status": step_result.status, "data": step_result.data})
                    continue
            results.append({"skill": skill_name, "status": "skipped", "reason": "skill not found"})

        return SkillResult(
            skill=self.name,
            status="success",
            data={"steps_total": len(steps), "steps_completed": len(results), "results": results},
            improvements_found=[],
        )
