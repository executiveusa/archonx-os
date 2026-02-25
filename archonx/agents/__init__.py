"""
BEAD: AX-MERGE-003 / AX-MERGE-010
archonx.agents — Archon-X Agent Package
=========================================
Exports all persona classes, router, voice engine, phone bridge,
guardian fleet, and proactive engine.
"""

from archonx.agents.archon_x_guardian_fleet import GuardianFleet
from archonx.agents.archon_x_phone import ArchonXPhone
from archonx.agents.archon_x_proactive import ProactiveEngine
from archonx.agents.archon_x_router import ArchonXRouter
from archonx.agents.archon_x_voice_engine import ArchonXVoiceEngine
from archonx.agents.pauli_brain_persona import PauliBrainPersona
from archonx.agents.synthia_persona import SynthiaPersona


def load_persona_config(persona_id: str) -> dict:
    """
    Load persona configuration from archon_x_personas.yaml.

    Args:
        persona_id: Persona ID to load (e.g. "AX-SYNTHIA-001").

    Returns:
        Configuration dict for the specified persona.

    Raises:
        KeyError: If the persona_id is not found in the config.
        FileNotFoundError: If the config file does not exist.
    """
    from pathlib import Path

    import yaml

    config_path = Path(__file__).parent.parent / "config" / "archon_x_personas.yaml"
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    personas = config.get("personas", {})
    if persona_id not in personas:
        raise KeyError(f"Persona '{persona_id}' not found in archon_x_personas.yaml")
    return personas[persona_id]  # type: ignore[return-value]


__all__ = [
    "SynthiaPersona",
    "PauliBrainPersona",
    "ArchonXRouter",
    "ArchonXVoiceEngine",
    "ArchonXPhone",
    "GuardianFleet",
    "ProactiveEngine",
    "load_persona_config",
]
