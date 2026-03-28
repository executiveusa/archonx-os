"""
BEAD-HERMES-001 — WhiteCouncil (Challenge Layer)
==================================================
White council produces a critical challenge/question against a given objective.
Uses the WhiteCrew's strategic instinct — surfacing risks, gaps, assumptions.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("archonx.agents.hermes.white_council")


class WhiteCouncil:
    """
    Challenges proposals. Asks: 'What could go wrong? What are we assuming?'
    In council mode: receives objective + prior context, returns critique string.
    LLM client injected for live runs; falls back to structured analysis prompt.
    """

    def __init__(self, llm_client: Any | None = None) -> None:
        self._llm = llm_client

    async def challenge(self, objective: str, context: dict[str, Any], round_num: int) -> str:
        """
        Returns a critical challenge / risk identification for the objective.
        """
        if self._llm is not None:
            return await self._llm_challenge(objective, context, round_num)
        return self._structured_challenge(objective, context, round_num)

    async def _llm_challenge(self, objective: str, context: dict[str, Any], round_num: int) -> str:
        prompt = (
            f"[WHITE COUNCIL — ROUND {round_num}]\n"
            f"Objective: {objective}\n"
            f"Context: {context}\n\n"
            "You are the White Council. Your role is to CHALLENGE this objective.\n"
            "Identify: the 3 biggest risks, 2 hidden assumptions, 1 alternative approach.\n"
            "Be direct. No agreement-optimization. Truth over comfort."
        )
        try:
            response = await self._llm.complete(prompt)
            return response.text if hasattr(response, "text") else str(response)
        except Exception as exc:
            logger.warning("WhiteCouncil LLM call failed: %s — using structured fallback", exc)
            return self._structured_challenge(objective, context, round_num)

    def _structured_challenge(self, objective: str, _context: dict, round_num: int) -> str:
        return (
            f"[WHITE COUNCIL CHALLENGE — Round {round_num}]\n"
            f"Objective under review: '{objective}'\n"
            "Primary risks identified:\n"
            "  1. Scope may exceed time budget without explicit iteration cap.\n"
            "  2. Dependencies between components could cause cascading delays.\n"
            "  3. Quality gates (8.5/10 UDEC) may not be verifiable without user testing.\n"
            "Hidden assumptions:\n"
            "  A. External APIs (Twilio, Twitter) are accessible and funded.\n"
            "  B. All spec JSON files are complete and unambiguous.\n"
            "Suggested alternative: build minimal verticals per component before integrating."
        )

    def vote(self, consensus_position: str, own_challenge: str) -> float:
        """
        Score 0-1: how much does White agree with the consensus position?
        Simple fallback: if own challenge keywords appear in consensus → high agreement.
        """
        challenge_words = set(own_challenge.lower().split())
        consensus_words = set(consensus_position.lower().split())
        overlap = len(challenge_words & consensus_words)
        return min(1.0, overlap / max(len(challenge_words), 1))
