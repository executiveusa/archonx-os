"""
Tests — Brenner Protocol (structured agent-to-agent collaboration)
"""

from archonx.core.brenner_protocol import (
    BrennerProtocol,
    Capability,
    CollaborationRequest,
    HandshakePhase,
)


def _setup_protocol() -> BrennerProtocol:
    proto = BrennerProtocol()
    proto.register_capability("agent_a", skills=["web_scraping", "research"], tools=["browser"], specialties=["data"])
    proto.register_capability("agent_b", skills=["code_gen", "testing"], tools=["terminal"], specialties=["code"])
    proto.register_capability("agent_c", skills=["web_scraping", "seo"], tools=["browser"], specialties=["marketing"])
    return proto


def test_register_capability() -> None:
    proto = _setup_protocol()
    assert len(proto._capabilities) == 3


def test_check_capability_matching_skill() -> None:
    proto = _setup_protocol()
    assert proto.check_capability("agent_a", skills=["web_scraping"])
    assert not proto.check_capability("agent_a", skills=["code_gen"])


def test_check_capability_matching_tool() -> None:
    proto = _setup_protocol()
    assert proto.check_capability("agent_b", tools=["terminal"])
    assert not proto.check_capability("agent_b", tools=["browser"])


def test_check_capability_unknown_agent() -> None:
    proto = _setup_protocol()
    assert not proto.check_capability("nonexistent")


def test_initiate_creates_request() -> None:
    proto = _setup_protocol()
    req = proto.initiate("agent_a", "agent_b", {"type": "code_review"}, {"file": "test.py"})
    assert req.id == "collab-00001"
    assert req.requester == "agent_a"
    assert req.helper == "agent_b"
    assert req.phase == HandshakePhase.CAPABILITY_CHECK
    assert not req.accepted


def test_accept_sets_execution_phase() -> None:
    proto = _setup_protocol()
    req = proto.initiate("a", "b", {"task": "x"})
    req = proto.accept(req)
    assert req.accepted
    assert req.phase == HandshakePhase.EXECUTION


def test_reject_sets_result() -> None:
    proto = _setup_protocol()
    req = proto.initiate("a", "b", {"task": "x"})
    req = proto.reject(req, reason="too busy")
    assert not req.accepted
    assert req.result["status"] == "rejected"
    assert req.result["reason"] == "too busy"
    assert req.completed_at is not None


def test_handoff_sets_result_and_timestamp() -> None:
    proto = _setup_protocol()
    req = proto.initiate("a", "b", {"task": "x"})
    req = proto.accept(req)
    req = proto.handoff(req, {"output": "done"})
    assert req.result["output"] == "done"
    assert req.phase == HandshakePhase.HANDOFF
    assert req.completed_at is not None


def test_feedback_records_improvements() -> None:
    proto = _setup_protocol()
    req = proto.initiate("a", "b", {"task": "x"})
    req = proto.accept(req)
    req = proto.handoff(req, {"output": "done"})
    req = proto.feedback(req, [{"description": "improve caching"}])
    assert len(req.improvements) == 1
    assert req.phase == HandshakePhase.FEEDBACK


def test_find_best_helper() -> None:
    proto = _setup_protocol()
    best = proto.find_best_helper(["web_scraping", "seo"])
    # agent_c has both web_scraping and seo
    assert best == "agent_c"


def test_find_best_helper_no_match() -> None:
    proto = _setup_protocol()
    best = proto.find_best_helper(["quantum_computing"])
    assert best is None


def test_stats() -> None:
    proto = _setup_protocol()
    req = proto.initiate("a", "b", {"task": "x"})
    proto.accept(req)
    proto.handoff(req, {"output": "ok"})
    stats = proto.stats
    assert stats["total_collaborations"] == 1
    assert stats["completed"] == 1
    assert stats["accepted"] == 1
    assert stats["registered_agents"] == 3


def test_full_handshake_lifecycle() -> None:
    proto = _setup_protocol()
    # 1. Check if helper can do it
    assert proto.check_capability("agent_a", skills=["web_scraping"])
    # 2. Initiate
    req = proto.initiate("agent_b", "agent_a", {"type": "scrape", "url": "example.com"})
    # 3. Accept
    req = proto.accept(req)
    # 4. Handoff
    req = proto.handoff(req, {"status": "scraped", "data": "..."})
    # 5. Feedback
    req = proto.feedback(req, [{"description": "add retry logic on timeout"}])
    assert req.phase == HandshakePhase.FEEDBACK
    assert req.accepted
    assert req.result["status"] == "scraped"
