"""
Price Monitoring Skill
======================
Track prices, set alerts, compare products.
Podcast use case: "monitor prices — track products, alert on drops"
"""

from __future__ import annotations
from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult


class PriceMonitoringSkill(BaseSkill):
    name = "price_monitoring"
    description = "Track product prices, set alerts, and compare options"
    category = SkillCategory.PERSONAL
    _ACTIONS = {"track", "alert", "compare", "history"}

    async def execute(self, context: SkillContext) -> SkillResult:
        action = str(context.params.get("action", "track")).lower()
        if action not in self._ACTIONS:
            return SkillResult(skill=self.name, status="error", error=f"Unsupported action '{action}'")

        products = context.params.get("products", [])
        return SkillResult(
            skill=self.name,
            status="success",
            data={
                "action": action,
                "products": products,
                "products_tracked": len(products),
                "alerts": context.params.get("alerts", []),
            },
            improvements_found=[],
        )
