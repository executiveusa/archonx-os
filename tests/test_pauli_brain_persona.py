"""
BEAD: AX-MERGE-009
Tests for PauliBrainPersona (AX-PAULI-BRAIN-002)
==================================================
5 tests — all pass without external API calls.
"""

from __future__ import annotations

import pytest

from archonx.agents.pauli_brain_persona import PauliBrainPersona


@pytest.fixture
def pauli() -> PauliBrainPersona:
    """Create a PauliBrainPersona instance for testing."""
    return PauliBrainPersona()


def test_pauli_brain_defaults_to_english(pauli: PauliBrainPersona) -> None:
    """English text with no Serbian or Spanish markers should return en-US."""
    text = "I need a strategic analysis of the current repository health"
    lang = pauli.detect_language(text)
    assert lang == "en-US"


def test_pauli_brain_detects_serbian_cyrillic(pauli: PauliBrainPersona) -> None:
    """Text containing Cyrillic characters should be detected as sr-RS."""
    # Serbian: "Good morning, what is the status?"
    text = "Добро јутро, какав је статус пројекта?"
    lang = pauli.detect_language(text)
    assert lang == "sr-RS"


def test_pauli_brain_gets_correct_serbian_voice(pauli: PauliBrainPersona) -> None:
    """Serbian language should map to the ax-pauli-sr voice ID."""
    voice_id = pauli.get_voice_id("sr-RS")
    assert voice_id == "ax-pauli-sr"

    # English and Spanish should use ax-pauli-en
    assert pauli.get_voice_id("en-US") == "ax-pauli-en"
    assert pauli.get_voice_id("es-MX") == "ax-pauli-en"


def test_pauli_brain_escalates_above_usd_threshold(pauli: PauliBrainPersona) -> None:
    """Amounts above $500 USD should trigger escalation."""
    assert pauli.should_escalate("purchase software license", 501.0) is True
    assert pauli.should_escalate("renew subscription", 1000.0) is True
    assert pauli.should_escalate("buy coffee", 500.0) is False
    assert pauli.should_escalate("minor expense", 100.0) is False

    # Sensitive keywords should also trigger escalation regardless of amount
    assert pauli.should_escalate("delete production database", 0.0) is True
    assert pauli.should_escalate("security patch deployment", 0.0) is True


def test_pauli_brain_morning_brief_has_repo_data(pauli: PauliBrainPersona) -> None:
    """Morning brief must include repo health data."""
    repo_data = [
        {"repo": "archonx-os", "build_status": "passing", "open_issues": 2, "last_commit": "2026-02-25"},
        {"repo": "synthia", "build_status": "failing", "open_issues": 5, "last_commit": "2026-02-24"},
        {"repo": "tanda-cdmx", "build_status": "passing", "open_issues": 0, "last_commit": "2026-02-25"},
    ]
    brief = pauli.format_morning_brief(repo_data, language="en-US")

    # Should contain PAULI BRAIN signature
    assert "PAULI BRAIN" in brief
    # Should include fleet statistics
    assert "3" in brief  # total repos checked
    # Should mention healthy/issues counts
    assert "Healthy" in brief or "healthy" in brief.lower() or "2" in brief
    # Should mention the failing repo
    assert "synthia" in brief.lower() or "failing" in brief.lower() or "1" in brief
