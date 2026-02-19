"""
Canonical Agent Log System
==========================
Thread-safe JSONL logging for all agent activities.
Provides oversight, debugging, and audit trail for the 64-agent swarm.

Usage:
    from archonx.logs.canonical_log import get_logger

    logger = get_logger()
    logger.log_agent_start("agent_001", "search", {"query": "test"})
    logger.log_tool_use("agent_001", "web_scraping", "Scrape example.com", True)
    logger.log_task_complete("agent_001", "search", {"results": 10})
"""

from __future__ import annotations

import json
import logging
import os
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger("archonx.logs")


class EventType(str, Enum):
    """Canonical event types for agent logging."""
    # Agent lifecycle
    AGENT_START = "AGENT_START"
    AGENT_STOP = "AGENT_STOP"
    AGENT_ERROR = "AGENT_ERROR"

    # Task execution
    TASK_START = "TASK_START"
    TASK_COMPLETE = "TASK_COMPLETE"
    TASK_FAILED = "TASK_FAILED"

    # Tool usage
    TOOL_USE = "TOOL_USE"
    TOOL_ERROR = "TOOL_ERROR"

    # Skill execution
    SKILL_EXECUTE = "SKILL_EXECUTE"
    SKILL_COMPLETE = "SKILL_COMPLETE"

    # Communication
    MESSAGE_SEND = "MESSAGE_SEND"
    MESSAGE_RECEIVE = "MESSAGE_RECEIVE"

    # Wave orchestration
    WAVE_START = "WAVE_START"
    WAVE_COMPLETE = "WAVE_COMPLETE"

    # Decision making
    DECISION = "DECISION"
    DELEGATION = "DELEGATION"

    # Memory operations
    MEMORY_STORE = "MEMORY_STORE"
    MEMORY_RETRIEVE = "MEMORY_RETRIEVE"

    # System events
    SYSTEM = "SYSTEM"
    HEARTBEAT = "HEARTBEAT"


@dataclass
class LogEvent:
    """Canonical log event structure."""
    timestamp: str
    event_type: EventType
    agent_id: str
    session_id: str
    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps({
            "timestamp": self.timestamp,
            "event_type": self.event_type.value,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "data": self.data,
            "metadata": self.metadata,
        })

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type.value,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "data": self.data,
            "metadata": self.metadata,
        }


