"""
BEAD: AX-MERGE-009
Tests for ArchonXRouter
========================
4 tests — all pass without external API calls.
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from archonx.agents.archon_x_router import ArchonXRouter
from archonx.agents.pauli_brain_persona import PauliBrainPersona
from archonx.agents.synthia_persona import SynthiaPersona


@pytest.fixture
def router() -> ArchonXRouter:
    """Create an ArchonXRouter instance for testing."""
    return ArchonXRouter()


def test_router_defaults_to_synthia_when_env_unset(router: ArchonXRouter) -> None:
    """When AX_ACTIVE_PERSONA env var is not set, router should default to SYNTHIA."""
    with patch.dict(os.environ, {}, clear=False):
        # Remove AX_ACTIVE_PERSONA if present
        env = os.environ.copy()
        env.pop("AX_ACTIVE_PERSONA", None)
        with patch.dict(os.environ, env, clear=True):
            persona_id = router.select_persona()
            assert persona_id == "AX-SYNTHIA-001"


def test_router_selects_persona_from_env_var(router: ArchonXRouter) -> None:
    """AX_ACTIVE_PERSONA env var should override the default persona selection."""
    with patch.dict(os.environ, {"AX_ACTIVE_PERSONA": "AX-PAULI-BRAIN-002"}):
        persona_id = router.select_persona()
        assert persona_id == "AX-PAULI-BRAIN-002"


def test_router_returns_persona_instance(router: ArchonXRouter) -> None:
    """router.route() should return the correct persona instance type."""
    with patch.dict(os.environ, {}, clear=False):
        env = os.environ.copy()
        env.pop("AX_ACTIVE_PERSONA", None)
        with patch.dict(os.environ, env, clear=True):
            persona_id, instance = router.route(
                text="Hola, necesito una factura",
                bead_id="BEAD-TEST-001",
            )
            assert persona_id == "AX-SYNTHIA-001"
            assert isinstance(instance, SynthiaPersona)

    # Test PAULI BRAIN route via env override
    with patch.dict(os.environ, {"AX_ACTIVE_PERSONA": "AX-PAULI-BRAIN-002"}):
        persona_id, instance = router.route(
            text="Good morning, status report",
            bead_id="BEAD-TEST-002",
        )
        assert persona_id == "AX-PAULI-BRAIN-002"
        assert isinstance(instance, PauliBrainPersona)


def test_router_lists_two_personas(router: ArchonXRouter) -> None:
    """Router must list exactly two personas: SYNTHIA and PAULI BRAIN."""
    personas = router.list_personas()
    assert len(personas) == 2
    assert "AX-SYNTHIA-001" in personas
    assert "AX-PAULI-BRAIN-002" in personas
