"""
Brenner Protocol
================
Structured handshake protocol for agent-to-agent collaboration.

Named after BrennerBot patterns — ensures agents have a clean contract
for requesting help, sharing context, and confirming completion.

The protocol enforces:
1. Capability declaration (what can this agent do?)
2. Context sharing (what does the helper need to know?)
3. Acceptance/rejection (can the helper actually help?)
4. Result handoff (structured return with quality metadata)
5. Flywheel feedback (improvements from the collaboration itself)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger("archonx.core.brenner_protocol")


class HandshakePhase(str, Enum):
    CAPABILITY_CHECK = "capability_check"
    CONTEXT_SHARE = "context_share"
    ACCEPTANCE = "acceptance"
    EXECUTION = "execution"
    HANDOFF = "handoff"
    FEEDBACK = "feedback"


@dataclass
class Capability:
    """What an agent can do."""
    agent_id: str
    skills: list[str]
    tools: list[str]
    specialties: list[str]
    current_load: float = 0.0  # 0.0 = idle, 1.0 = max capacity


@dataclass
class CollaborationRequest:
    """A structured request from one agent to another."""
    id: str
    requester: str         # agent_id
    helper: str            # agent_id
    task: dict[str, Any]
    context: dict[str, Any] = field(default_factory=dict)
    phase: HandshakePhase = HandshakePhase.CAPABILITY_CHECK
    accepted: bool = False
    result: dict[str, Any] | None = None
    improvements: list[dict[str, Any]] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    completed_at: float | None = None


class BrennerProtocol:
    """
    Manages structured agent-to-agent collaboration handshakes.

    Usage:
        proto = BrennerProtocol()
        req = proto.initiate("agent_a", "agent_b", task, context)
        cap = proto.check_capability("agent_b", skills=["web_scraping"])
        if cap:
            req = proto.accept(req)
            result = await do_work(req.task)
            req = proto.handoff(req, result)
            proto.feedback(req, improvements=[...])
    """

    def __init__(self) -> None:
        self._requests: dict[str, CollaborationRequest] = {}
        self._capabilities: dict[str, Capability] = {}
        self._counter = 0

    def register_capability(self, agent_id: str, skills: list[str], tools: list[str], specialties: list[str]) -> None:
        """Register what an agent can do."""
        self._capabilities[agent_id] = Capability(
            agent_id=agent_id,
            skills=skills,
            tools=tools,
            specialties=specialties,
        )

    def check_capability(self, agent_id: str, skills: list[str] | None = None, tools: list[str] | None = None) -> bool:
        """Check if an agent has the required capabilities."""
        cap = self._capabilities.get(agent_id)
        if not cap:
            return False
        if skills and not set(skills).intersection(cap.skills):
            return False
        if tools and not set(tools).intersection(cap.tools):
            return False
        return True

    def initiate(
        self,
        requester: str,
        helper: str,
        task: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> CollaborationRequest:
        """Start a collaboration handshake."""
        self._counter += 1
        req = CollaborationRequest(
            id=f"collab-{self._counter:05d}",
            requester=requester,
            helper=helper,
            task=task,
            context=context or {},
            phase=HandshakePhase.CAPABILITY_CHECK,
        )
        self._requests[req.id] = req
        logger.info("Brenner: %s → %s initiated [%s]", requester, helper, req.id)
        return req

    def accept(self, req: CollaborationRequest) -> CollaborationRequest:
        """Helper accepts the collaboration."""
        req.accepted = True
        req.phase = HandshakePhase.EXECUTION
        logger.info("Brenner: %s accepted by %s", req.id, req.helper)
        return req

    def reject(self, req: CollaborationRequest, reason: str = "") -> CollaborationRequest:
        """Helper rejects the collaboration."""
        req.accepted = False
        req.phase = HandshakePhase.HANDOFF
        req.result = {"status": "rejected", "reason": reason}
        req.completed_at = time.time()
        logger.info("Brenner: %s rejected by %s — %s", req.id, req.helper, reason)
        return req

    def handoff(self, req: CollaborationRequest, result: dict[str, Any]) -> CollaborationRequest:
        """Helper hands off the completed result."""
        req.result = result
        req.phase = HandshakePhase.HANDOFF
        req.completed_at = time.time()
        logger.info("Brenner: %s handoff complete", req.id)
        return req

    def feedback(self, req: CollaborationRequest, improvements: list[dict[str, Any]]) -> CollaborationRequest:
        """Record flywheel improvements from the collaboration."""
        req.improvements = improvements
        req.phase = HandshakePhase.FEEDBACK
        logger.info("Brenner: %s feedback — %d improvements", req.id, len(improvements))
        return req

    def find_best_helper(self, required_skills: list[str]) -> str | None:
        """Find the best available agent for a set of required skills."""
        best_agent = None
        best_overlap = 0
        for agent_id, cap in self._capabilities.items():
            overlap = len(set(required_skills).intersection(cap.skills))
            if overlap > best_overlap and cap.current_load < 0.8:
                best_overlap = overlap
                best_agent = agent_id
        return best_agent

    @property
    def stats(self) -> dict[str, Any]:
        total = len(self._requests)
        completed = len([r for r in self._requests.values() if r.completed_at])
        accepted = len([r for r in self._requests.values() if r.accepted])
        return {
            "total_collaborations": total,
            "completed": completed,
            "accepted": accepted,
            "rejection_rate": (total - accepted) / max(total, 1),
            "registered_agents": len(self._capabilities),
        }
