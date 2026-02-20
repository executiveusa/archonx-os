"""
Calendar Management Skill
=========================
Schedule, reschedule, cancel meetings. Manage availability.
Podcast use case: "manage your calendar — schedule meetings around your preferences"
"""

from __future__ import annotations
from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult


class CalendarManagementSkill(BaseSkill):
    name = "calendar_management"
    description = "Schedule, reschedule, and manage calendar events"
    category = SkillCategory.PERSONAL
    _ACTIONS = {"list", "create", "update", "cancel"}

    async def execute(self, context: SkillContext) -> SkillResult:
        action = str(context.params.get("action", "list")).lower()
        if action not in self._ACTIONS:
            return SkillResult(skill=self.name, status="error", error=f"Unsupported action '{action}'")

        events = context.params.get("events", [])
        timezone = context.params.get("timezone", "UTC")
        return SkillResult(
            skill=self.name,
            status="success",
            data={"action": action, "events": events, "timezone": timezone},
            metadata={"event_count": len(events)},
            improvements_found=[],
        )
