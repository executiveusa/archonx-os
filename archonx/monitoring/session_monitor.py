"""
Session Monitoring and Event Streaming

Real-time monitoring of agent execution sessions with structured event logging,
artifact persistence, and WebSocket streaming capabilities.

ZTE-20260308-0004: Session monitoring infrastructure
"""

import json
import logging
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Session event types"""
    SESSION_CREATED = "session_created"
    SESSION_STARTED = "session_started"
    TASK_RECEIVED = "task_received"
    TOOL_SELECTED = "tool_selected"
    BROWSER_ACTION = "browser_action"
    DESKTOP_ACTION = "desktop_action"
    SCREENSHOT = "screenshot"
    PROMPT_SENT = "prompt_sent"
    RESULT_RECEIVED = "result_received"
    ERROR_RAISED = "error_raised"
    ARTIFACT_CREATED = "artifact_created"
    VIDEO_RENDER_REQUESTED = "video_render_requested"
    SESSION_COMPLETED = "session_completed"
    SESSION_CLOSED = "session_closed"


@dataclass
class SessionEvent:
    """Single session event"""
    event_id: str
    session_id: str
    event_type: EventType
    timestamp: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        d = asdict(self)
        d['event_type'] = self.event_type.value
        if d['metadata'] is None:
            d['metadata'] = {}
        return d


class SessionMonitor:
    """Monitor and stream session events"""

    def __init__(self, max_events_per_session: int = 10000):
        """Initialize session monitor"""
        self.events: Dict[str, List[SessionEvent]] = {}
        self.event_listeners: Dict[str, List[Callable]] = {}
        self.max_events_per_session = max_events_per_session
        self._event_counter = 0

    async def log_event(
        self,
        session_id: str,
        event_type: EventType,
        data: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> SessionEvent:
        """Log a session event"""
        self._event_counter += 1
        now = datetime.now().isoformat()

        event = SessionEvent(
            event_id=f"evt-{self._event_counter}",
            session_id=session_id,
            event_type=event_type,
            timestamp=now,
            data=data or {},
            metadata=metadata or {}
        )

        # Store event
        if session_id not in self.events:
            self.events[session_id] = []

        self.events[session_id].append(event)

        # Trim old events if exceeding limit
        if len(self.events[session_id]) > self.max_events_per_session:
            self.events[session_id] = self.events[session_id][-self.max_events_per_session:]

        # Notify listeners
        await self._notify_listeners(session_id, event)

        logger.debug(f"Event logged: {event.event_id} - {event_type.value}")
        return event

    async def subscribe(self, session_id: str, callback: Callable) -> str:
        """Subscribe to session events"""
        if session_id not in self.event_listeners:
            self.event_listeners[session_id] = []

        self.event_listeners[session_id].append(callback)
        listener_id = f"listener-{len(self.event_listeners[session_id])}"
        logger.info(f"Listener {listener_id} subscribed to {session_id}")
        return listener_id

    async def unsubscribe(self, session_id: str, listener_id: str) -> bool:
        """Unsubscribe from events"""
        if session_id not in self.event_listeners:
            return False

        try:
            self.event_listeners[session_id] = [
                l for l in self.event_listeners[session_id]
                if id(l) != int(listener_id.split('-')[1])
            ]
            return True
        except:
            return False

    async def _notify_listeners(self, session_id: str, event: SessionEvent):
        """Notify all listeners of event"""
        if session_id in self.event_listeners:
            for callback in self.event_listeners[session_id]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    logger.error(f"Listener error: {e}")

    def get_events(
        self,
        session_id: str,
        event_type: Optional[EventType] = None,
        limit: int = 100
    ) -> List[SessionEvent]:
        """Get events for session"""
        if session_id not in self.events:
            return []

        events = self.events[session_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return events[-limit:]

    def get_event_count(self, session_id: str) -> int:
        """Get event count for session"""
        return len(self.events.get(session_id, []))

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get session event summary"""
        events = self.events.get(session_id, [])

        if not events:
            return {"session_id": session_id, "event_count": 0}

        first_event = events[0]
        last_event = events[-1]

        event_types = {}
        for event in events:
            event_types[event.event_type.value] = event_types.get(event.event_type.value, 0) + 1

        return {
            "session_id": session_id,
            "event_count": len(events),
            "first_event": first_event.timestamp,
            "last_event": last_event.timestamp,
            "event_types": event_types,
            "duration_seconds": self._calculate_duration(first_event, last_event)
        }

    @staticmethod
    def _calculate_duration(first: SessionEvent, last: SessionEvent) -> float:
        """Calculate session duration in seconds"""
        try:
            first_dt = datetime.fromisoformat(first.timestamp)
            last_dt = datetime.fromisoformat(last.timestamp)
            return (last_dt - first_dt).total_seconds()
        except:
            return 0.0

    async def export_events(self, session_id: str, format: str = "json") -> Optional[str]:
        """Export session events"""
        events = self.events.get(session_id, [])

        if not events:
            return None

        if format == "json":
            return json.dumps([e.to_dict() for e in events], indent=2)
        elif format == "jsonl":
            return "\n".join(json.dumps(e.to_dict()) for e in events)
        else:
            return None

    def clear_session(self, session_id: str) -> bool:
        """Clear session events"""
        if session_id in self.events:
            del self.events[session_id]
        if session_id in self.event_listeners:
            del self.event_listeners[session_id]
        return True


# Global monitor instance
_monitor_instance: Optional[SessionMonitor] = None


def get_monitor() -> SessionMonitor:
    """Get or create global monitor"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = SessionMonitor()
    return _monitor_instance
