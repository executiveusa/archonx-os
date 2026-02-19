"""
Collaborative Chess Reasoning Engine
=====================================
White and Black crews are *collaborators*, not competitors.
They evaluate the same task from different angles (optimistic vs adversarial)
then merge into a consensus result — like a chess position evaluated by both sides.

Flow:
    1. White proposes (optimistic, speed-oriented)
    2. Black critiques (adversarial, quality-oriented)
    3. Merge: best-of-both with confidence scoring
    4. If disagreement is high → escalate to Kings for final call
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger("archonx.core.chess_reasoning")


class Verdict(str, Enum):
    CONSENSUS = "consensus"
    WHITE_PREFERRED = "white_preferred"
    BLACK_PREFERRED = "black_preferred"
    ESCALATED = "escalated"


@dataclass
class Proposal:
    crew: str  # "white" | "black"
    approach: str
    confidence: float  # 0.0 – 1.0
    risks: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class MergedResult:
    verdict: Verdict
    chosen_approach: str
    confidence: float
    white_proposal: Proposal
    black_proposal: Proposal
    merged_strengths: list[str] = field(default_factory=list)
    mitigated_risks: list[str] = field(default_factory=list)
    escalation_reason: str | None = None


class CollaborativeMatch:
    """
    Run a collaborative reasoning match between White and Black crews.

    Both sides evaluate the same task; results are merged rather than fought over.
    """

    DISAGREEMENT_THRESHOLD = 0.35  # confidence gap triggering escalation

    def __init__(self, white_crew: Any, black_crew: Any) -> None:
        self.white = white_crew
        self.black = black_crew

    async def play(self, task: dict[str, Any], decision: Any) -> MergedResult:
        """
        Full reasoning match:
        1. White proposes → 2. Black critiques → 3. Merge
        """
        white_result = await self.white.execute(task, decision)
        black_result = await self.black.execute(task, decision)

        white_proposal = self._extract_proposal("white", white_result)
        black_proposal = self._extract_proposal("black", black_result)

        merged = self._merge(white_proposal, black_proposal)

        logger.info(
            "Match result: %s (conf=%.2f) | White=%.2f Black=%.2f",
            merged.verdict.value,
            merged.confidence,
            white_proposal.confidence,
            black_proposal.confidence,
        )
        return merged

    def _extract_proposal(self, crew: str, result: dict[str, Any]) -> Proposal:
        """Convert raw crew output into a structured Proposal."""
        return Proposal(
            crew=crew,
            approach=result.get("approach", result.get("results", {}).get("status", "default")),
            confidence=result.get("confidence", 0.75),
            risks=result.get("risks", []),
            strengths=result.get("strengths", []),
            data=result,
        )

    def _merge(self, white: Proposal, black: Proposal) -> MergedResult:
        """Merge two proposals into a consensus or escalation."""
        gap = abs(white.confidence - black.confidence)

        if gap > self.DISAGREEMENT_THRESHOLD:
            # Big disagreement → escalate to Kings
            return MergedResult(
                verdict=Verdict.ESCALATED,
                chosen_approach=f"ESCALATED: white={white.approach}, black={black.approach}",
                confidence=(white.confidence + black.confidence) / 2,
                white_proposal=white,
                black_proposal=black,
                escalation_reason=f"Confidence gap {gap:.2f} exceeds threshold {self.DISAGREEMENT_THRESHOLD}",
            )

        # Pick higher-confidence side's approach, merge strengths
        if white.confidence >= black.confidence:
            chosen = white.approach
            verdict = Verdict.WHITE_PREFERRED if gap > 0.1 else Verdict.CONSENSUS
        else:
            chosen = black.approach
            verdict = Verdict.BLACK_PREFERRED if gap > 0.1 else Verdict.CONSENSUS

        # Combine strengths, dedupe risks already addressed by the other side
        merged_strengths = list(set(white.strengths + black.strengths))
        all_risks = set(white.risks + black.risks)
        addressed = set(white.strengths + black.strengths)
        mitigated = [r for r in all_risks if any(s.lower() in r.lower() for s in addressed)]
        remaining = [r for r in all_risks if r not in mitigated]

        return MergedResult(
            verdict=verdict,
            chosen_approach=chosen,
            confidence=max(white.confidence, black.confidence),
            white_proposal=white,
            black_proposal=black,
            merged_strengths=merged_strengths,
            mitigated_risks=remaining,
        )
