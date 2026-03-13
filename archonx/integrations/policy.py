"""Approval and scope enforcement for Archon integration usage."""

from __future__ import annotations

from dataclasses import dataclass, field

from archonx.integrations.registry import IntegrationRegistry, build_default_integration_registry
from archonx.security.tool_gating import (
    AgentToolPolicy,
    ToolGatekeeper,
    ToolTrustEntry,
    TrustLevel,
)


@dataclass
class IntegrationPolicyDecision:
    """Policy outcome for one required integration."""

    integration_id: str
    allowed: bool
    requires_approval: bool
    reason: str

    def to_dict(self) -> dict:
        return {
            "integration_id": self.integration_id,
            "allowed": self.allowed,
            "requires_approval": self.requires_approval,
            "reason": self.reason,
        }


@dataclass
class IntegrationPolicyResult:
    """Aggregate policy outcome for a dispatch plan."""

    decisions: list[IntegrationPolicyDecision] = field(default_factory=list)

    @property
    def blocked_integrations(self) -> list[str]:
        return [
            decision.integration_id
            for decision in self.decisions
            if not decision.allowed and not decision.requires_approval
        ]

    @property
    def approval_integrations(self) -> list[str]:
        return [decision.integration_id for decision in self.decisions if decision.requires_approval]

    def to_dict(self) -> dict:
        return {
            "decisions": [decision.to_dict() for decision in self.decisions],
            "blocked_integrations": self.blocked_integrations,
            "approval_integrations": self.approval_integrations,
        }


class IntegrationPolicyEnforcer:
    """Maps canonical integrations onto Archon's tool gatekeeper."""

    def __init__(
        self,
        registry: IntegrationRegistry | None = None,
        gatekeeper: ToolGatekeeper | None = None,
    ) -> None:
        self.registry = registry or build_default_integration_registry()
        self.gatekeeper = gatekeeper or ToolGatekeeper()
        self._bootstrap_gatekeeper()

    def _bootstrap_gatekeeper(self) -> None:
        for capability in self.registry.list():
            self.gatekeeper.register_tool(
                ToolTrustEntry(
                    tool_name=capability.integration_id,
                    trust_level=TrustLevel.BUILTIN,
                    description=capability.description,
                    requires_approval=capability.approval_required,
                )
            )
        self.gatekeeper.set_policy(
            AgentToolPolicy(
                agent_id="archonx_dispatch",
                min_trust_level=TrustLevel.BUILTIN,
                allowed_tools={capability.integration_id for capability in self.registry.list()},
                auto_approve=True,
            )
        )

    def evaluate(self, integration_ids: list[str]) -> IntegrationPolicyResult:
        self.registry.require(integration_ids)
        decisions: list[IntegrationPolicyDecision] = []
        for integration_id in integration_ids:
            gating = self.gatekeeper.check("archonx_dispatch", integration_id)
            decisions.append(
                IntegrationPolicyDecision(
                    integration_id=integration_id,
                    allowed=gating.allowed,
                    requires_approval=gating.requires_approval,
                    reason=gating.reason,
                )
            )
        return IntegrationPolicyResult(decisions=decisions)
