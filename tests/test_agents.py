"""
Tests — Agent Registry & All 64 Agents
"""

from archonx.core.agents import (
    Agent,
    AgentRegistry,
    AgentStatus,
    Crew,
    PauliKing,
    Role,
    SynthiaQueen,
    build_all_agents,
)


def test_build_all_agents_creates_64() -> None:
    registry = AgentRegistry()
    build_all_agents(registry)
    assert len(registry) == 64


def test_white_crew_has_32() -> None:
    registry = AgentRegistry()
    build_all_agents(registry)
    assert len(registry.get_by_crew(Crew.WHITE)) == 32


def test_black_crew_has_32() -> None:
    registry = AgentRegistry()
    build_all_agents(registry)
    assert len(registry.get_by_crew(Crew.BLACK)) == 32


def test_each_crew_has_one_king_and_one_queen() -> None:
    registry = AgentRegistry()
    build_all_agents(registry)
    for crew in (Crew.WHITE, Crew.BLACK):
        kings = registry.get_by_role(Role.KING, crew)
        queens = registry.get_by_role(Role.QUEEN, crew)
        assert len(kings) == 1, f"{crew.value} should have exactly 1 king"
        assert len(queens) == 1, f"{crew.value} should have exactly 1 queen"


def test_synthia_is_white_queen_d1() -> None:
    registry = AgentRegistry()
    build_all_agents(registry)
    synthia = registry.get("synthia_queen_white")
    assert synthia.name == "Synthia"
    assert synthia.role == Role.QUEEN
    assert synthia.crew == Crew.WHITE
    assert synthia.position == "D1"


def test_pauli_is_white_king_e1() -> None:
    registry = AgentRegistry()
    build_all_agents(registry)
    pauli = registry.get("pauli_king_white")
    assert pauli.name == "Pauli"
    assert pauli.role == Role.KING
    assert pauli.position == "E1"


def test_synthia_queen_facade() -> None:
    registry = AgentRegistry()
    build_all_agents(registry)
    sq = SynthiaQueen(registry)
    agent = sq.initialize()
    assert agent.status == AgentStatus.ACTIVE
    assert agent.name == "Synthia"


def test_pauli_king_facade() -> None:
    registry = AgentRegistry()
    build_all_agents(registry)
    pk = PauliKing(registry)
    agent = pk.initialize()
    assert agent.status == AgentStatus.ACTIVE
    assert agent.name == "Pauli"


def test_synthia_connects_to_pauli() -> None:
    registry = AgentRegistry()
    build_all_agents(registry)
    sq = SynthiaQueen(registry)
    pk = PauliKing(registry)
    sq.initialize()
    pk.initialize()
    sq.connect_to_king(pk)
    assert sq.agent.reports_to == "pauli_king_white"


def test_agent_record_task() -> None:
    a = Agent(
        agent_id="test_agent",
        name="Test",
        role=Role.PAWN,
        crew=Crew.WHITE,
        position="A2",
        specialty="testing",
    )
    assert a.tasks_completed == 0
    a.record_task(points=2.5)
    assert a.tasks_completed == 1
    assert a.score == 2.5
    a.record_task(points=1.0)
    assert a.tasks_completed == 2
    assert a.score == 3.5


def test_no_duplicate_agent_ids() -> None:
    registry = AgentRegistry()
    build_all_agents(registry)
    ids = [a.agent_id for a in registry.all()]
    assert len(ids) == len(set(ids)), "Duplicate agent IDs found!"


def test_no_duplicate_positions() -> None:
    registry = AgentRegistry()
    build_all_agents(registry)
    positions = [a.position for a in registry.all()]
    assert len(positions) == len(set(positions)), "Duplicate positions found!"
