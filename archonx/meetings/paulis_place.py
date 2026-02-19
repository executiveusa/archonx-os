"""
Pauli's Place - Daily Meeting Schedule
5 daily meetings for strategy, learning, and coordination
"""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum
from typing import Optional

logger = logging.getLogger("archonx.meetings.paulis_place")


class MeetingType(str, Enum):
    MORNING_BRIEFING = "morning_briefing"
    CHESS_MATCH = "chess_match"
    CARD_GAMES = "card_games"
    WAR_ROOM = "war_room"
    EVENING_REVIEW = "evening_review"


@dataclass
class Meeting:
    """A scheduled meeting at Pauli's Place."""
    meeting_type: MeetingType
    time_utc: time
    description: str = ""
    attendees: str = "all"
    agenda: list[str] = field(default_factory=list)


DAILY_SCHEDULE: list[Meeting] = [
    Meeting(MeetingType.MORNING_BRIEFING, time(8, 0), "Morning Briefing", "all", ["Status updates", "Priority tasks", "Blockers"]),
    Meeting(MeetingType.CHESS_MATCH, time(12, 0), "Chess Match", "all", ["White vs Black collaborative reasoning", "Strategy evaluation"]),
    Meeting(MeetingType.CARD_GAMES, time(15, 0), "Card Games", "all", ["Probability training", "Risk assessment drills"]),
    Meeting(MeetingType.WAR_ROOM, time(18, 0), "War Room", "senior", ["Critical issues", "Escalation review", "Tactical decisions"]),
    Meeting(MeetingType.EVENING_REVIEW, time(21, 0), "Evening Review", "all", ["Day summary", "Flywheel metrics", "Tomorrow planning"]),
]

class PaulisPlaceManager:
    """
    Manages the 5 daily meetings at Pauli's Place:
    08:00 UTC - Morning Briefing
    12:00 UTC - Chess Match
    15:00 UTC - Card Games  
    18:00 UTC - War Room
    21:00 UTC - Evening Review
    """
    
    def __init__(self) -> None:
        self.meetings = {
            "morning_briefing": time(8, 0),
            "chess_match": time(12, 0),
            "card_games": time(15, 0),
            "war_room": time(18, 0),
            "evening_review": time(21, 0),
        }
        self._scheduled = False
        logger.info("Pauli's Place initialized")
    
    def schedule_daily_meetings(self) -> None:
        """Schedule recurring daily meetings."""
        self._scheduled = True
        logger.info("Daily meetings scheduled at Pauli's Place")
        for name, meeting_time in self.meetings.items():
            logger.info("  %s: %s UTC", name, meeting_time.strftime("%H:%M"))
    
    def cancel_all(self) -> None:
        """Cancel all scheduled meetings."""
        self._scheduled = False
        logger.info("All meetings cancelled")

    @property
    def schedule(self) -> list[Meeting]:
        return DAILY_SCHEDULE
    
    def get_current_meeting(self) -> Optional[str]:
        """Get current meeting if one is active."""
        now = datetime.utcnow().time()
        for name, meeting_time in self.meetings.items():
            if abs((now.hour * 60 + now.minute) - (meeting_time.hour * 60 + meeting_time.minute)) < 60:
                return name
        return None
    
    def get_next_meeting(self) -> tuple[str, time]:
        """Get next scheduled meeting."""
        now = datetime.utcnow().time()
        for name, meeting_time in self.meetings.items():
            if (meeting_time.hour * 60 + meeting_time.minute) > (now.hour * 60 + now.minute):
                return name, meeting_time
        return "morning_briefing", self.meetings["morning_briefing"]
