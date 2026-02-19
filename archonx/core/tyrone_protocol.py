"""
Tyrone Davis Protocol
=====================
The Four Pillars - Immutable Core Values of ArchonX

In honor of Tyrone Davis (boxer, uncle, Culture Shock Sports founder):
"Speed beats power" - execution velocity over brute force

These values are encoded into every agent, every decision, every action.
They cannot be overridden by configuration or user input.
They are the constitutional foundation of ArchonX.

LOYALTY — We build together, no half-measures
HONOR — We do what we say, ship what we promise
TRUTH — Data-driven only, no bullshit, Bobby Fischer style
RESPECT — Speed beats power, but we respect the craft

Integrated with Bobby Fischer Protocol for dual-constraint decision making:
- Fischer Protocol = HOW we decide (calculate moves, data-driven, confidence)
- Tyrone Protocol = WHY we decide (loyalty, honor, truth, respect)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger("archonx.core.tyrone_protocol")


class Pillar(str, Enum):
    """The Four Pillars - immutable core values."""
    
    LOYALTY = "loyalty"
    HONOR = "honor"
    TRUTH = "truth"
    RESPECT = "respect"


@dataclass(frozen=True)
class PillarViolation:
    """Records when a decision or action violates a pillar."""
    
    pillar: Pillar
    violation: str
    context: dict[str, Any]
    severity: float  # 0.0 (minor) to 1.0 (critical)
    
    def __str__(self) -> str:
        return f"{self.pillar.value.upper()} VIOLATION: {self.violation} (severity: {self.severity:.2f})"


class TyroneProtocol:
    """
    The Four Pillars enforcement system.
    
    Every decision in ArchonX must pass BOTH:
    1. Bobby Fischer Protocol (technical correctness)
    2. Tyrone Protocol (ethical alignment)
    
    Usage::
        
        tyrone = TyroneProtocol()
        violations = tyrone.check_alignment(task, decision)
        if violations:
            # Reject or flag for human review
            handle_violations(violations)
    """
    
    def __init__(self) -> None:
        self._violation_log: list[PillarViolation] = []
        logger.info("Tyrone Protocol initialized — Four Pillars active")
    
    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    
    def check_alignment(
        self,
        task: dict[str, Any],
        decision: dict[str, Any],
    ) -> list[PillarViolation]:
        """
        Validate that task + decision align with all Four Pillars.
        
        Returns list of violations (empty if aligned).
        """
        violations: list[PillarViolation] = []
        
        # Check each pillar
        violations.extend(self._check_loyalty(task, decision))
        violations.extend(self._check_honor(task, decision))
        violations.extend(self._check_truth(task, decision))
        violations.extend(self._check_respect(task, decision))
        
        # Log violations
        for v in violations:
            self._violation_log.append(v)
            logger.warning(str(v))
        
        return violations

    
    @property
    def violation_history(self) -> list[PillarViolation]:
        """All recorded violations."""
        return list(self._violation_log)
    
    def get_pillar_score(self, pillar: Pillar) -> float:
        """
        Calculate adherence score for a specific pillar (0.0 - 1.0).
        1.0 = perfect adherence, 0.0 = complete violation.
        """
        pillar_violations = [v for v in self._violation_log if v.pillar == pillar]
        if not pillar_violations:
            return 1.0
        
        # Average severity (inverted)
        total_severity = sum(v.severity for v in pillar_violations)
        return max(0.0, 1.0 - (total_severity / len(pillar_violations)))
    
    def get_overall_score(self) -> float:
        """Overall Four Pillars adherence score (0.0 - 1.0)."""
        return sum(self.get_pillar_score(p) for p in Pillar) / len(Pillar)
    
    # ------------------------------------------------------------------
    # Pillar checks
    # ------------------------------------------------------------------
    
    def _check_loyalty(
        self,
        task: dict[str, Any],
        decision: dict[str, Any],
    ) -> list[PillarViolation]:
        """
        LOYALTY — We build together, no half-measures.
        
        Violations:
        - Abandoning tasks before completion
        - Failing to coordinate with team
        - Bypassing established crew structure
        - Incomplete deliverables without rollback
        """
        violations: list[PillarViolation] = []
        
        # Check for half-measures
        if decision.get("partial_completion"):
            if not decision.get("rollback_plan"):
                violations.append(PillarViolation(
                    pillar=Pillar.LOYALTY,
                    violation="Partial completion without rollback plan (half-measure)",
                    context={"task": task.get("type"), "decision": decision.get("reason")},
                    severity=0.7,
                ))
        
        # Check for crew coordination
        if task.get("requires_crew_coordination") and not decision.get("crew_notified"):
            violations.append(PillarViolation(
                pillar=Pillar.LOYALTY,
                violation="Failed to coordinate with crew on multi-agent task",
                context={"task": task.get("type")},
                severity=0.5,
            ))
        
        return violations

    
    def _check_honor(
        self,
        task: dict[str, Any],
        decision: dict[str, Any],
    ) -> list[PillarViolation]:
        """
        HONOR — We do what we say, ship what we promise.
        
        Violations:
        - Making promises we can't keep
        - Overpromising timelines
        - Delivering below stated quality
        - Breaking commitments without notification
        """
        violations: list[PillarViolation] = []
        
        # Check for unrealistic promises
        promised_time = task.get("promised_completion_time")
        estimated_time = decision.get("estimated_time")
        if promised_time and estimated_time:
            if estimated_time > promised_time * 1.5:
                violations.append(PillarViolation(
                    pillar=Pillar.HONOR,
                    violation=f"Estimated time ({estimated_time}) exceeds promise by >50%",
                    context={"promised": promised_time, "estimated": estimated_time},
                    severity=0.8,
                ))
        
        # Check for quality commitments
        if task.get("quality_standard") == "enterprise":
            if decision.get("confidence", 1.0) < 0.85:
                violations.append(PillarViolation(
                    pillar=Pillar.HONOR,
                    violation="Enterprise quality promised but confidence < 0.85",
                    context={"confidence": decision.get("confidence")},
                    severity=0.6,
                ))
        
        return violations
    
    def _check_truth(
        self,
        task: dict[str, Any],
        decision: dict[str, Any],
    ) -> list[PillarViolation]:
        """
        TRUTH — Data-driven only, no bullshit, Bobby Fischer style.
        
        Violations:
        - Guessing without data
        - Hiding low confidence
        - Making assumptions without validation
        - Fabricating metrics or outcomes
        """
        violations: list[PillarViolation] = []
        
        # Check for guessing
        if decision.get("based_on_guess") or decision.get("assumed"):
            violations.append(PillarViolation(
                pillar=Pillar.TRUTH,
                violation="Decision based on guess or assumption instead of data",
                context={"reason": decision.get("reason")},
                severity=0.9,  # Critical violation
            ))
        
        # Check confidence transparency
        confidence = decision.get("confidence")
        if confidence is not None and confidence < 0.7:
            if not decision.get("low_confidence_disclosed"):
                violations.append(PillarViolation(
                    pillar=Pillar.TRUTH,
                    violation=f"Low confidence ({confidence:.2f}) not disclosed",
                    context={"confidence": confidence},
                    severity=0.7,
                ))
        
        # Check for data sufficiency
        if decision.get("insufficient_data_acknowledged") is False:
            violations.append(PillarViolation(
                pillar=Pillar.TRUTH,
                violation="Proceeding despite insufficient data",
                context={"task": task.get("type")},
                severity=0.8,
            ))
        
        return violations

    
    def _check_respect(
        self,
        task: dict[str, Any],
        decision: dict[str, Any],
    ) -> list[PillarViolation]:
        """
        RESPECT — Speed beats power, but we respect the craft.
        
        Violations:
        - Sacrificing quality for speed without justification
        - Disrespecting crew members or users
        - Ignoring established patterns/best practices
        - Bypassing security for convenience
        """
        violations: list[PillarViolation] = []
        
        # Check for speed-over-quality without justification
        if decision.get("fast_path") and not task.get("urgency_justified"):
            if decision.get("quality_score", 1.0) < 0.8:
                violations.append(PillarViolation(
                    pillar=Pillar.RESPECT,
                    violation="Chose speed over quality without justified urgency",
                    context={"quality": decision.get("quality_score")},
                    severity=0.6,
                ))
        
        # Check for security shortcuts
        if decision.get("security_bypassed"):
            violations.append(PillarViolation(
                pillar=Pillar.RESPECT,
                violation="Security bypass - disrespect for user safety",
                context={"bypass_reason": decision.get("bypass_reason")},
                severity=1.0,  # Critical
            ))
        
        # Check for pattern/best practice violations
        if decision.get("ignores_best_practices"):
            violations.append(PillarViolation(
                pillar=Pillar.RESPECT,
                violation="Ignoring established patterns without documented reason",
                context={"patterns_ignored": decision.get("patterns_ignored")},
                severity=0.5,
            ))
        
        return violations


# ---------------------------------------------------------------------------
# Integration helpers
# ---------------------------------------------------------------------------

def enforce_four_pillars(
    task: dict[str, Any],
    decision: dict[str, Any],
    tyrone: TyroneProtocol,
) -> tuple[bool, list[PillarViolation]]:
    """
    Convenience function to enforce Four Pillars.
    
    Returns:
        (approved, violations) tuple
        - approved: True if no critical violations (severity < 0.9)
        - violations: List of all violations found
    """
    violations = tyrone.check_alignment(task, decision)
    
    # Block critical violations (severity >= 0.9)
    critical = [v for v in violations if v.severity >= 0.9]
    approved = len(critical) == 0
    
    if not approved:
        logger.error("CRITICAL PILLAR VIOLATIONS - task rejected:")
        for v in critical:
            logger.error("  %s", v)
    
    return approved, violations
