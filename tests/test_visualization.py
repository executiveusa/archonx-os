"""
Tests — Visualization (Chessboard, Dashboard, Pauli's Place View)
"""

import pytest

from archonx.core.agents import AgentRegistry, Crew, build_all_agents
from archonx.core.metrics import Leaderboard, MetricSnapshot
from archonx.meetings.paulis_place import DAILY_SCHEDULE
from archonx.visualization.chessboard import ChessboardView
from archonx.visualization.dashboard import MetricsDashboard
from archonx.visualization.paulis_place_view import PaulisPlaceView


@pytest.fixture
def registry() -> AgentRegistry:
    r = AgentRegistry()
    build_all_agents(r)
    return r


def test_chessboard_8x8(registry: AgentRegistry) -> None:
    view = ChessboardView(registry)
    board = view.get_board_state()
    assert len(board) == 8
    assert all(len(row) == 8 for row in board)


def test_chessboard_to_dict(registry: AgentRegistry) -> None:
    view = ChessboardView(registry)
    data = view.to_dict()
    assert "board" in data
    assert "collaborations" in data
    assert len(data["board"]) == 8


def test_chessboard_collaboration_lines(registry: AgentRegistry) -> None:
    view = ChessboardView(registry)
    view.add_collaboration("D1", "B1", strength=0.9)
    view.add_collaboration("D1", "G2", strength=0.7)
    assert len(view.collaboration_lines) == 2
    view.clear_collaborations()
    assert len(view.collaboration_lines) == 0


def test_dashboard_crew_scores(registry: AgentRegistry) -> None:
    lb = Leaderboard()
    lb.record(MetricSnapshot(crew="white", tasks_completed=10))
    lb.record(MetricSnapshot(crew="black", tasks_completed=8))
    dashboard = MetricsDashboard(registry, lb)
    scores = dashboard.get_crew_scores()
    assert "white_score" in scores
    assert "black_score" in scores


def test_dashboard_system_health(registry: AgentRegistry) -> None:
    lb = Leaderboard()
    dashboard = MetricsDashboard(registry, lb)
    health = dashboard.get_system_health()
    assert health["agents_total"] == 64
    assert health["average_health"] == 1.0  # all agents start at 1.0


def test_dashboard_to_dict(registry: AgentRegistry) -> None:
    lb = Leaderboard()
    dashboard = MetricsDashboard(registry, lb)
    data = dashboard.to_dict()
    assert "crew_scores" in data
    assert "tasks_today" in data
    assert "system_health" in data
    assert "leaderboard" in data


def test_paulis_place_view_no_scene() -> None:
    view = PaulisPlaceView()
    assert view.current_scene is None
    assert view.to_dict() == {"active": False}


def test_paulis_place_view_start_scene() -> None:
    view = PaulisPlaceView()
    meeting = DAILY_SCHEDULE[0]  # morning briefing
    attendees = [
        {"agent_id": "synthia_queen_white", "name": "Synthia", "crew": "white", "role": "queen"},
        {"agent_id": "pauli_king_white", "name": "Pauli", "crew": "white", "role": "king"},
    ]
    scene = view.start_meeting_scene(meeting, attendees)
    assert scene.active is True
    assert scene.scene == "round_table"
    assert len(scene.attendees) == 2


def test_paulis_place_view_speech() -> None:
    view = PaulisPlaceView()
    meeting = DAILY_SCHEDULE[0]
    attendees = [
        {"agent_id": "synthia_queen_white", "name": "Synthia", "crew": "white", "role": "queen"},
    ]
    view.start_meeting_scene(meeting, attendees)
    view.agent_speaks("synthia_queen_white", "Good morning, team!")
    avatar = view.current_scene.attendees[0]
    assert avatar.speaking is True
    assert avatar.speech_text == "Good morning, team!"


def test_paulis_place_view_end_scene() -> None:
    view = PaulisPlaceView()
    meeting = DAILY_SCHEDULE[0]
    view.start_meeting_scene(meeting, [])
    view.end_meeting_scene()
    assert view.current_scene is None
