"""Sub-agent coordinator scaffolding for Devika PI flows."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DevikaSubagentPlan:
    planner: str
    implementer: str
    tester: str
    reviewer: str


class DevikaSubagentCoordinator:
    """Simple profile-aware subagent assignment."""

    def for_profile(self, profile: str) -> DevikaSubagentPlan:
        if profile == "devika-pi-research":
            return DevikaSubagentPlan(
                planner="research_planner",
                implementer="prototype_builder",
                tester="evidence_validator",
                reviewer="compliance_reviewer",
            )
        if profile == "devika-pi-safe":
            return DevikaSubagentPlan(
                planner="guardrail_planner",
                implementer="safe_implementer",
                tester="policy_tester",
                reviewer="security_reviewer",
            )
        return DevikaSubagentPlan(
            planner="default_planner",
            implementer="default_implementer",
            tester="default_tester",
            reviewer="default_reviewer",
        )

