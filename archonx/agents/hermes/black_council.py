"""
BEAD-HERMES-001 — BlackCouncil (Solution Layer)
================================================
Black council produces solutions and counter-proposals.
'Given the challenge, here's how we solve it.'
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("archonx.agents.hermes.black_council")


class BlackCouncil:
    """
    Solves problems. Answers: 'Given the risks White raised — here's the plan.'
    """

    def __init__(self, llm_client: Any | None = None) -> None:
        self._llm = llm_client

    async def solve(
        self,
        objective: str,
        white_challenge: str,
        context: dict[str, Any],
        round_num: int,
    ) -> str:
        """
        Returns a solution / counter-position to the White Council's challenge.
        """
        if self._llm is not None:
            return await self._llm_solve(objective, white_challenge, context, round_num)
        return self._structured_solve(objective, white_challenge, round_num)

    async def _llm_solve(
        self,
        objective: str,
        white_challenge: str,
        context: dict[str, Any],
        round_num: int,
    ) -> str:
        prompt = (
            f"[BLACK COUNCIL — ROUND {round_num}]\n"
            f"Objective: {objective}\n"
            f"White Council raised: {white_challenge}\n"
            f"Context: {context}\n\n"
            "You are the Black Council. Your role is to SOLVE this.\n"
            "Respond to each risk with a concrete mitigation.\n"
            "Respond to each assumption with a validation step.\n"
            "Propose actionable, spec-driven steps. No vague suggestions."
        )
        try:
            response = await self._llm.complete(prompt)
            return response.text if hasattr(response, "text") else str(response)
        except Exception as exc:
            logger.warning("BlackCouncil LLM call failed: %s — using structured fallback", exc)
            return self._structured_solve(objective, white_challenge, round_num)

    def _structured_solve(self, objective: str, white_challenge: str, round_num: int) -> str:
        return (
            f"[BLACK COUNCIL SOLUTION — Round {round_num}]\n"
            f"Responding to challenge on: '{objective}'\n"
            "Mitigations:\n"
            "  R1: Cap scope with explicit bead iteration limits (max 3 PAULIWHEEL cycles).\n"
            "  R2: Build dependency graph first; implement in topological order.\n"
            "  R3: Apply UDEC checklist as build-time assertions, not post-hoc review.\n"
            "Assumption validations:\n"
            "  A: Ping Twilio/Twitter health endpoints before Phase 3 deployment.\n"
            "  B: JSON schema validation on all spec files before Phase 2 starts.\n"
            "Proposed execution: sequential bead completion with integration tests at junction."
        )

    def vote(self, consensus_position: str, own_solution: str) -> float:
        """Score 0-1: how much does Black agree with the consensus position."""
        solution_words = set(own_solution.lower().split())
        consensus_words = set(consensus_position.lower().split())
        overlap = len(solution_words & consensus_words)
        return min(1.0, overlap / max(len(solution_words), 1))
