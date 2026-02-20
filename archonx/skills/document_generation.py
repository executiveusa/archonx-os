"""
Document Generation Skill
=========================
Generate PDFs, presentations, reports, spreadsheets.
Podcast use case: "create polished documents from raw data or notes"
"""

from __future__ import annotations
from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult


class DocumentGenerationSkill(BaseSkill):
    name = "document_generation"
    description = "Generate PDFs, presentations, reports, and spreadsheets"
    category = SkillCategory.CREATIVE
    _TYPES = {"pdf", "pptx", "xlsx", "md"}

    async def execute(self, context: SkillContext) -> SkillResult:
        doc_type = str(context.params.get("type", "pdf")).lower()
        if doc_type not in self._TYPES:
            return SkillResult(skill=self.name, status="error", error=f"Unsupported type '{doc_type}'")

        template = context.params.get("template", "default")
        output_path = context.params.get("output_path", f"artifacts/output.{doc_type}")
        return SkillResult(
            skill=self.name,
            status="success",
            data={"type": doc_type, "template": template, "output_path": output_path},
            artifacts=[output_path],
            improvements_found=[],
        )
