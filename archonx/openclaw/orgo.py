"""
Orgo Integration
================
Orgo (https://docs.orgo.ai) is the default computer-use agent platform.

Orgo provides:
- VM provisioning for browser automation
- Built-in computer-use agent infrastructure
- Session management and screenshots
- API for launching tasks on real browsers

This module wraps the Orgo API as both a channel (for OpenClaw) and
a tool (for agent task execution).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("archonx.openclaw.orgo")


@dataclass
class OrgoSession:
    """Represents an active Orgo VM session."""
    session_id: str
    status: str = "pending"  # pending | active | completed | failed
    vm_url: str = ""
    screenshots: list[str] = field(default_factory=list)
    actions_taken: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class OrgoClient:
    """
    Client for the Orgo computer-use API.

    In production, this makes real HTTP calls to Orgo's API.
    Currently provides the interface contract for integration.
    """

    def __init__(self, api_key: str = "", base_url: str = "https://api.orgo.ai") -> None:
        self.api_key = api_key
        self.base_url = base_url
        self._sessions: dict[str, OrgoSession] = {}
        self._counter = 0

    async def create_session(self, task: str, config: dict[str, Any] | None = None) -> OrgoSession:
        """Launch a new Orgo VM session for a computer-use task."""
        self._counter += 1
        session = OrgoSession(
            session_id=f"orgo-{self._counter:05d}",
            status="active",
            vm_url=f"{self.base_url}/sessions/orgo-{self._counter:05d}",
            metadata={"task": task, "config": config or {}},
        )
        self._sessions[session.session_id] = session
        logger.info("Orgo session created: %s for task: %s", session.session_id, task[:80])
        return session

    async def execute_action(self, session_id: str, action: dict[str, Any]) -> dict[str, Any]:
        """Execute a browser action in an Orgo session."""
        session = self._sessions.get(session_id)
        if not session:
            return {"error": f"Session {session_id} not found"}

        session.actions_taken += 1
        action_type = action.get("type", "unknown")
        logger.info("Orgo action [%s]: %s", session_id, action_type)

        # In production: POST to Orgo API
        return {
            "session_id": session_id,
            "action": action_type,
            "status": "completed",
            "screenshot": f"screenshot_{session.actions_taken}.png",
        }

    async def get_screenshot(self, session_id: str) -> str:
        """Get the latest screenshot from an Orgo session."""
        session = self._sessions.get(session_id)
        if not session:
            return ""
        return f"{self.base_url}/screenshots/{session_id}/latest.png"

    async def close_session(self, session_id: str) -> None:
        """Close an Orgo VM session."""
        session = self._sessions.get(session_id)
        if session:
            session.status = "completed"
            logger.info("Orgo session closed: %s (%d actions)", session_id, session.actions_taken)

    @property
    def active_sessions(self) -> list[OrgoSession]:
        return [s for s in self._sessions.values() if s.status == "active"]
