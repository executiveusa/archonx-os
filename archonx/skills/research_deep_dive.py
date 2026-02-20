"""
Research Deep Dive Skill
========================
Multi-source research with synthesis and citation tracking.
Podcast use case: "deep research on any topic — combine multiple sources"
"""

from __future__ import annotations
from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult


class ResearchDeepDiveSkill(BaseSkill):
    name = "research_deep_dive"
    description = "Multi-source research with synthesis and citations"
    category = SkillCategory.RESEARCH
    _DEPTH = {"quick", "standard", "deep"}

    async def execute(self, context: SkillContext) -> SkillResult:
        topic = context.params.get("topic", "")
        depth = str(context.params.get("depth", "standard")).lower()
        if depth not in self._DEPTH:
            return SkillResult(skill=self.name, status="error", error=f"Unsupported depth '{depth}'")

        sources = context.params.get("sources", [])
        synthesis = context.params.get("synthesis", "")
        citations = context.params.get("citations", [])
        return SkillResult(
            skill=self.name,
            status="success",
            data={
                "topic": topic,
                "depth": depth,
                "sources": sources,
                "synthesis": synthesis,
                "citations": citations,
            },
            metadata={"source_count": len(sources), "citation_count": len(citations)},
            improvements_found=[],
        )
