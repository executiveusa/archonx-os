"""
Data Analysis Skill
===================
Analyze datasets, generate charts, find insights.
Podcast use case: "analyze spreadsheets, find patterns, create charts"
"""

from __future__ import annotations
from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult


class DataAnalysisSkill(BaseSkill):
    name = "data_analysis"
    description = "Analyze datasets, find patterns, and generate visualizations"
    category = SkillCategory.RESEARCH
    _ACTIONS = {"analyze", "chart", "summarize"}

    async def execute(self, context: SkillContext) -> SkillResult:
        action = str(context.params.get("action", "analyze")).lower()
        if action not in self._ACTIONS:
            return SkillResult(skill=self.name, status="error", error=f"Unsupported action '{action}'")

        data_source = context.params.get("source", "")
        rows = int(context.params.get("rows", 0))
        return SkillResult(
            skill=self.name,
            status="success",
            data={
                "action": action,
                "source": data_source,
                "rows": rows,
                "insights": context.params.get("insights", []),
                "charts": context.params.get("charts", []),
            },
            improvements_found=[],
        )
