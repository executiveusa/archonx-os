"""
BEAD-HERMES-001 — HermesAgent
================================
Top-level orchestrator. Runs the WhiteCouncil↔BlackCouncil debate cycle,
synthesises consensus via ConsensusEngine, and produces an ExecutionPlan.

Pipeline:
    CouncilTask
        → WhiteCouncil.challenge()     (risks, assumptions)
        → BlackCouncil.solve()         (mitigations, plan)
        → ConsensusEngine.evaluate()   (convergence score)
        → repeat up to max_rounds
        → ConsensusEngine.compute()    (final verdict)
        → ExecutionPlan
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from archonx.agents.hermes.debate import (
    AssignedCrew,
    CouncilTask,
    DebateRound,
    ExecutionPlan,
    ExecutionResult,
)
from archonx.agents.hermes.white_council import WhiteCouncil
from archonx.agents.hermes.black_council import BlackCouncil
from archonx.agents.hermes.consensus import ConsensusEngine

logger = logging.getLogger("archonx.agents.hermes.agent")


class HermesAgent:
    """
    Karpathy LLM Council arbitrator.
    Receives a CouncilTask, runs n rounds of White↔Black debate,
    synthesises consensus, returns ExecutionPlan.
    """

    def __init__(
        self,
        white_council: WhiteCouncil | None = None,
        black_council: BlackCouncil | None = None,
        consensus_engine: ConsensusEngine | None = None,
        llm_client: Any | None = None,
        cost_guard: Any | None = None,
    ) -> None:
        self.white_council = white_council or WhiteCouncil(llm_client)
        self.black_council = black_council or BlackCouncil(llm_client)
        self.consensus_engine = consensus_engine or ConsensusEngine()
        self._llm = llm_client
        self._cost_guard = cost_guard

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def run(self, task: CouncilTask) -> ExecutionResult:
        """Full pipeline: deliberate → plan → (optional) execute."""
        consensus = await self.deliberate(task)
        plan = self._build_plan(consensus, task)
        return await self.execute(plan)

    async def deliberate(self, task: CouncilTask) -> Any:
        """Run the full debate cycle, return ConsensusResult."""
        rounds: list[DebateRound] = []

        for round_num in range(1, task.max_rounds + 1):
            try:
                white_pos = await asyncio.wait_for(
                    self.white_council.challenge(task.objective, task.context, round_num),
                    timeout=task.timeout_seconds / task.max_rounds,
                )
            except asyncio.TimeoutError:
                logger.warning("HermesAgent: White Council timed out in round %d", round_num)
                white_pos = "[WHITE COUNCIL TIMEOUT]"

            try:
                black_pos = await asyncio.wait_for(
                    self.black_council.solve(task.objective, white_pos, task.context, round_num),
                    timeout=task.timeout_seconds / task.max_rounds,
                )
            except asyncio.TimeoutError:
                logger.warning("HermesAgent: Black Council timed out in round %d", round_num)
                black_pos = "[BLACK COUNCIL TIMEOUT]"

            convergence = self.consensus_engine.evaluate_convergence(white_pos, black_pos)
            synthesis = self._arbitrate(white_pos, black_pos, convergence)

            rnd = DebateRound(
                round_number=round_num,
                white_position=white_pos,
                black_position=black_pos,
                hermes_synthesis=synthesis,
                convergence_score=convergence,
            )
            rounds.append(rnd)

            logger.info(
                "HermesAgent: round %d complete — convergence=%.3f",
                round_num,
                convergence,
            )

            if not self.consensus_engine.should_continue(rnd, task.max_rounds):
                logger.info("HermesAgent: stopping — threshold met or max rounds reached")
                break

        return self.consensus_engine.compute_consensus(rounds, task.requires_unanimous)

    async def execute(self, plan: ExecutionPlan) -> ExecutionResult:
        """Execute the agreed plan. For MVP: records and returns plan as output."""
        logger.info(
            "HermesAgent: executing plan %s (crew=%s, actions=%d)",
            plan.plan_id,
            plan.assigned_crew.value,
            len(plan.actions),
        )
        return ExecutionResult(
            plan_id=plan.plan_id,
            success=True,
            output={
                "plan_id": plan.plan_id,
                "assigned_crew": plan.assigned_crew.value,
                "actions": plan.actions,
                "consensus_confidence": (
                    plan.consensus_result.confidence if plan.consensus_result else 0.0
                ),
                "winning_position": (
                    plan.consensus_result.winning_position if plan.consensus_result else ""
                ),
            },
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _arbitrate(self, white: str, black: str, convergence: float) -> str:
        """Hermes synthesis — finds the common thread between positions."""
        if convergence >= 0.85:
            return f"[HERMES: HIGH CONVERGENCE ({convergence:.2f})] Consensus reached. {black}"
        if convergence >= 0.5:
            return (
                f"[HERMES: MODERATE CONVERGENCE ({convergence:.2f})] "
                f"Core agreement: implement iteratively with validation gates. "
                f"White risk mitigation + Black execution plan combined."
            )
        return (
            f"[HERMES: LOW CONVERGENCE ({convergence:.2f})] "
            f"Arbitrating: adopt Black Council's implementation approach "
            f"with White Council's risk mitigations as mandatory checkpoints."
        )

    def _build_plan(self, consensus: Any, task: CouncilTask) -> ExecutionPlan:
        actions: list[dict[str, Any]] = []
        if consensus.winning_position:
            actions.append({
                "step": 1,
                "action": "execute_consensus_position",
                "description": consensus.winning_position[:300],
                "assigned_to": "kernel",
            })
        return ExecutionPlan(
            consensus_result=consensus,
            actions=actions,
            assigned_crew=AssignedCrew.WHITE if consensus.white_vote >= consensus.black_vote else AssignedCrew.BLACK,
            cost_estimate=0.01 * len(actions),
        )
