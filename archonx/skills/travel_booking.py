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
    _MAX_TEXT_LEN = 200
    _MAX_PASSENGERS = 20
    _MAX_RESULTS = 50

    def _safe_text(self, value: object, default: str = "") -> str:
        text = str(value) if value is not None else default
        clean = "".join(ch if ch.isprintable() else " " for ch in text).strip()
        return clean[: self._MAX_TEXT_LEN]

    def _safe_passengers(self, value: object) -> int:
        try:
            passengers = int(value)
        except (TypeError, ValueError):
            return 1
        return max(1, min(passengers, self._MAX_PASSENGERS))

    def _sanitize_payload(self, value: object, depth: int = 0) -> object:
        if depth > 2:
            return self._safe_text(value)
        if isinstance(value, (int, float, bool)) or value is None:
            return value
        if isinstance(value, str):
            return self._safe_text(value)
        if isinstance(value, list):
            return [self._sanitize_payload(item, depth + 1) for item in value[: self._MAX_RESULTS]]
        if isinstance(value, dict):
            clean: dict[str, object] = {}
            for index, (key, item) in enumerate(value.items()):
                if index >= self._MAX_RESULTS:
                    break
                clean_key = self._safe_text(key)
                if not clean_key:
                    continue
                clean[clean_key] = self._sanitize_payload(item, depth + 1)
            return clean
        return self._safe_text(value)

    async def execute(self, context: SkillContext) -> SkillResult:
        action = self._safe_text(context.params.get("action", "search"), default="search").lower()
        travel_type = self._safe_text(context.params.get("type", "flight"), default="flight").lower()
        if action not in self._ACTIONS:
            return SkillResult(skill=self.name, status="error", error=f"Unsupported action '{action}'")
        if travel_type not in self._TYPES:
            return SkillResult(skill=self.name, status="error", error=f"Unsupported type '{travel_type}'")

        # Normalize untrusted payloads before they can be reused in downstream prompts/tools.
        passengers = self._safe_passengers(context.params.get("passengers", 1))
        origin = self._safe_text(context.params.get("origin", ""))
        destination = self._safe_text(context.params.get("destination", ""))
        results = self._sanitize_payload(context.params.get("results", []))
        if not isinstance(results, list):
            results = []
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
