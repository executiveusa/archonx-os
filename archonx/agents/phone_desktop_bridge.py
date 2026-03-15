"""Phone-originated desktop control planning through Archon governance."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from archonx.agents.archon_x_router import ArchonXRouter
from archonx.orchestration.dispatch import DispatchCoordinator
from archonx.orchestration.graph_spec import (
    IntentGraphSpec,
    build_intent_graph_from_dispatch,
)


@dataclass
class RemoteDesktopControlPlan:
    """Governed remote desktop plan triggered from the phone layer."""

    bead_id: str
    persona_id: str
    source: str
    caller_number: str | None
    approval_state: str
    dispatch_decision: dict[str, Any]
    graph_spec: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "bead_id": self.bead_id,
            "persona_id": self.persona_id,
            "source": self.source,
            "caller_number": self.caller_number,
            "approval_state": self.approval_state,
            "dispatch_decision": self.dispatch_decision,
            "graph_spec": self.graph_spec,
        }


class PhoneDesktopBridge:
    """Routes phone-originated remote desktop actions into Archon dispatch."""

    def __init__(
        self,
        dispatch_coordinator: DispatchCoordinator,
        persona_router: ArchonXRouter | None = None,
    ) -> None:
        self.dispatch_coordinator = dispatch_coordinator
        self.persona_router = persona_router or ArchonXRouter()

    def plan_remote_desktop_action(
        self,
        command_text: str,
        repo_ids: list[int],
        bead_id: str,
        caller_number: str | None = None,
        source: str = "phone",
        persona_override: str | None = None,
    ) -> RemoteDesktopControlPlan:
        """Create a governed remote desktop action plan from a phone request."""

        if not bead_id:
            raise ValueError("bead_id is required for remote desktop control")
        persona_id = self.persona_router.select_persona(
            env_override=persona_override,
            text=command_text,
        )
        decision = self.dispatch_coordinator.create_dispatch_decision(
            repo_ids=repo_ids,
            task_name=f"remote_desktop:{bead_id}",
            task_intent="desktop_action",
            objective=command_text,
        )
        graph = build_intent_graph_from_dispatch(decision, source=source)
        approval_state = (
            "awaiting_approval"
            if decision.policy.get("approval_integrations")
            else "ready"
        )
        return RemoteDesktopControlPlan(
            bead_id=bead_id,
            persona_id=persona_id,
            source=source,
            caller_number=caller_number,
            approval_state=approval_state,
            dispatch_decision=decision.to_dict(),
            graph_spec=graph.to_dict(),
        )
