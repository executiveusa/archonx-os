"""
Tests — Pauli's Place meetings
"""

import pytest

from archonx.meetings.paulis_place import (
    DAILY_SCHEDULE,
    MeetingType,
    PaulisPlaceManager,
)


def test_five_daily_meetings() -> None:
    assert len(DAILY_SCHEDULE) == 5


def test_meeting_schedule_times() -> None:
    times = [m.time_utc.hour for m in DAILY_SCHEDULE]
    assert times == [8, 12, 15, 18, 21]


def test_schedule_activation() -> None:
    mgr = PaulisPlaceManager()
    assert mgr.is_active is False
    mgr.schedule_daily_meetings()
    assert mgr.is_active is True


def test_cancel_all() -> None:
    mgr = PaulisPlaceManager()
    mgr.schedule_daily_meetings()
    mgr.cancel_all()
    assert mgr.is_active is False


@pytest.mark.asyncio
async def test_run_meeting() -> None:
    mgr = PaulisPlaceManager()
    meeting = DAILY_SCHEDULE[0]  # morning briefing
    result = await mgr.run_meeting(meeting)
    assert result["status"] == "completed"
    assert result["meeting"] == MeetingType.MORNING_BRIEFING.value


@pytest.mark.asyncio
async def test_register_and_run_handler() -> None:
    mgr = PaulisPlaceManager()
    called_with = []

    async def handler(meeting):
        called_with.append(meeting.meeting_type)

    mgr.register_handler(MeetingType.WAR_ROOM, handler)
    war_room = [m for m in DAILY_SCHEDULE if m.meeting_type == MeetingType.WAR_ROOM][0]
    await mgr.run_meeting(war_room)
    assert MeetingType.WAR_ROOM in called_with