class CanonicalLogger:
    """
    Thread-safe singleton logger for all agent activities.

    Features:
    - JSONL format for easy parsing
    - Thread-safe writes
    - Session tracking
    - Automatic timestamps
    - Event type validation
    """

    _instance: "CanonicalLogger | None" = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs) -> "CanonicalLogger":
        """Singleton pattern with thread safety."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        log_dir: str | None = None,
        session_id: str | None = None,
        enabled: bool = True
    ):
        """Initialize the canonical logger."""
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.enabled = enabled
        self.log_dir = Path(log_dir or os.environ.get("ARCHONX_LOG_DIR", "logs"))
        self.session_id = session_id or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self._file_lock = threading.Lock()
        self._initialized = True

        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Open log file
        self.log_file = self.log_dir / f"agents_{self.session_id}.jsonl"

        logger.info("Canonical logger initialized: %s", self.log_file)

    def _write_event(self, event: LogEvent) -> None:
        """Write an event to the log file (thread-safe)."""
        if not self.enabled:
            return

        with self._file_lock:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(event.to_json() + "\n")
            except Exception as e:
                logger.error("Failed to write log event: %s", e)

    def log(
        self,
        event_type: EventType,
        agent_id: str,
        data: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        session_id: str | None = None
    ) -> LogEvent:
        """
        Log a canonical event.

        Args:
            event_type: Type of event from EventType enum
            agent_id: ID of the agent generating the event
            data: Event-specific data
            metadata: Additional metadata
            session_id: Optional session ID (uses default if not provided)

        Returns:
            The created LogEvent
        """
        event = LogEvent(
            timestamp=datetime.utcnow().isoformat() + "Z",
            event_type=event_type,
            agent_id=agent_id,
            session_id=session_id or self.session_id,
            data=data or {},
            metadata=metadata or {},
        )

        self._write_event(event)
        return event

    # Convenience methods for common event types

    def log_agent_start(
        self,
        agent_id: str,
        task_type: str,
        params: dict[str, Any],
        session_id: str | None = None
    ) -> LogEvent:
        """Log agent start event."""
        return self.log(
            EventType.AGENT_START,
            agent_id,
            {"task_type": task_type, "params": params},
            session_id=session_id
        )

    def log_agent_stop(
        self,
        agent_id: str,
        reason: str = "completed",
        session_id: str | None = None
    ) -> LogEvent:
        """Log agent stop event."""
        return self.log(
            EventType.AGENT_STOP,
            agent_id,
            {"reason": reason},
            session_id=session_id
        )

    def log_agent_error(
        self,
        agent_id: str,
        error: str,
        stack_trace: str | None = None,
        session_id: str | None = None
    ) -> LogEvent:
        """Log agent error event."""
        data = {"error": error}
        if stack_trace:
            data["stack_trace"] = stack_trace
        return self.log(EventType.AGENT_ERROR, agent_id, data, session_id=session_id)

    def log_task_start(
        self,
        agent_id: str,
        task_id: str,
        task_type: str,
        session_id: str | None = None
    ) -> LogEvent:
        """Log task start event."""
        return self.log(
            EventType.TASK_START,
            agent_id,
            {"task_id": task_id, "task_type": task_type},
            session_id=session_id
        )

    def log_task_complete(
        self,
        agent_id: str,
        task_id: str,
        result: dict[str, Any],
        duration_ms: int | None = None,
        session_id: str | None = None
    ) -> LogEvent:
        """Log task complete event."""
        data = {"task_id": task_id, "result": result}
        if duration_ms is not None:
            data["duration_ms"] = duration_ms
        return self.log(EventType.TASK_COMPLETE, agent_id, data, session_id=session_id)

    def log_task_failed(
        self,
        agent_id: str,
        task_id: str,
        error: str,
        session_id: str | None = None
    ) -> LogEvent:
        """Log task failed event."""
        return self.log(
            EventType.TASK_FAILED,
            agent_id,
            {"task_id": task_id, "error": error},
            session_id=session_id
        )

    def log_tool_use(
        self,
        agent_id: str,
        tool: str,
        purpose: str,
        success: bool = True,
        duration_ms: int = 0,
        session_id: str | None = None
    ) -> LogEvent:
        """Log tool usage event."""
        return self.log(
            EventType.TOOL_USE,
            agent_id,
            {
                "tool": tool,
                "purpose": purpose,
                "success": success,
                "duration_ms": duration_ms,
            },
            session_id=session_id
        )

    def log_tool_error(
        self,
        agent_id: str,
        tool: str,
        error: str,
        session_id: str | None = None
    ) -> LogEvent:
        """Log tool error event."""
        return self.log(
            EventType.TOOL_ERROR,
            agent_id,
            {"tool": tool, "error": error},
            session_id=session_id
        )

    def log_skill_execute(
        self,
        agent_id: str,
        skill_name: str,
        params: dict[str, Any],
        session_id: str | None = None
    ) -> LogEvent:
        """Log skill execution event."""
        return self.log(
            EventType.SKILL_EXECUTE,
            agent_id,
            {"skill": skill_name, "params": params},
            session_id=session_id
        )

    def log_skill_complete(
        self,
        agent_id: str,
        skill_name: str,
        status: str,
        duration_ms: int,
        session_id: str | None = None
    ) -> LogEvent:
        """Log skill completion event."""
        return self.log(
            EventType.SKILL_COMPLETE,
            agent_id,
            {"skill": skill_name, "status": status, "duration_ms": duration_ms},
            session_id=session_id
        )

    def log_message_send(
        self,
        agent_id: str,
        recipient_id: str,
        message_type: str,
        session_id: str | None = None
    ) -> LogEvent:
        """Log message send event."""
        return self.log(
            EventType.MESSAGE_SEND,
            agent_id,
            {"recipient": recipient_id, "message_type": message_type},
            session_id=session_id
        )

    def log_message_receive(
        self,
        agent_id: str,
        sender_id: str,
        message_type: str,
        session_id: str | None = None
    ) -> LogEvent:
        """Log message receive event."""
        return self.log(
            EventType.MESSAGE_RECEIVE,
            agent_id,
            {"sender": sender_id, "message_type": message_type},
            session_id=session_id
        )

    def log_wave_start(
        self,
        wave_id: str,
        agent_ids: list[str],
        session_id: str | None = None
    ) -> LogEvent:
        """Log wave start event."""
        return self.log(
            EventType.WAVE_START,
            "orchestrator",
            {"wave_id": wave_id, "agents": agent_ids},
            session_id=session_id
        )

    def log_wave_complete(
        self,
        wave_id: str,
        results: dict[str, Any],
        session_id: str | None = None
    ) -> LogEvent:
        """Log wave complete event."""
        return self.log(
            EventType.WAVE_COMPLETE,
            "orchestrator",
            {"wave_id": wave_id, "results": results},
            session_id=session_id
        )

    def log_decision(
        self,
        agent_id: str,
        decision_type: str,
        choice: str,
        reasoning: str | None = None,
        session_id: str | None = None
    ) -> LogEvent:
        """Log decision event."""
        data = {"decision_type": decision_type, "choice": choice}
        if reasoning:
            data["reasoning"] = reasoning
        return self.log(EventType.DECISION, agent_id, data, session_id=session_id)

    def log_delegation(
        self,
        agent_id: str,
        delegate_id: str,
        task_type: str,
        session_id: str | None = None
    ) -> LogEvent:
        """Log delegation event."""
        return self.log(
            EventType.DELEGATION,
            agent_id,
            {"delegate": delegate_id, "task_type": task_type},
            session_id=session_id
        )

    def log_memory_store(
        self,
        agent_id: str,
        key: str,
        value_type: str,
        session_id: str | None = None
    ) -> LogEvent:
        """Log memory store event."""
        return self.log(
            EventType.MEMORY_STORE,
            agent_id,
            {"key": key, "value_type": value_type},
            session_id=session_id
        )

    def log_memory_retrieve(
        self,
        agent_id: str,
        key: str,
        found: bool,
        session_id: str | None = None
    ) -> LogEvent:
        """Log memory retrieve event."""
        return self.log(
            EventType.MEMORY_RETRIEVE,
            agent_id,
            {"key": key, "found": found},
            session_id=session_id
        )

    def log_system(
        self,
        message: str,
        level: str = "INFO",
        session_id: str | None = None
    ) -> LogEvent:
        """Log system event."""
        return self.log(
            EventType.SYSTEM,
            "system",
            {"message": message, "level": level},
            session_id=session_id
        )

    def log_heartbeat(
        self,
        agent_id: str,
        status: dict[str, Any],
        session_id: str | None = None
    ) -> LogEvent:
        """Log heartbeat event."""
        return self.log(EventType.HEARTBEAT, agent_id, status, session_id=session_id)

    def read_events(
        self,
        event_type: EventType | None = None,
        agent_id: str | None = None,
        limit: int = 100
    ) -> list[LogEvent]:
        """
        Read events from the log file.

        Args:
            event_type: Filter by event type (optional)
            agent_id: Filter by agent ID (optional)
            limit: Maximum number of events to return

        Returns:
            List of LogEvent objects
        """
        events = []

        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        event = LogEvent(
                            timestamp=data["timestamp"],
                            event_type=EventType(data["event_type"]),
                            agent_id=data["agent_id"],
                            session_id=data["session_id"],
                            data=data.get("data", {}),
                            metadata=data.get("metadata", {}),
                        )

                        # Apply filters
                        if event_type and event.event_type != event_type:
                            continue
                        if agent_id and event.agent_id != agent_id:
                            continue

                        events.append(event)

                        if len(events) >= limit:
                            break
                    except (json.JSONDecodeError, KeyError):
                        continue
        except FileNotFoundError:
            pass

        return events

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about logged events."""
        events = self.read_events(limit=10000)

        stats = {
            "total_events": len(events),
            "session_id": self.session_id,
            "log_file": str(self.log_file),
            "event_counts": {},
            "agent_counts": {},
        }

        for event in events:
            # Count by event type
            event_type = event.event_type.value
            stats["event_counts"][event_type] = stats["event_counts"].get(event_type, 0) + 1

            # Count by agent
            stats["agent_counts"][event.agent_id] = stats["agent_counts"].get(event.agent_id, 0) + 1

        return stats


def get_logger(
    log_dir: str | None = None,
    session_id: str | None = None,
    enabled: bool = True
) -> CanonicalLogger:
    """
    Get the singleton CanonicalLogger instance.

    Args:
        log_dir: Directory for log files
        session_id: Session ID for this logging session
        enabled: Whether logging is enabled

    Returns:
        CanonicalLogger instance
    """
    return CanonicalLogger(log_dir=log_dir, session_id=session_id, enabled=enabled)


# Convenience function for quick logging
def log_event(
    event_type: EventType,
    agent_id: str,
    data: dict[str, Any] | None = None
) -> LogEvent:
    """
    Quick logging function for single events.

    Args:
        event_type: Type of event
        agent_id: ID of the agent
        data: Event data

    Returns:
        The created LogEvent
    """
    return get_logger().log(event_type, agent_id, data)
