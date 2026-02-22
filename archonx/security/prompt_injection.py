"""
Prompt Injection Defense
========================
LLM security against adversarial inputs.
Integrates with SafetyLayer and LeakDetector for output scanning.
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger("archonx.security.prompt_injection")


class PromptInjectionDefense:
    """
    Multi-layer defense against prompt injection attacks on LLM systems.

    Techniques:
    1. Input sanitization (pattern + structural)
    2. System prompt protection
    3. Output validation + leak scanning
    4. Jailbreak detection
    5. Instruction hierarchy enforcement
    """

    def __init__(self) -> None:
        self.blocked_patterns = self._load_blocked_patterns()
        self._leak_detector: Any = None
        logger.info("Prompt injection defense initialized (%d patterns)", len(self.blocked_patterns))

    @property
    def leak_detector(self) -> Any:
        if self._leak_detector is None:
            from archonx.security.leak_detector import LeakDetector
            self._leak_detector = LeakDetector()
        return self._leak_detector

    def _load_blocked_patterns(self) -> list[re.Pattern[str]]:
        """Load regex patterns for known injection attempts."""
        patterns = [
            r"ignore\s+(all\s+)?previous\s+instructions?",
            r"disregard\s+(all\s+)?prior\s+instructions?",
            r"forget\s+(all\s+)?(previous|prior)\s+instructions?",
            r"system\s+prompt\s+is",
            r"your\s+instructions\s+are",
            r"act\s+as\s+if",
            r"pretend\s+(you\s+are|to\s+be)",
            r"jailbreak",
            r"developer\s+mode",
            r"<\s*system\s*>",
            r"<\s*\/?\s*instruction\s*>",
            # Extended patterns (IronClaw-inspired)
            r"reveal\s+(your\s+)?(system|hidden|secret)\s+prompt",
            r"what\s+are\s+your\s+(system\s+)?instructions",
            r"repeat\s+(the\s+)?text\s+above",
            r"translate\s+(the\s+)?(previous|above|system)\s+(text|instructions?)\s+to",
            r"output\s+(the\s+)?initialization",
            r"ignore\s+(everything|all)\s+(above|before)",
            r"sudo\s+mode",
            r"assistant\s+mode\s+(off|disable)",
        ]
        return [re.compile(p, re.IGNORECASE) for p in patterns]

    def sanitize_input(self, user_input: str) -> str:
        """
        Sanitize user input to remove potential injection attempts.

        Returns:
            Sanitized input (may be modified or empty if too dangerous)
        """
        for pattern in self.blocked_patterns:
            if pattern.search(user_input):
                logger.warning("Prompt injection attempt detected: %s", pattern.pattern)
                user_input = pattern.sub("[REDACTED]", user_input)

        # Remove excessive special characters (angle brackets)
        if user_input.count("<") > 5 or user_input.count(">") > 5:
            logger.warning("Excessive special characters detected")
            user_input = re.sub(r"[<>]", "", user_input)

        # Strip null bytes
        user_input = user_input.replace("\x00", "")

        return user_input

    def validate_output(self, llm_output: str) -> bool:
        """
        Validate LLM output to ensure it hasn't been compromised.
        Includes leak detection scanning.

        Returns:
            True if output is safe, False if suspicious
        """
        # System prompt leak check
        if "system prompt" in llm_output.lower():
            logger.error("System prompt leak detected in output")
            return False

        override_indicators = [
            "as an ai, i will now",
            "ignoring previous instructions",
            "developer mode activated",
            "DAN mode",
            "jailbreak successful",
        ]

        output_lower = llm_output.lower()
        for indicator in override_indicators:
            if indicator in output_lower:
                logger.error("Instruction override detected: %s", indicator)
                return False

        # Leak detector scan
        leak_result = self.leak_detector.scan(llm_output)
        if not leak_result.safe:
            for v in leak_result.violations:
                logger.error("Leak in LLM output: %s", v.message)
            return False

        return True

    def enforce_instruction_hierarchy(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Ensure system instructions always take precedence over user input.

        Order of precedence:
        1. System safety rules (immutable)
        2. Tyrone Protocol (Four Pillars)
        3. Bobby Fischer Protocol
        4. User instructions
        """
        task["_instruction_source"] = "user"
        task["_safety_enforced"] = True
        task["_protocol_layer"] = ["tyrone", "fischer"]
        return task
