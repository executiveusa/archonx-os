"""
Pauli's Place View
==================
Animated meeting-room visualization:
    - Round table with agent avatars
    - Speech bubbles during discussions
    - Chess board for Pauli vs Mirror matches
    - Card table for probability training
    - War room tactical map
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from archonx.meetings.paulis_place import Meeting, MeetingType

logger = logging.getLogger("archonx.visualization.paulis_place_view")


@dataclass
class AgentAvatar:
    """Visual representation of an agent at Pauli's Place."""

    agent_id: str
    name: str
    crew: str
    role: str
    seat_index: int
    speaking: bool = False
    speech_text: str = ""
    animation: str = "idle"  # idle | speaking | thinking | celebrating


@dataclass
class MeetingScene:
    """Full scene state for a meeting at Pauli's Place."""

    meeting_type: str
    description: str
    scene: str = "round_table"  # round_table | chess_board | card_table | war_room
    attendees: list[AgentAvatar] = field(default_factory=list)
    agenda_items: list[str] = field(default_factory=list)
    current_agenda_index: int = 0
    active: bool = False


class PaulisPlaceView:
    """
    Generates the Pauli's Place meeting visualization state.

    Scenes:
        - round_table: Morning briefing / evening review
        - chess_board: Pauli vs Mirror chess match
        - card_table: Probability training card games
        - war_room: Strategic tactical map
    """

    MEETING_TO_SCENE = {
        MeetingType.MORNING_BRIEFING: "round_table",
        MeetingType.CHESS_MATCH: "chess_board",
        MeetingType.CARD_GAMES: "card_table",
        MeetingType.WAR_ROOM: "war_room",
        MeetingType.EVENING_REVIEW: "round_table",
    }

    def __init__(self) -> None:
        self._current_scene: MeetingScene | None = None

    def start_meeting_scene(
        self,
        meeting: Meeting,
        attendee_data: list[dict[str, Any]],
    ) -> MeetingScene:
        """Create a new meeting scene visualization."""
        scene_type = self.MEETING_TO_SCENE.get(meeting.meeting_type, "round_table")

        avatars = [
            AgentAvatar(
                agent_id=a["agent_id"],
                name=a["name"],
                crew=a["crew"],
                role=a["role"],
                seat_index=i,
            )
            for i, a in enumerate(attendee_data)
        ]

        self._current_scene = MeetingScene(
            meeting_type=meeting.meeting_type.value,
            description=meeting.description,
            scene=scene_type,
            attendees=avatars,
            agenda_items=list(meeting.agenda),
            active=True,
        )

        logger.info(
            "Meeting scene started: %s (%s) with %d attendees",
            meeting.description,
            scene_type,
            len(avatars),
        )
        return self._current_scene

    def agent_speaks(self, agent_id: str, text: str) -> None:
        """Show a speech bubble for an agent."""
        if not self._current_scene:
            return
        for avatar in self._current_scene.attendees:
            if avatar.agent_id == agent_id:
                avatar.speaking = True
                avatar.speech_text = text
                avatar.animation = "speaking"
            else:
                avatar.speaking = False
                avatar.speech_text = ""
                avatar.animation = "idle"

    def advance_agenda(self) -> str | None:
        """Move to next agenda item, return it or None if done."""
        if not self._current_scene:
            return None
        idx = self._current_scene.current_agenda_index + 1
        if idx >= len(self._current_scene.agenda_items):
            return None
        self._current_scene.current_agenda_index = idx
        return self._current_scene.agenda_items[idx]

    def end_meeting_scene(self) -> None:
        if self._current_scene:
            self._current_scene.active = False
            logger.info("Meeting scene ended: %s", self._current_scene.description)
        self._current_scene = None

    @property
    def current_scene(self) -> MeetingScene | None:
        return self._current_scene

    def to_dict(self) -> dict[str, Any]:
        """Serialize current scene for the frontend."""
        if not self._current_scene:
            return {"active": False}

        scene = self._current_scene
        return {
            "active": scene.active,
            "meeting_type": scene.meeting_type,
            "description": scene.description,
            "scene": scene.scene,
            "attendees": [
                {
                    "agent_id": a.agent_id,
                    "name": a.name,
                    "crew": a.crew,
                    "role": a.role,
                    "seat": a.seat_index,
                    "speaking": a.speaking,
                    "speech": a.speech_text,
                    "animation": a.animation,
                }
                for a in scene.attendees
            ],
            "agenda": scene.agenda_items,
            "current_agenda": scene.current_agenda_index,
        }
