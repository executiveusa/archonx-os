"""
Financial Tracking Skill
========================
Track expenses, budgets, investments, crypto portfolios.
Podcast use case: "personal finance — track spending, budgets, investments"
"""

from __future__ import annotations
from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult


class FinancialTrackingSkill(BaseSkill):
    name = "financial_tracking"
    description = "Track expenses, budgets, investments, and financial goals"
    category = SkillCategory.FINANCIAL
    _ACTIONS = {"summary", "track", "budget", "invest"}

    async def execute(self, context: SkillContext) -> SkillResult:
        action = str(context.params.get("action", "summary")).lower()
        if action not in self._ACTIONS:
            return SkillResult(
                skill=self.name,
                status="error",
                error=f"Unsupported action '{action}'. Expected one of {sorted(self._ACTIONS)}",
            )

        transactions = context.params.get("transactions", [])
        balance = float(context.params.get("balance", 0.0))
        budget_limit = float(context.params.get("budget_limit", 0.0))
        spent = sum(float(t.get("amount", 0.0)) for t in transactions if isinstance(t, dict))
        remaining_budget = budget_limit - spent if budget_limit else None

        return SkillResult(
            skill=self.name,
            status="success",
            data={
                "action": action,
                "balance": balance,
                "transactions": transactions,
                "spent": spent,
                "budget_limit": budget_limit,
                "remaining_budget": remaining_budget,
            },
            metadata={"transaction_count": len(transactions)},
            improvements_found=(
                ["Add persistent ledger storage for transaction history"] if not transactions else []
            ),
        )
