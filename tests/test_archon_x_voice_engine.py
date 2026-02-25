"""
BEAD: AX-MERGE-009
Tests for ArchonXVoiceEngine
=============================
4 tests — mocks ElevenLabs API calls.
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from archonx.agents.archon_x_voice_engine import ArchonXVoiceEngine


@pytest.fixture
def engine_no_key() -> ArchonXVoiceEngine:
    """Create a voice engine with no API key (mock mode)."""
    with patch.dict(os.environ, {}, clear=False):
        env = os.environ.copy()
        env.pop("ELEVEN_LABS_API", None)
        with patch.dict(os.environ, env, clear=True):
            return ArchonXVoiceEngine()


@pytest.fixture
def engine_with_key() -> ArchonXVoiceEngine:
    """Create a voice engine with a dummy API key."""
    with patch.dict(os.environ, {"ELEVEN_LABS_API": "test_key_12345"}):
        return ArchonXVoiceEngine()


def test_voice_engine_selects_synthia_mx_voice(engine_no_key: ArchonXVoiceEngine) -> None:
    """SYNTHIA + es-MX should map to ax-synthia-mx voice."""
    voice_id = engine_no_key.select_voice("AX-SYNTHIA-001", "es-MX")
    assert voice_id == "ax-synthia-mx"

    # SYNTHIA en-US also uses the same multilingual voice
    voice_id_en = engine_no_key.select_voice("AX-SYNTHIA-001", "en-US")
    assert voice_id_en == "ax-synthia-mx"


def test_voice_engine_selects_pauli_sr_voice_for_serbian(
    engine_no_key: ArchonXVoiceEngine,
) -> None:
    """PAULI BRAIN + sr-RS should map to ax-pauli-sr voice."""
    voice_id = engine_no_key.select_voice("AX-PAULI-BRAIN-002", "sr-RS")
    assert voice_id == "ax-pauli-sr"

    # English PAULI BRAIN should use ax-pauli-en
    voice_id_en = engine_no_key.select_voice("AX-PAULI-BRAIN-002", "en-US")
    assert voice_id_en == "ax-pauli-en"


def test_voice_engine_mock_synthesize_returns_bytes(
    engine_no_key: ArchonXVoiceEngine,
) -> None:
    """Mock synthesize (no API key) must return bytes (empty b'')."""
    result = engine_no_key.synthesize("Hola Ivette", "ax-synthia-mx", "es-MX")
    assert isinstance(result, bytes)
    # In mock mode, returns empty bytes
    assert result == b""


def test_voice_engine_is_available_false_when_no_api_key(
    engine_no_key: ArchonXVoiceEngine,
) -> None:
    """is_available() must return False when ELEVEN_LABS_API is not set."""
    assert engine_no_key.is_available() is False

    # With a key set, should return True
    with patch.dict(os.environ, {"ELEVEN_LABS_API": "test_key_xyz"}):
        engine_with_key = ArchonXVoiceEngine()
        assert engine_with_key.is_available() is True
