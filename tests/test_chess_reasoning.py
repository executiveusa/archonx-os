"""
Tests — Collaborative Chess Reasoning Engine
"""

from archonx.core.chess_reasoning import (
    CollaborativeMatch,
    MergedResult,
    Proposal,
    Verdict,
)


def _proposal(crew: str, confidence: float, approach: str = "default") -> Proposal:
    return Proposal(
        crew=crew,
        approach=approach,
        confidence=confidence,
        risks=[f"{crew}_risk"],
        strengths=[f"{crew}_strength"],
    )


# --- Merge logic tests (unit-testing _merge directly) ---


class _FakeMatch(CollaborativeMatch):
    """Expose _merge for direct testing without async crews."""

    def __init__(self) -> None:
        # Skip super().__init__ — we don't need real crews for merge tests
        pass


def test_consensus_when_close() -> None:
    m = _FakeMatch()
    result = m._merge(_proposal("white", 0.85), _proposal("black", 0.82))
    assert result.verdict == Verdict.CONSENSUS
    assert result.confidence == 0.85


def test_white_preferred_when_moderate_gap() -> None:
    m = _FakeMatch()
    result = m._merge(_proposal("white", 0.9, "fast"), _proposal("black", 0.75, "safe"))
    assert result.verdict == Verdict.WHITE_PREFERRED
    assert result.chosen_approach == "fast"


def test_black_preferred_when_moderate_gap() -> None:
    m = _FakeMatch()
    result = m._merge(_proposal("white", 0.6, "fast"), _proposal("black", 0.75, "safe"))
    assert result.verdict == Verdict.BLACK_PREFERRED
    assert result.chosen_approach == "safe"


def test_escalated_when_large_gap() -> None:
    m = _FakeMatch()
    result = m._merge(_proposal("white", 0.95), _proposal("black", 0.5))
    assert result.verdict == Verdict.ESCALATED
    assert result.escalation_reason is not None
    assert "0.45" in result.escalation_reason
    assert "ESCALATED" in result.chosen_approach


def test_strengths_merged() -> None:
    m = _FakeMatch()
    result = m._merge(_proposal("white", 0.8), _proposal("black", 0.8))
    assert "white_strength" in result.merged_strengths
    assert "black_strength" in result.merged_strengths


def test_threshold_boundary_not_escalated() -> None:
    m = _FakeMatch()
    # Exactly at threshold (0.35) — uses strict >, so NOT escalated
    result = m._merge(_proposal("white", 0.85), _proposal("black", 0.50))
    assert result.verdict != Verdict.ESCALATED


def test_threshold_boundary_escalated() -> None:
    m = _FakeMatch()
    # Just above threshold → escalated
    result = m._merge(_proposal("white", 0.86), _proposal("black", 0.50))
    assert result.verdict == Verdict.ESCALATED


def test_extract_proposal() -> None:
    m = CollaborativeMatch(None, None)
    raw = {
        "approach": "test_approach",
        "confidence": 0.88,
        "risks": ["r1"],
        "strengths": ["s1"],
    }
    p = m._extract_proposal("white", raw)
    assert p.crew == "white"
    assert p.approach == "test_approach"
    assert p.confidence == 0.88


def test_extract_proposal_defaults() -> None:
    m = CollaborativeMatch(None, None)
    p = m._extract_proposal("black", {})
    assert p.confidence == 0.75  # default
    assert p.approach == "default"
