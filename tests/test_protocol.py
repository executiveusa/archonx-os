"""
Tests — Bobby Fischer Protocol
"""

from archonx.core.protocol import BobbyFischerProtocol, Decision


def test_protocol_approves_valid_task() -> None:
    proto = BobbyFischerProtocol()
    task = {"type": "deployment", "complexity": "medium"}
    decision = proto.evaluate(task)
    assert decision.approved is True
    assert decision.confidence >= 0.7
    assert decision.rollback_plan is not None


def test_protocol_rejects_missing_type() -> None:
    proto = BobbyFischerProtocol()
    task = {}  # no 'type' field → insufficient data
    decision = proto.evaluate(task)
    assert decision.approved is False
    assert "REQUEST_MORE_DATA" in decision.reason


def test_protocol_respects_confidence_threshold() -> None:
    proto = BobbyFischerProtocol(confidence_threshold=0.99)
    task = {"type": "deployment"}
    decision = proto.evaluate(task)
    # Default placeholder scoring ≈ 0.75, so should fail at 0.99 threshold
    assert decision.approved is False
    assert "CONFIDENCE_TOO_LOW" in decision.reason


def test_depth_high_complexity() -> None:
    proto = BobbyFischerProtocol(min_depth=5, preferred_depth=10)
    task = {"type": "migration", "complexity": "high"}
    decision = proto.evaluate(task)
    assert decision.depth == 10


def test_depth_low_complexity() -> None:
    proto = BobbyFischerProtocol(min_depth=5, preferred_depth=10)
    task = {"type": "hotfix", "complexity": "low"}
    decision = proto.evaluate(task)
    assert decision.depth == 5


def test_decision_history_logged() -> None:
    proto = BobbyFischerProtocol()
    proto.evaluate({"type": "task_a"})
    proto.evaluate({"type": "task_b"})
    assert len(proto.decision_history) == 2


def test_rollback_plan_contains_task_type() -> None:
    proto = BobbyFischerProtocol()
    decision = proto.evaluate({"type": "e-commerce-deploy"})
    assert "e-commerce-deploy" in (decision.rollback_plan or "")


def test_pattern_library_matching() -> None:
    proto = BobbyFischerProtocol()
    proto.pattern_library.record({"type": "deployment", "name": "blue-green"})
    proto.pattern_library.record({"type": "deployment", "name": "canary"})
    proto.pattern_library.record({"type": "migration", "name": "db-migration"})

    matches = proto.pattern_library.match({"type": "deployment"})
    assert len(matches) == 2
    assert all(m["type"] == "deployment" for m in matches)
