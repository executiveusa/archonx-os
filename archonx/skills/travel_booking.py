"""
Travel Booking Skill
====================
Search flights, hotels, rental cars. Compare prices. Book trips.
Podcast use case: "book travel — find best flights, hotels, and plan itineraries"
"""

from __future__ import annotations
from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult


class TravelBookingSkill(BaseSkill):
    name = "travel_booking"
    description = "Search and book flights, hotels, and rental cars"
    category = SkillCategory.PERSONAL
    _ACTIONS = {"search", "compare", "book"}
    _TYPES = {"flight", "hotel", "car"}

    async def execute(self, context: SkillContext) -> SkillResult:
        action = str(context.params.get("action", "search")).lower()
        travel_type = str(context.params.get("type", "flight")).lower()
        if action not in self._ACTIONS:
            return SkillResult(skill=self.name, status="error", error=f"Unsupported action '{action}'")
        if travel_type not in self._TYPES:
            return SkillResult(skill=self.name, status="error", error=f"Unsupported type '{travel_type}'")

        passengers = int(context.params.get("passengers", 1))
        origin = context.params.get("origin", "")
        destination = context.params.get("destination", "")
        results = context.params.get("results", [])
        return SkillResult(
            skill=self.name,
            status="success",
            data={
                "action": action,
                "type": travel_type,
                "origin": origin,
                "destination": destination,
                "passengers": passengers,
                "results": results,
            },
            metadata={"result_count": len(results)},
            improvements_found=[],
        )
