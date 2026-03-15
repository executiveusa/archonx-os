"""
Tests — Agent Theater + Token Meter (billing)
"""

import time
from archonx.visualization.agent_theater import AgentTheater, TheaterEvent, TheaterSession
from archonx.billing.token_meter import TokenMeter, TokenTransaction


# ==================== Agent Theater ====================


def test_emit_creates_event() -> None:
    t = AgentTheater()
    ev = t.emit("agent_action", "pawn_a2", "Scout Alpha", "Scanning target")
    assert ev.event_type == "agent_action"
    assert ev.agent_id == "pawn_a2"
    assert ev.description == "Scanning target"


def test_recent_events() -> None:
    t = AgentTheater()
    for i in range(5):
        t.emit("agent_action", f"agent_{i}", f"Agent {i}", f"Action {i}")
    recent = t.get_recent_events(limit=3)
    assert len(recent) == 3
    assert recent[-1].description == "Action 4"


def test_start_session() -> None:
    t = AgentTheater()
    session = t.start_session("user_123")
    assert session.viewer_id == "user_123"
    assert session.active
    assert session.tokens_spent == 0


def test_end_session_calculates_tokens() -> None:
    t = AgentTheater()
    session = t.start_session("user_123")
    # Backdate start to simulate time passing
    session.started_at = time.time() - 120  # 2 minutes ago
    ended = t.end_session(session.session_id)
    assert not ended.active
    assert ended.tokens_spent >= 18  # ~2 min × 10 tokens/min = 20 (±rounding)


def test_end_nonexistent_session() -> None:
    t = AgentTheater()
    assert t.end_session("nonexistent") is None


def test_session_events_filtered() -> None:
    t = AgentTheater()
    session = t.start_session("viewer_1")
    t.emit("agent_action", "a1", "Test", "During session")
    events = t.get_session_events(session.session_id)
    assert len(events) >= 1


def test_theater_stats() -> None:
    t = AgentTheater()
    t.emit("agent_action", "a1", "Test", "Event 1")
    s = t.start_session("v1")
    stats = t.stats
    assert stats["total_events"] == 1
    assert stats["active_sessions"] == 1


def test_event_log_max_capacity() -> None:
    t = AgentTheater()
    # maxlen is 10000 — just verify it doesn't crash on many events
    for i in range(100):
        t.emit("test", f"a{i}", f"Agent {i}", f"Event {i}")
    assert len(t.get_recent_events(limit=50)) == 50


# ==================== Token Meter ====================


def test_credit_adds_balance() -> None:
    meter = TokenMeter()
    txn = meter.credit("user_1", 1000)
    assert meter.balance("user_1") == 1000
    assert txn.amount == -1000  # negative = credit


def test_charge_deducts_balance() -> None:
    meter = TokenMeter()
    meter.credit("user_1", 1000)
    txn = meter.charge("user_1", 200, "theater")
    assert txn is not None
    assert meter.balance("user_1") == 800
    assert txn.amount == 200


def test_charge_insufficient_balance() -> None:
    meter = TokenMeter()
    meter.credit("user_1", 100)
    txn = meter.charge("user_1", 200, "skill")
    assert txn is None
    assert meter.balance("user_1") == 100  # unchanged


def test_balance_unknown_user() -> None:
    meter = TokenMeter()
    assert meter.balance("nonexistent") == 0


def test_history() -> None:
    meter = TokenMeter()
    meter.credit("u1", 500)
    meter.charge("u1", 100, "theater")
    meter.charge("u1", 50, "skill")
    history = meter.history("u1")
    assert len(history) == 3


def test_history_limit() -> None:
    meter = TokenMeter()
    meter.credit("u1", 10000)
    for i in range(10):
        meter.charge("u1", 10, "api", f"Call {i}")
    history = meter.history("u1", limit=5)
    assert len(history) == 5


def test_stats() -> None:
    meter = TokenMeter()
    meter.credit("u1", 1000)
    meter.credit("u2", 500)
    meter.charge("u1", 200, "theater")
    stats = meter.stats
    assert stats["total_users"] == 2
    assert stats["total_charged"] == 200
    assert stats["total_credited"] == 1500
    assert stats["total_transactions"] == 3


def test_multiple_users_isolated() -> None:
    meter = TokenMeter()
    meter.credit("u1", 1000)
    meter.credit("u2", 500)
    meter.charge("u1", 100, "theater")
    assert meter.balance("u1") == 900
    assert meter.balance("u2") == 500
