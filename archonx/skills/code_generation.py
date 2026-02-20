"""
Code Generation Skill
=====================
Write, review, refactor, and test code in any language.
Podcast use case: "write and review code — full development lifecycle"
"""

from __future__ import annotations
from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult


class CodeGenerationSkill(BaseSkill):
    name = "code_generation"
    description = "Write, review, refactor, and test code"
    category = SkillCategory.AUTOMATION
    _ACTIONS = {"generate", "review", "refactor", "test"}

    async def execute(self, context: SkillContext) -> SkillResult:
        action = str(context.params.get("action", "generate")).lower()
        if action not in self._ACTIONS:
            return SkillResult(skill=self.name, status="error", error=f"Unsupported action '{action}'")

        language = str(context.params.get("language", "python")).lower()
        spec = context.params.get("spec", "")
        code = context.params.get("code", "")
        return SkillResult(
            skill=self.name,
            status="success",
            data={
                "action": action,
                "language": language,
                "spec": spec,
                "code": code,
                "next_steps": ["run tests", "lint code", "review changes"],
            },
            improvements_found=[],
        )
