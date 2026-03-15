"""
BEAD: AX-MERGE-009
Tests for SynthiaPersona (AX-SYNTHIA-001)
==========================================
5 tests — all pass without external API calls.
"""

from __future__ import annotations

import pytest

from archonx.agents.synthia_persona import SynthiaPersona


@pytest.fixture
def synthia() -> SynthiaPersona:
    """Create a SynthiaPersona instance for testing."""
    return SynthiaPersona()


def test_synthia_system_prompt_is_spanish(synthia: SynthiaPersona) -> None:
    """The Spanish system prompt must be in Spanish and mention SAT/LFT."""
    prompt = synthia.get_system_prompt("es-MX")
    assert "SYNTHIA" in prompt
    assert "Kupuri Media" in prompt
    # Should contain Spanish-language content
    assert any(word in prompt for word in ["español", "Ley Federal", "SAT", "CFDI", "Ciudad de México"])


def test_synthia_detects_spanish_input(synthia: SynthiaPersona) -> None:
    """Spanish text with accented characters should be detected as es-MX."""
    text = "Buenas tardes, necesito una factura para mi empresa"
    lang = synthia.detect_language(text)
    assert lang == "es-MX"


def test_synthia_detects_english_input(synthia: SynthiaPersona) -> None:
    """English text without Spanish markers should be detected as en-US."""
    text = "Hello, I would like to schedule a meeting please"
    lang = synthia.detect_language(text)
    assert lang == "en-US"


def test_synthia_escalation_above_threshold(synthia: SynthiaPersona) -> None:
    """Amounts above 5000 MXN should trigger escalation."""
    assert synthia.should_escalate(5001.0) is True
    assert synthia.should_escalate(10000.0) is True
    assert synthia.should_escalate(5000.0) is False
    assert synthia.should_escalate(4999.99) is False


def test_synthia_morning_brief_in_spanish(synthia: SynthiaPersona) -> None:
    """Morning brief must be in Spanish and include key sections."""
    data = {
        "date": "25 de febrero de 2026",
        "calls": [{"name": "Carlos López", "context": "demo de producto"}],
        "leads": [{"name": "María Ramos", "score": 8, "last_contact": "ayer", "next_step": "demo"}],
        "tasks": [{"title": "Enviar contrato", "deadline": "hoy"}],
        "alerts": ["Repo tanda_cdmx tiene 3 issues abiertos"],
        "first_call_name": "Carlos López",
        "first_call_time": "10:00",
    }
    brief = synthia.format_morning_brief(data)

    # Must be in Spanish
    assert "Buenos días Ivette" in brief
    assert "SYNTHIA" in brief
    # Must include sections
    assert "LLAMADAS DE HOY" in brief
    assert "Carlos López" in brief
    assert "LEADS ACTIVOS" in brief
    assert "María Ramos" in brief
    assert "TAREAS CRÍTICAS" in brief
    assert "Enviar contrato" in brief
    assert "ALERTAS" in brief
    assert "primera llamada" in brief
