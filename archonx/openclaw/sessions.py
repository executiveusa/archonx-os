"""
Session Management
==================
Per-client session isolation for multi-tenant operation.
Each client gets their own ArchonX instance with isolated state.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("archonx.openclaw.sessions")


@dataclass
class ClientSession:
    """An isolated session for a single client."""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str = ""
    client_name: str = ""
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)
    active: bool = True

    # Crew assignment (which crew handles this client's requests)
    primary_crew: str = "white"

    # Per-session agent state overrides
    agent_overrides: dict[str, Any] = field(default_factory=dict)


class SessionManager:
    """
    Manages client sessions with full multi-tenant isolation.

    In production, sessions are persisted to Redis/PostgreSQL
    and include auth tokens, rate limits, and billing info.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, ClientSession] = {}

    def create_session(
        self,
        client_id: str,
        client_name: str = "",
        **kwargs: Any,
    ) -> ClientSession:
        session = ClientSession(
            client_id=client_id,
            client_name=client_name or client_id,
            metadata=kwargs,
        )
        self._sessions[session.session_id] = session
        logger.info(
            "Session created: %s for client %s", session.session_id[:8], client_id
        )
        return session

    def get_session(self, session_id: str) -> ClientSession | None:
        return self._sessions.get(session_id)

    def get_by_client(self, client_id: str) -> list[ClientSession]:
        return [s for s in self._sessions.values() if s.client_id == client_id and s.active]

    def close_session(self, session_id: str) -> None:
        session = self._sessions.get(session_id)
        if session:
            session.active = False
            logger.info("Session closed: %s", session_id[:8])

    @property
    def active_count(self) -> int:
        return sum(1 for s in self._sessions.values() if s.active)
