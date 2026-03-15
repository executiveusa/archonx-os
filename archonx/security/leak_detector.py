"""
Leak Detector — Scans text for secret exfiltration patterns.

Adapted from IronClaw's LeakDetector. Blocks API keys, tokens, passwords,
PII, and internal URLs from appearing in LLM output or tool params.
"""

from __future__ import annotations

import logging
import math
import re
from dataclasses import dataclass, field

from archonx.security.safety_layer import SafetyResult, SafetyViolation, Severity

logger = logging.getLogger("archonx.security.leak_detector")


@dataclass
class LeakPattern:
    name: str
    pattern: re.Pattern[str]
    severity: Severity = Severity.CRITICAL


class LeakDetector:
    """Scan text for leaked secrets, API keys, tokens, PII."""

    def __init__(self, extra_patterns: list[LeakPattern] | None = None) -> None:
        self._patterns = self._default_patterns()
        if extra_patterns:
            self._patterns.extend(extra_patterns)
        logger.info("LeakDetector initialized with %d patterns", len(self._patterns))

    @staticmethod
    def _default_patterns() -> list[LeakPattern]:
        return [
            # Cloud provider keys
            LeakPattern("AWS Access Key", re.compile(r"AKIA[0-9A-Z]{16}")),
            LeakPattern("AWS Secret Key", re.compile(r"(?i)aws[_\-]?secret[_\-]?access[_\-]?key\s*[:=]\s*\S{20,}")),
            # Anthropic / OpenAI
            LeakPattern("Anthropic API Key", re.compile(r"sk-ant-[a-zA-Z0-9\-_]{20,}")),
            LeakPattern("OpenAI API Key", re.compile(r"sk-[a-zA-Z0-9]{20,}")),
            # GitHub
            LeakPattern("GitHub PAT (classic)", re.compile(r"ghp_[a-zA-Z0-9]{36}")),
            LeakPattern("GitHub PAT (fine-grained)", re.compile(r"github_pat_[a-zA-Z0-9_]{22,}")),
            LeakPattern("GitHub OAuth", re.compile(r"gho_[a-zA-Z0-9]{36}")),
            # Slack
            LeakPattern("Slack Bot Token", re.compile(r"xoxb-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{24}")),
            LeakPattern("Slack User Token", re.compile(r"xoxp-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{24,}")),
            # Generic secrets
            LeakPattern("Bearer Token", re.compile(r"Bearer\s+[a-zA-Z0-9\-_.~+/]{20,}")),
            LeakPattern("Private Key Header", re.compile(r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----")),
            LeakPattern("Basic Auth", re.compile(r"(?i)basic\s+[A-Za-z0-9+/=]{20,}")),
            # Database
            LeakPattern("Postgres URI", re.compile(r"postgres(?:ql)?://[^\s]{10,}")),
            LeakPattern("MySQL URI", re.compile(r"mysql://[^\s]{10,}")),
            LeakPattern("MongoDB URI", re.compile(r"mongodb(?:\+srv)?://[^\s]{10,}")),
            # PII
            LeakPattern("SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
            LeakPattern("Credit Card (Visa)", re.compile(r"\b4[0-9]{12}(?:[0-9]{3})?\b")),
            LeakPattern("Credit Card (MC)", re.compile(r"\b5[1-5][0-9]{14}\b")),
            # Internal infrastructure
            LeakPattern("Internal IP (10.x)", re.compile(r"\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")),
            LeakPattern("Internal IP (172.16-31)", re.compile(r"\b172\.(?:1[6-9]|2[0-9]|3[01])\.\d{1,3}\.\d{1,3}\b")),
            LeakPattern("Internal IP (192.168)", re.compile(r"\b192\.168\.\d{1,3}\.\d{1,3}\b")),
            # Generic password assignment
            LeakPattern("Password Assignment", re.compile(r"(?i)(?:password|passwd|pwd)\s*[:=]\s*\S{6,}")),
        ]

    def scan(self, text: str) -> SafetyResult:
        """Scan text for leaked secrets."""
        result = SafetyResult(safe=True)
        for lp in self._patterns:
            matches = lp.pattern.findall(text)
            if matches:
                result.add(SafetyViolation(
                    component="leak_detector",
                    severity=lp.severity,
                    message=f"Potential {lp.name} leak detected ({len(matches)} match(es))",
                    blocked=lp.severity in (Severity.CRITICAL, Severity.HIGH),
                ))
                logger.warning("Leak detected: %s (%d matches)", lp.name, len(matches))
        # High-entropy check for generic base64 blobs near secret keywords
        result = self._check_high_entropy(text, result)
        return result

    def _check_high_entropy(self, text: str, result: SafetyResult) -> SafetyResult:
        """Flag high-entropy strings adjacent to secret-related keywords."""
        secret_keywords = re.compile(
            r"(?i)(?:key|token|secret|password|credential|auth)\s*[:=]\s*\"?([A-Za-z0-9+/=\-_]{32,})\"?",
        )
        for match in secret_keywords.finditer(text):
            value = match.group(1)
            entropy = self._shannon_entropy(value)
            if entropy > 4.0:
                result.add(SafetyViolation(
                    component="leak_detector",
                    severity=Severity.HIGH,
                    message=f"High-entropy secret-like value detected (entropy={entropy:.2f})",
                ))
        return result

    @staticmethod
    def _shannon_entropy(data: str) -> float:
        if not data:
            return 0.0
        freq: dict[str, int] = {}
        for c in data:
            freq[c] = freq.get(c, 0) + 1
        length = len(data)
        return -sum(
            (count / length) * math.log2(count / length)
            for count in freq.values()
        )

    def redact(self, text: str) -> str:
        """Return text with all detected secrets redacted."""
        for lp in self._patterns:
            text = lp.pattern.sub(f"[REDACTED:{lp.name}]", text)
        return text
