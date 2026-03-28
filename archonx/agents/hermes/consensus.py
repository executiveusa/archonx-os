"""
BEAD-HERMES-001 — ConsensusEngine
===================================
Weighted-vote consensus across White and Black council positions.
Hermes tiebreaks when convergence_score < threshold.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from archonx.agents.hermes.debate import ConsensusResult, DebateRound

if TYPE_CHECKING:
    pass

logger = logging.getLogger("archonx.agents.hermes.consensus")

_CONSENSUS_THRESHOLD = 0.85   # Stop debating if convergence >= this


class ConsensusEngine:
    """
    Evaluates debate rounds and determines whether consensus is reached.
    Uses simple keyword overlap + weighted vote for convergence scoring.
    No external LLM calls — deterministic.
    """

    def __init__(self, threshold: float = _CONSENSUS_THRESHOLD) -> None:
        self.threshold = threshold

    def evaluate_convergence(self, white: str, black: str) -> float:
        """
        Score 0-1: how similar are the two positions?
        Uses Jaccard similarity on lowercase word tokens.
        """
        w_tokens = set(white.lower().split())
        b_tokens = set(black.lower().split())
        if not w_tokens or not b_tokens:
            return 0.0
        intersection = len(w_tokens & b_tokens)
        union = len(w_tokens | b_tokens)
        return intersection / union if union else 0.0

    def should_continue(self, round_: DebateRound, max_rounds: int) -> bool:
        """Return True if another debate round is warranted."""
        if round_.round_number >= max_rounds:
            return False
        return round_.convergence_score < self.threshold

    def compute_consensus(
        self,
        rounds: list[DebateRound],
        requires_unanimous: bool = False,
    ) -> ConsensusResult:
        """
        After all rounds: weight later rounds more heavily, compute final vote.
        """
        if not rounds:
            return ConsensusResult(
                reached=False,
                rounds_taken=0,
                winning_position="",
                confidence=0.0,
                white_vote=0.0,
                black_vote=0.0,
            )

        last = rounds[-1]
        final_score = last.convergence_score

        # Weighted average: later rounds count more
        total_weight = 0.0
        weighted_score = 0.0
        for i, r in enumerate(rounds):
            weight = i + 1
            weighted_score += r.convergence_score * weight
            total_weight += weight
        avg_score = weighted_score / total_weight if total_weight else 0.0

        reached = avg_score >= self.threshold
        if requires_unanimous:
            reached = final_score >= 0.95

        # Hermes override: force consensus after max rounds even if below threshold
        hermes_override = (not reached) and (last.round_number >= 3)
        if hermes_override:
            reached = True

        # Derive individual crew votes from last round synthesis
        white_vote = min(1.0, final_score + 0.1)
        black_vote = max(0.0, final_score - 0.05)

        winning_position = last.hermes_synthesis if reached else last.white_position

        return ConsensusResult(
            reached=reached,
            rounds_taken=len(rounds),
            winning_position=winning_position,
            confidence=avg_score,
            white_vote=white_vote,
            black_vote=black_vote,
            hermes_override=hermes_override,
        )
