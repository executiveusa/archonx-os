"""
Safety Layer — IronClaw-inspired multi-component safety enforcement.

Components:
- Sanitizer: strips dangerous patterns from input/output
- Validator: schema-checks tool calls and parameter bounds
- PolicyEngine: per-agent rules, forbidden patterns, escalation triggers
- LeakDetector: blocks secret exfiltration (delegated to leak_detector module)

Adapted from pauli-iron-claw safety/mod.rs for Python/ArchonX.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger("archonx.security.safety_layer")


class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SafetyViolation:
    component: str
    severity: Severity
    message: str
    blocked: bool = True


@dataclass
class SafetyResult:
    safe: bool
    violations: list[SafetyViolation] = field(default_factory=list)

    def add(self, violation: SafetyViolation) -> None:
        self.violations.append(violation)
        if violation.blocked:
            self.safe = False


# ---------------------------------------------------------------------------
# Sanitizer
# ---------------------------------------------------------------------------

class Sanitizer:
    """Strip or neutralise dangerous patterns in text flowing to/from LLMs."""

    _DANGEROUS_PATTERNS: list[tuple[re.Pattern[str], str]] = [
        (re.compile(r"<\s*script\b[^>]*>.*?<\s*/\s*script\s*>", re.I | re.S), "[SCRIPT_REMOVED]"),
        (re.compile(r"<\s*iframe\b[^>]*>.*?<\s*/\s*iframe\s*>", re.I | re.S), "[IFRAME_REMOVED]"),
        (re.compile(r"javascript\s*:", re.I), "[JS_REMOVED]"),
        (re.compile(r"on\w+\s*=\s*[\"'][^\"']+[\"']", re.I), "[EVENT_REMOVED]"),
        (re.compile(r"\x00"), ""),  # null bytes
    ]

    def sanitize(self, text: str) -> str:
        for pattern, replacement in self._DANGEROUS_PATTERNS:
            text = pattern.sub(replacement, text)
        return text


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

@dataclass
class ToolCallSpec:
    """Schema for validating a tool invocation."""
    name: str
    required_params: list[str] = field(default_factory=list)
    max_param_length: int = 10_000
    forbidden_param_values: list[re.Pattern[str]] = field(default_factory=list)


class Validator:
    """Structural validation of tool calls."""

    def __init__(self, specs: dict[str, ToolCallSpec] | None = None) -> None:
        self._specs = specs or {}

    def register_spec(self, spec: ToolCallSpec) -> None:
        self._specs[spec.name] = spec

    def validate_tool_call(
        self, tool_name: str, params: dict[str, Any]
    ) -> SafetyResult:
        result = SafetyResult(safe=True)
        spec = self._specs.get(tool_name)
        if spec is None:
            # Unknown tools pass — gating is PolicyEngine's job
            return result

        # Required params
        for rp in spec.required_params:
            if rp not in params:
                result.add(SafetyViolation(
                    component="validator",
                    severity=Severity.MEDIUM,
                    message=f"Missing required param '{rp}' for tool '{tool_name}'",
                ))

        # Param length bounds
        for key, val in params.items():
            if isinstance(val, str) and len(val) > spec.max_param_length:
                result.add(SafetyViolation(
                    component="validator",
                    severity=Severity.HIGH,
                    message=f"Param '{key}' exceeds max length ({len(val)} > {spec.max_param_length})",
                ))

            # Forbidden values
            str_val = str(val)
            for pat in spec.forbidden_param_values:
                if pat.search(str_val):
                    result.add(SafetyViolation(
                        component="validator",
                        severity=Severity.HIGH,
                        message=f"Forbidden value pattern in param '{key}'",
                    ))

        return result


# ---------------------------------------------------------------------------
# PolicyEngine
# ---------------------------------------------------------------------------

@dataclass
class AgentPolicy:
    """Per-agent security policy."""
    agent_id: str
    allowed_tools: list[str] | None = None  # None = all allowed
    forbidden_patterns: list[re.Pattern[str]] = field(default_factory=list)
    max_tool_iterations: int = 50
    require_human_approval: bool = False


class PolicyEngine:
    """Configurable rule engine for agent behaviour."""

    def __init__(self) -> None:
        self._policies: dict[str, AgentPolicy] = {}
        self._global_forbidden: list[re.Pattern[str]] = [
            re.compile(r"rm\s+-rf\s+/", re.I),
            re.compile(r":()\s*{\s*:\|:\s*&\s*}", re.I),  # fork bomb
            re.compile(r"dd\s+if=/dev/zero", re.I),
            re.compile(r"mkfs\.", re.I),
            re.compile(r">\s*/dev/sd[a-z]", re.I),
        ]

    def set_policy(self, policy: AgentPolicy) -> None:
        self._policies[policy.agent_id] = policy

    def check(
        self,
        agent_id: str,
        tool_name: str,
        params: dict[str, Any],
        iteration: int = 0,
    ) -> SafetyResult:
        result = SafetyResult(safe=True)
        policy = self._policies.get(agent_id)

        # Tool allowlist
        if policy and policy.allowed_tools is not None:
            if tool_name not in policy.allowed_tools:
                result.add(SafetyViolation(
                    component="policy",
                    severity=Severity.HIGH,
                    message=f"Agent '{agent_id}' not allowed tool '{tool_name}'",
                ))

        # Iteration limit
        if policy and iteration > policy.max_tool_iterations:
            result.add(SafetyViolation(
                component="policy",
                severity=Severity.CRITICAL,
                message=f"Agent '{agent_id}' exceeded max tool iterations ({iteration})",
            ))

        # Global + agent-specific forbidden patterns
        combined_text = f"{tool_name} {' '.join(str(v) for v in params.values())}"

        for pat in self._global_forbidden:
            if pat.search(combined_text):
                result.add(SafetyViolation(
                    component="policy",
                    severity=Severity.CRITICAL,
                    message=f"Global forbidden pattern matched: {pat.pattern}",
                ))

        if policy:
            for pat in policy.forbidden_patterns:
                if pat.search(combined_text):
                    result.add(SafetyViolation(
                        component="policy",
                        severity=Severity.HIGH,
                        message=f"Agent-specific forbidden pattern matched",
                    ))

            # Human approval required
            if policy.require_human_approval:
                result.add(SafetyViolation(
                    component="policy",
                    severity=Severity.MEDIUM,
                    message=f"Agent '{agent_id}' requires human approval for tool use",
                    blocked=True,
                ))

        return result


# ---------------------------------------------------------------------------
# SafetyLayer — unified entry point
# ---------------------------------------------------------------------------

class SafetyLayer:
    """
    Unified safety layer wrapping Sanitizer, Validator, PolicyEngine,
    and LeakDetector (imported lazily to avoid circular deps).
    """

    def __init__(self) -> None:
        self.sanitizer = Sanitizer()
        self.validator = Validator()
        self.policy = PolicyEngine()
        self._leak_detector: Any = None
        logger.info("SafetyLayer initialized (Sanitizer + Validator + Policy + LeakDetector)")

    @property
    def leak_detector(self) -> Any:
        if self._leak_detector is None:
            from archonx.security.leak_detector import LeakDetector
            self._leak_detector = LeakDetector()
        return self._leak_detector

    def check_input(self, text: str, agent_id: str = "") -> tuple[str, SafetyResult]:
        """Sanitize + policy-check input text. Returns (sanitized_text, result)."""
        sanitized = self.sanitizer.sanitize(text)
        result = SafetyResult(safe=True)

        # Check for leaks in input (user might be trying to embed secrets)
        leak_result = self.leak_detector.scan(sanitized)
        if not leak_result.safe:
            for v in leak_result.violations:
                result.add(v)

        return sanitized, result

    def check_output(self, text: str) -> tuple[str, SafetyResult]:
        """Scan LLM output for leaks and dangerous content. Returns (sanitized_text, result)."""
        result = SafetyResult(safe=True)

        # Leak detection on output — most critical path
        leak_result = self.leak_detector.scan(text)
        if not leak_result.safe:
            for v in leak_result.violations:
                result.add(v)

        # Sanitize output
        sanitized = self.sanitizer.sanitize(text)
        return sanitized, result

    def check_tool_call(
        self,
        agent_id: str,
        tool_name: str,
        params: dict[str, Any],
        iteration: int = 0,
    ) -> SafetyResult:
        """Full safety check on a tool invocation."""
        # Validator
        val_result = self.validator.validate_tool_call(tool_name, params)

        # Policy
        pol_result = self.policy.check(agent_id, tool_name, params, iteration)

        # Merge
        merged = SafetyResult(safe=val_result.safe and pol_result.safe)
        merged.violations = val_result.violations + pol_result.violations

        # Leak-check params
        param_text = " ".join(str(v) for v in params.values())
        leak_result = self.leak_detector.scan(param_text)
        if not leak_result.safe:
            for v in leak_result.violations:
                merged.add(v)

        return merged
