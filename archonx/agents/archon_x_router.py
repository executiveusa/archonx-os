"""
BEAD: AX-MERGE-004
Archon-X Router
================
Selects the active persona based on env var, language detection, or default.
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from archonx.agents.pauli_brain_persona import PauliBrainPersona
from archonx.agents.synthia_persona import SynthiaPersona

if TYPE_CHECKING:
    pass

logger = logging.getLogger("archonx.agents.archon_x_router")

_PERSONA_MAP: dict[str, type[SynthiaPersona] | type[PauliBrainPersona]] = {
    "AX-SYNTHIA-001": SynthiaPersona,
    "AX-PAULI-BRAIN-002": PauliBrainPersona,
}

# Type alias for either persona instance
BasePersona = SynthiaPersona | PauliBrainPersona


class ArchonXRouter:
    """
    Routes incoming interactions to the correct persona.

    Selection priority:
    1. AX_ACTIVE_PERSONA environment variable
    2. Language detection from provided text
    3. Default: AX-SYNTHIA-001
    """

    DEFAULT_PERSONA_ID: str = "AX-SYNTHIA-001"

    def __init__(self) -> None:
        """Initialise router with persona instances cached."""
        self._instances: dict[str, BasePersona] = {
            "AX-SYNTHIA-001": SynthiaPersona(),
            "AX-PAULI-BRAIN-002": PauliBrainPersona(),
        }
        logger.info("ArchonXRouter initialised with %d personas", len(self._instances))

    def select_persona(
        self,
        env_override: str | None = None,
        text: str | None = None,
    ) -> str:
        """
        Determine the active persona ID.

        Args:
            env_override: Explicit persona ID override (bypasses env var check).
            text: Optional text for language-based detection.

        Returns:
            Persona ID string (e.g. "AX-SYNTHIA-001").
        """
        # 1. Explicit override
        if env_override and env_override in _PERSONA_MAP:
            logger.debug("Persona selected via override: %s", env_override)
            return env_override

        # 2. Environment variable
        env_persona = os.environ.get("AX_ACTIVE_PERSONA", "").strip()
        if env_persona and env_persona in _PERSONA_MAP:
            logger.debug("Persona selected via AX_ACTIVE_PERSONA env: %s", env_persona)
            return env_persona

        # 3. Language detection from text
        if text:
            synthia = self._instances["AX-SYNTHIA-001"]
            assert isinstance(synthia, SynthiaPersona)
            pauli = self._instances["AX-PAULI-BRAIN-002"]
            assert isinstance(pauli, PauliBrainPersona)

            # Check for Serbian first (Pauli Brain handles Serbian)
            lang = pauli.detect_language(text)
            if lang == "sr-RS":
                logger.debug("Persona selected via Serbian detection: AX-PAULI-BRAIN-002")
                return "AX-PAULI-BRAIN-002"

            # English default: check if it is clearly English (Pauli) vs Spanish (Synthia)
            synthia_lang = synthia.detect_language(text)
            if synthia_lang == "en-US":
                # Ambiguous — default to Synthia unless env says otherwise
                logger.debug("Language en-US detected, defaulting to SYNTHIA")
                return self.DEFAULT_PERSONA_ID

        # 4. Default
        logger.debug("Persona defaulting to: %s", self.DEFAULT_PERSONA_ID)
        return self.DEFAULT_PERSONA_ID

    def route(self, text: str, bead_id: str) -> tuple[str, BasePersona]:
        """
        Route an interaction to the correct persona.

        Args:
            text: Input text for language detection and persona selection.
            bead_id: BEAD ID for traceability (required).

        Returns:
            Tuple of (persona_id, persona_instance).

        Raises:
            ValueError: If bead_id is empty.
        """
        if not bead_id:
            raise ValueError("bead_id is required for all routed interactions")

        persona_id = self.select_persona(text=text)
        instance = self._instances[persona_id]
        logger.info(
            "BEAD %s routed to persona %s",
            bead_id,
            persona_id,
        )
        return persona_id, instance

    def list_personas(self) -> list[str]:
        """
        Return the list of available persona IDs.

        Returns:
            List of persona ID strings.
        """
        return list(_PERSONA_MAP.keys())

    def get_persona(self, persona_id: str) -> BasePersona:
        """
        Retrieve a persona instance by ID.

        Args:
            persona_id: The persona ID to retrieve.

        Returns:
            Persona instance.

        Raises:
            KeyError: If persona_id is not registered.
        """
        if persona_id not in self._instances:
            raise KeyError(f"Unknown persona: {persona_id}")
        return self._instances[persona_id]
