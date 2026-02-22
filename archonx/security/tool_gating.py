"""
Tool Trust Gating — Per-agent tool access control with trust levels.

Adapted from IronClaw's skills trust system. Implements:
- Trust tiers: BUILTIN > VERIFIED > COMMUNITY
- Per-agent tool allowlists
- auto_approve toggle (require human confirmation)
- Iteration limits per task
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any

logger = logging.getLogger("archonx.security.tool_gating")


class TrustLevel(IntEnum):
    """Trust tiers — higher is more trusted."""
    COMMUNITY = 0
    VERIFIED = 1
    BUILTIN = 2


@dataclass
class ToolTrustEntry:
    """Registration of a tool with its trust level."""
    tool_name: str
    trust_level: TrustLevel = TrustLevel.COMMUNITY
    description: str = ""
    requires_approval: bool = False


@dataclass
class AgentToolPolicy:
    """Per-agent tool access configuration."""
    agent_id: str
    min_trust_level: TrustLevel = TrustLevel.COMMUNITY
    allowed_tools: set[str] | None = None  # None = all at or above min_trust
    denied_tools: set[str] = field(default_factory=set)
    auto_approve: bool = True
    max_iterations: int = 50


@dataclass
class GatingDecision:
    allowed: bool
    reason: str
    requires_approval: bool = False


class ToolGatekeeper:
    """
    Central gating authority for tool access.

    Evaluates whether agent X may invoke tool Y based on:
    1. Tool trust level vs agent minimum trust requirement
    2. Agent-specific allowed/denied tool lists
    3. Tool-specific approval requirements
    4. Iteration limits
    """

    def __init__(self) -> None:
        self._tools: dict[str, ToolTrustEntry] = {}
        self._policies: dict[str, AgentToolPolicy] = {}
        logger.info("ToolGatekeeper initialized")

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_tool(self, entry: ToolTrustEntry) -> None:
        self._tools[entry.tool_name] = entry

    def set_policy(self, policy: AgentToolPolicy) -> None:
        self._policies[policy.agent_id] = policy

    # ------------------------------------------------------------------
    # Gate check
    # ------------------------------------------------------------------

    def check(
        self,
        agent_id: str,
        tool_name: str,
        iteration: int = 0,
    ) -> GatingDecision:
        """Evaluate whether agent may invoke tool."""
        tool = self._tools.get(tool_name)
        policy = self._policies.get(agent_id)

        # Unknown tool — default allow at COMMUNITY trust
        if tool is None:
            tool = ToolTrustEntry(tool_name=tool_name, trust_level=TrustLevel.COMMUNITY)

        # No policy — allow if tool is BUILTIN, otherwise require default gate
        if policy is None:
            if tool.requires_approval:
                return GatingDecision(
                    allowed=False,
                    reason=f"Tool '{tool_name}' requires approval, no policy for agent '{agent_id}'",
                    requires_approval=True,
                )
            return GatingDecision(allowed=True, reason="no_policy_default_allow")

        # Explicit deny list
        if tool_name in policy.denied_tools:
            return GatingDecision(
                allowed=False,
                reason=f"Tool '{tool_name}' explicitly denied for agent '{agent_id}'",
            )

        # Explicit allow list (if set, tool must be in it)
        if policy.allowed_tools is not None and tool_name not in policy.allowed_tools:
            return GatingDecision(
                allowed=False,
                reason=f"Tool '{tool_name}' not in allowed list for agent '{agent_id}'",
            )

        # Trust level check
        if tool.trust_level < policy.min_trust_level:
            return GatingDecision(
                allowed=False,
                reason=f"Tool trust {tool.trust_level.name} < agent minimum {policy.min_trust_level.name}",
            )

        # Iteration limit
        if iteration > policy.max_iterations:
            return GatingDecision(
                allowed=False,
                reason=f"Iteration {iteration} exceeds limit {policy.max_iterations}",
            )

        # Approval check
        needs_approval = tool.requires_approval or not policy.auto_approve
        if needs_approval:
            return GatingDecision(
                allowed=False,
                reason=f"Tool '{tool_name}' requires human approval",
                requires_approval=True,
            )

        return GatingDecision(allowed=True, reason="allowed")

    # ------------------------------------------------------------------
    # Bulk operations
    # ------------------------------------------------------------------

    def register_builtin_tools(self, tool_names: list[str]) -> None:
        """Register multiple tools at BUILTIN trust."""
        for name in tool_names:
            self.register_tool(ToolTrustEntry(
                tool_name=name, trust_level=TrustLevel.BUILTIN,
            ))

    def list_tools_for_agent(self, agent_id: str) -> list[str]:
        """List all tools available to a specific agent."""
        result = []
        for tool_name in self._tools:
            decision = self.check(agent_id, tool_name)
            if decision.allowed:
                result.append(tool_name)
        return result
