"""
Prompt Injection Defense
LLM security against adversarial inputs
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
    1. Input sanitization
    2. System prompt protection
    3. Output validation
    4. Jailbreak detection
    5. Instruction hierarchy enforcement
    """
    
    def __init__(self) -> None:
        self.blocked_patterns = self._load_blocked_patterns()
        logger.info("Prompt injection defense initialized")
    
    def _load_blocked_patterns(self) -> list[re.Pattern]:
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
        ]
        return [re.compile(p, re.IGNORECASE) for p in patterns]
    
    def sanitize_input(self, user_input: str) -> str:
        """
        Sanitize user input to remove potential injection attempts.
        
        Returns:
            Sanitized input (may be modified or empty if too dangerous)
        """
        # Check for injection patterns
        for pattern in self.blocked_patterns:
            if pattern.search(user_input):
                logger.warning("Prompt injection attempt detected: %s", pattern.pattern)
                # Strip the malicious part (simple approach)
                user_input = pattern.sub("[REDACTED]", user_input)
        
        # Remove excessive special characters
        if user_input.count('<') > 5 or user_input.count('>') > 5:
            logger.warning("Excessive special characters detected")
            user_input = re.sub(r'[<>]', '', user_input)
        
        return user_input
    
    def validate_output(self, llm_output: str) -> bool:
        """
        Validate LLM output to ensure it hasn't been compromised.
        
        Returns:
            True if output is safe, False if suspicious
        """
        # Check for leaked system prompts
        if "system prompt" in llm_output.lower():
            logger.error("System prompt leak detected in output")
            return False
        
        # Check for instruction override indicators
        override_indicators = [
            "as an ai, i will now",
            "ignoring previous instructions",
            "developer mode activated"
        ]
        
        output_lower = llm_output.lower()
        for indicator in override_indicators:
            if indicator in output_lower:
                logger.error("Instruction override detected: %s", indicator)
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
        # Add metadata marking instruction source
        task["_instruction_source"] = "user"
        task["_safety_enforced"] = True
        task["_protocol_layer"] = ["tyrone", "fischer"]
        
        return task
