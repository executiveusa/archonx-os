"""
Session Manager
===============
Session management for ArchonX ecosystem.

Provides:
- User session tracking
- Cross-service session sharing
- Session expiration and cleanup
- Activity tracking
"""

from __future__ import annotations

import json
import logging
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("archonx.auth.session")


@dataclass
class User:
    """User information."""
    user_id: str
    email: str
    name: str
    roles: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "name": self.name,
            "roles": self.roles,
            "metadata": self.metadata,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> User:
        return cls(
            user_id=data["user_id"],
            email=data["email"],
            name=data["name"],
            roles=data.get("roles", []),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", datetime.now(timezone.UTC).isoformat())
        )


@dataclass
class Session:
    """User session."""
    session_id: str
    user: User
    access_token: str
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    expires_at: float = 0.0
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    services: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.expires_at == 0.0:
            self.expires_at = self.created_at + 86400  # 24 hours

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def touch(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user": self.user.to_dict(),
            "access_token": self.access_token,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "expires_at": self.expires_at,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "services": self.services
        }


class SessionManager:
    """
    Session manager for ArchonX ecosystem.
    
    Features:
    - User session tracking
    - Cross-service session sharing
    - Session expiration and cleanup
    - Activity tracking
    
    Usage:
        manager = SessionManager()
        
        # Create session
        session = manager.create_session(user, access_token)
        
        # Validate session
        session = manager.get_session(session_id)
        
        # End session
        manager.end_session(session_id)
    """

    def __init__(
        self,
        session_lifetime: int = 86400,  # 24 hours
        max_sessions_per_user: int = 5,
        sessions_file: Optional[Path] = None
    ):
        """
        Initialize session manager.
        
        Args:
            session_lifetime: Session lifetime in seconds
            max_sessions_per_user: Maximum concurrent sessions per user
            sessions_file: File to persist sessions
        """
        self.session_lifetime = session_lifetime
        self.max_sessions_per_user = max_sessions_per_user
        
        # Storage
        self.sessions_file = sessions_file or Path.home() / ".archonx" / "sessions.json"
        self.sessions_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._sessions: dict[str, Session] = {}
        self._user_sessions: dict[str, list[str]] = {}  # user_id -> [session_ids]
        
        # Load sessions
        self._load_sessions()
        
        logger.info(f"Session manager initialized (lifetime: {session_lifetime}s)")

    def _load_sessions(self) -> None:
        """Load sessions from file."""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for session_data in data.get("sessions", []):
                        user = User.from_dict(session_data["user"])
                        session = Session(
                            session_id=session_data["session_id"],
                            user=user,
                            access_token=session_data["access_token"],
                            created_at=session_data.get("created_at", time.time()),
                            last_activity=session_data.get("last_activity", time.time()),
                            expires_at=session_data.get("expires_at", time.time() + 86400),
                            ip_address=session_data.get("ip_address"),
                            user_agent=session_data.get("user_agent"),
                            services=session_data.get("services", [])
                        )
                        
                        # Skip expired sessions
                        if not session.is_expired():
                            self._sessions[session.session_id] = session
                            
                            if user.user_id not in self._user_sessions:
                                self._user_sessions[user.user_id] = []
                            self._user_sessions[user.user_id].append(session.session_id)
                
                logger.info(f"Loaded {len(self._sessions)} sessions")
            except Exception as e:
                logger.warning(f"Failed to load sessions: {e}")

    def _save_sessions(self) -> None:
        """Save sessions to file."""
        data = {
            "sessions": [s.to_dict() for s in self._sessions.values()]
        }
        with open(self.sessions_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def create_session(
        self,
        user: User,
        access_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        services: Optional[list[str]] = None
    ) -> Session:
        """
        Create a new session.
        
        Args:
            user: The user
            access_token: OAuth access token
            ip_address: Client IP address
            user_agent: Client user agent
            services: Services this session is valid for
            
        Returns:
            The created Session
        """
        # Check max sessions per user
        user_session_ids = self._user_sessions.get(user.user_id, [])
        if len(user_session_ids) >= self.max_sessions_per_user:
            # Remove oldest session
            oldest_id = user_session_ids[0]
            self.end_session(oldest_id)
        
        session_id = secrets.token_urlsafe(32)
        
        session = Session(
            session_id=session_id,
            user=user,
            access_token=access_token,
            ip_address=ip_address,
            user_agent=user_agent,
            services=services or ["all"],
            expires_at=time.time() + self.session_lifetime
        )
        
        self._sessions[session_id] = session
        
        if user.user_id not in self._user_sessions:
            self._user_sessions[user.user_id] = []
        self._user_sessions[user.user_id].append(session_id)
        
        self._save_sessions()
        
        logger.info(f"Created session {session_id[:8]}... for user {user.user_id}")
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get a session by ID.
        
        Args:
            session_id: The session ID
            
        Returns:
            Session if valid, None otherwise
        """
        session = self._sessions.get(session_id)
        
        if not session:
            return None
        
        if session.is_expired():
            self.end_session(session_id)
            return None
        
        # Update activity
        session.touch()
        
        return session

    def get_session_by_token(self, access_token: str) -> Optional[Session]:
        """
        Get a session by access token.
        
        Args:
            access_token: The access token
            
        Returns:
            Session if found, None otherwise
        """
        for session in self._sessions.values():
            if session.access_token == access_token:
                if not session.is_expired():
                    session.touch()
                    return session
                else:
                    self.end_session(session.session_id)
        
        return None

    def get_user_sessions(self, user_id: str) -> list[Session]:
        """
        Get all sessions for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            List of active sessions
        """
        session_ids = self._user_sessions.get(user_id, [])
        sessions = []
        
        for session_id in session_ids[:]:
            session = self._sessions.get(session_id)
            if session and not session.is_expired():
                sessions.append(session)
            elif session:
                self.end_session(session_id)
        
        return sessions

    def end_session(self, session_id: str) -> bool:
        """
        End a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            True if ended, False if not found
        """
        session = self._sessions.pop(session_id, None)
        
        if not session:
            return False
        
        # Remove from user sessions
        user_id = session.user.user_id
        if user_id in self._user_sessions:
            try:
                self._user_sessions[user_id].remove(session_id)
            except ValueError:
                pass
        
        self._save_sessions()
        
        logger.info(f"Ended session {session_id[:8]}...")
        return True

    def end_user_sessions(self, user_id: str) -> int:
        """
        End all sessions for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            Number of sessions ended
        """
        session_ids = self._user_sessions.get(user_id, [])[:]
        count = 0
        
        for session_id in session_ids:
            if self.end_session(session_id):
                count += 1
        
        return count

    def add_service(self, session_id: str, service: str) -> bool:
        """
        Add a service to a session.
        
        Args:
            session_id: The session ID
            service: Service name
            
        Returns:
            True if added, False if session not found
        """
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        if service not in session.services:
            session.services.append(service)
            self._save_sessions()
        
        return True

    def validate_service(self, session_id: str, service: str) -> bool:
        """
        Validate that a session has access to a service.
        
        Args:
            session_id: The session ID
            service: Service name
            
        Returns:
            True if valid, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        return "all" in session.services or service in session.services

    def cleanup_expired(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        expired_ids = [
            sid for sid, session in self._sessions.items()
            if session.is_expired()
        ]
        
        for session_id in expired_ids:
            self.end_session(session_id)
        
        if expired_ids:
            logger.info(f"Cleaned up {len(expired_ids)} expired sessions")
        
        return len(expired_ids)

    def get_stats(self) -> dict[str, Any]:
        """
        Get session statistics.
        
        Returns:
            Dictionary with stats
        """
        return {
            "total_sessions": len(self._sessions),
            "unique_users": len(self._user_sessions),
            "sessions_per_user": {
                user_id: len(sessions)
                for user_id, sessions in self._user_sessions.items()
            }
        }


# Singleton instance
_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get the singleton SessionManager."""
    global _manager
    if _manager is None:
        _manager = SessionManager()
    return _manager
