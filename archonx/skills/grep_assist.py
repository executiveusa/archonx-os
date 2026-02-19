"""
Grep Assist Skill
=================
Structured search skill that wraps grep_mcp for crews.
"""

from __future__ import annotations

from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult


class GrepAssistSkill(BaseSkill):
    name = "grep_assist"
    description = "Search the workspace for symbols, snippets, and patterns"
    category = SkillCategory.RESEARCH
    required_tools = ["grep_mcp"]

    async def execute(self, context: SkillContext) -> SkillResult:
        if context.tools is None:
            return SkillResult(skill=self.name, status="error", error="Tool registry is not available")

        query = str(context.params.get("query", "")).strip()
        include = str(context.params.get("include", "")).strip()
        max_results = int(context.params.get("max_results", 50))

        if not query:
            return SkillResult(skill=self.name, status="error", error="query is required")

        tool_result = await context.tools.execute(
            "grep_mcp",
            {"query": query, "include": include, "max_results": max_results},
        )
        if tool_result.status != "success":
            return SkillResult(
                skill=self.name,
                status="error",
                error=tool_result.error or "grep_mcp failed",
                data={"query": query},
            )

        return SkillResult(
            skill=self.name,
            status="success",
            data=tool_result.data,
            improvements_found=[
                "Use grep_assist before implementing large refactors to map callsites quickly"
            ],
        )
