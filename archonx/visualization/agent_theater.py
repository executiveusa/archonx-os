"""
Agent Theater — "Watch Agent in Action"
========================================
Live-streamable visualization of agents working.
Users pay tokens to watch agents solve problems in real-time.

Features:
- Real-time agent activity stream (which agent, what action, result)
- Chess board visualization of crew positions
- Flywheel metrics overlay
- Session recording for replay
- Token-gated access (billing integration)
"""

from __future__ import annotations

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("archonx.visualization.agent_theater")


@dataclass
class TheaterEvent:
    """A single event in the agent theater stream."""
    timestamp: float
    event_type: str       # agent_action | crew_decision | skill_execution | tool_call | flywheel | match
    agent_id: str
    agent_name: str
    description: str
    data: dict[str, Any] = field(default_factory=dict)
    crew: str = ""


@dataclass
class TheaterSession:
    """A theater viewing session."""
    session_id: str
    viewer_id: str
    started_at: float = field(default_factory=time.time)
    tokens_spent: int = 0
    events_watched: int = 0
    active: bool = True


class AgentTheater:
    """
    Live visualization engine for watching agents work.

    Publishers (kernel, crews, skills) emit events.
    Viewers subscribe to the event stream and pay tokens.
    """

    TOKEN_COST_PER_MINUTE = 10  # tokens per minute of viewing

    def __init__(self) -> None:
        self._event_log: deque[TheaterEvent] = deque(maxlen=10000)
        self._sessions: dict[str, TheaterSession] = {}
        self._subscribers: list[Any] = []  # WebSocket connections
        self._counter = 0

    # ------------------------------------------------------------------
    # Publishing (called by kernel/crews/skills)
    # ------------------------------------------------------------------

    def emit(
        self,
        event_type: str,
        agent_id: str,
        agent_name: str,
        description: str,
        data: dict[str, Any] | None = None,
        crew: str = "",
    ) -> TheaterEvent:
        """Publish an event to the theater stream."""
        event = TheaterEvent(
            timestamp=time.time(),
            event_type=event_type,
            agent_id=agent_id,
            agent_name=agent_name,
            description=description,
            data=data or {},
            crew=crew,
        )
        self._event_log.append(event)
        # In production: push to all WebSocket subscribers
        return event

    # ------------------------------------------------------------------
    # Viewing sessions
    # ------------------------------------------------------------------

    def start_session(self, viewer_id: str) -> TheaterSession:
        """Start a new theater viewing session."""
        self._counter += 1
        session = TheaterSession(
            session_id=f"theater-{self._counter:05d}",
            viewer_id=viewer_id,
        )
        self._sessions[session.session_id] = session
        logger.info("Theater session started: %s for viewer %s", session.session_id, viewer_id)
        return session

    def end_session(self, session_id: str) -> TheaterSession | None:
        """End a viewing session and calculate final cost."""
        session = self._sessions.get(session_id)
        if not session:
            return None
        session.active = False
        duration_minutes = (time.time() - session.started_at) / 60
        session.tokens_spent = int(duration_minutes * self.TOKEN_COST_PER_MINUTE)
        logger.info(
            "Theater session ended: %s — %.1f min, %d tokens",
            session_id, duration_minutes, session.tokens_spent,
        )
        return session

    def get_recent_events(self, limit: int = 50) -> list[TheaterEvent]:
        """Get recent theater events."""
        events = list(self._event_log)
        return events[-limit:]

    def get_session_events(self, session_id: str, since: float = 0.0) -> list[TheaterEvent]:
        """Get events that occurred during a session."""
        session = self._sessions.get(session_id)
        if not session:
            return []
        return [e for e in self._event_log if e.timestamp >= max(session.started_at, since)]

    @property
    def stats(self) -> dict[str, Any]:
        active = [s for s in self._sessions.values() if s.active]
        return {
            "total_events": len(self._event_log),
            "active_sessions": len(active),
            "total_sessions": len(self._sessions),
            "total_tokens_earned": sum(s.tokens_spent for s in self._sessions.values()),
        }
