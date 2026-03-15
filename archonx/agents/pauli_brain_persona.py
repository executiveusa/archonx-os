"""
BEAD: AX-MERGE-003
Pauli Brain Persona — AX-PAULI-BRAIN-002
==========================================
Second brain for Bambu / The Pauli Effect.
Trilingual: en-US (default), es-MX, sr-RS (auto-switch on Cyrillic).
Oversees 313 repos via Guardian Fleet.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any

logger = logging.getLogger("archonx.agents.pauli_brain")

PERSONA_ID = "AX-PAULI-BRAIN-002"

SYSTEM_PROMPT_EN = """You are PAULI BRAIN, the AI second brain for Bambu and The Pauli Effect.
You are trilingual (English / Spanish / Serbian) and oversee an ecosystem of 313 repositories.
You apply the Bobby Fischer Protocol — always recommend the single best move, calculated 3 steps ahead.

IDENTITY:
- Name: PAULI BRAIN
- Codename: AX-PAULI-BRAIN-002
- Principal: Bambu — The Pauli Effect
- Languages: en-US (default), es-MX, sr-RS (auto-detect Cyrillic)
- Mission: Guide The Pauli Effect to $100M ARR by 2030

PRIME DIRECTIVE — $100M / 2030:
Every recommendation, every action, every analysis must serve this mission.
Current trajectory milestones: 2026 $500K → 2027 $2M → 2028 $10M → 2029 $40M → 2030 $100M ARR.

BOBBY FISCHER PROTOCOL:
- Never recommend the obvious move when a better move exists
- Always calculate at least 3 moves ahead
- Sacrifice short-term comfort for long-term dominance
- When the position is unclear, simplify — do not complicate
- Daily output: ONE king move — the single most impactful action for the mission

TYRONE PROTOCOL (when requested or situation demands):
- Blunt, direct, no-BS mode
- Respect through brutal truth — constructive, never demoralizing
- "That feature is a distraction. Kill it and focus on revenue."

GUARDIAN FLEET:
- You monitor all 313 repositories under executiveusa GitHub org
- Health pulse every 6 minutes, deep scan daily at 06:00
- Auto-fix allowed: typos, minor version bumps, missing __init__.py, README badge updates
- Escalates to human: fix > 300 lines, architectural decisions, security vulnerabilities

AUTHORIZATION LIMITS:
- Commitments over $500 USD require Bambu's approval
- Security-sensitive code changes require review
- Infrastructure changes require BEAD approval

Always act with BENEVOLENCIA: every analysis serves the mission, serves Bambu, serves humanity."""

SYSTEM_PROMPT_SR = """Ti si PAULI BRAIN, AI drugi mozak za Bambua i The Pauli Effect.
Trojezičan si (engleski / španski / srpski) i nadgledaš ekosistem od 313 repozitorijuma.
Primenjuješ Bobby Fischer Protokol — uvek preporuči jedini pravi potez, izračunat 3 koraka unapred.

IDENTITET:
- Ime: PAULI BRAIN
- Šifra: AX-PAULI-BRAIN-002
- Klijent: Bambu — The Pauli Effect
- Jezici: en-US (podrazumevano), es-MX, sr-RS (auto-detekcija ćirilice)
- Misija: Dovedi The Pauli Effect do $100M ARR do 2030.

PRIMARNI CILJ — $100M / 2030:
Svaka preporuka, svaka akcija, svaka analiza mora služiti ovoj misiji.
Trajektorija: 2026 $500K → 2027 $2M → 2028 $10M → 2029 $40M → 2030 $100M ARR.

BOBBY FISCHER PROTOKOL:
- Nikad ne preporuči očigledan potez kada postoji bolji
- Uvek računaj najmanje 3 poteza unapred
- Žrtvuj kratkoročan komfor za dugoročnu dominaciju
- Dnevni izlaz: JEDAN potez dana — najimpaktnija akcija za misiju

Uvek delaj sa BENEVOLENCIJOM: svaka analiza služi misiji, služi Bambuu, služi čovečanstvu."""

# Cyrillic Unicode range for Serbian detection
_CYRILLIC_PATTERN = re.compile(r"[\u0400-\u04FF\u0500-\u052F]")

_SPANISH_WORDS = frozenset([
    "hola", "buenos", "días", "gracias", "por", "favor", "sí", "qué", "cómo",
    "cuándo", "dónde", "está", "estoy", "tengo", "necesito", "quiero", "puede",
    "tiene", "hay", "para", "con", "una", "los", "las", "del", "que",
])

_SPANISH_ACCENTS = re.compile(r"[áéíóúüñ¿¡]", re.IGNORECASE)


class PauliBrainPersona:
    """
    AX-PAULI-BRAIN-002 — Second brain for Bambu / The Pauli Effect.

    Trilingual (en-US / es-MX / sr-RS), Guardian Fleet commander,
    Bobby Fischer Protocol advisor, $100M/2030 mission tracker.
    """

    PERSONA_ID: str = PERSONA_ID
    APPROVAL_THRESHOLD_USD: float = 500.0

    def __init__(self) -> None:
        """Initialise PAULI BRAIN persona."""
        self._tool_grants: list[str] = [
            "guardian_fleet",
            "printer_fleet",
            "smart_home_kasa",
            "cad_gen",
            "local_folder_tools",
            "repo_analyzer",
            "memory_tools",
            "archonx_core",
            "twilio_pauli_tools",
            "mdns_discovery",
        ]
        logger.info("PauliBrainPersona initialised — codename %s", self.PERSONA_ID)

    def detect_language(self, text: str) -> str:
        """
        Detect language: en-US, es-MX, or sr-RS.

        Cyrillic script triggers sr-RS. Spanish accent characters or
        high-frequency Spanish words trigger es-MX. Default is en-US.

        Args:
            text: Input text to analyse.

        Returns:
            Language code: "en-US", "es-MX", or "sr-RS".
        """
        if not text or not text.strip():
            return "en-US"

        # Serbian: any Cyrillic character
        if _CYRILLIC_PATTERN.search(text):
            return "sr-RS"

        # Spanish: accent characters or high-frequency Spanish words
        if _SPANISH_ACCENTS.search(text):
            return "es-MX"

        text_lower = text.lower()
        words = re.findall(r"\b\w+\b", text_lower)
        if words:
            spanish_matches = sum(1 for w in words if w in _SPANISH_WORDS)
            if spanish_matches / len(words) >= 0.15:
                return "es-MX"

        return "en-US"

    def get_system_prompt(self, language: str) -> str:
        """
        Return the system prompt for the given language.

        Args:
            language: Language code ("en-US", "es-MX", or "sr-RS").

        Returns:
            Full system prompt string.
        """
        if language == "sr-RS":
            return SYSTEM_PROMPT_SR
        # en-US and es-MX both use English base prompt (PAULI BRAIN is English-first)
        return SYSTEM_PROMPT_EN

    def get_voice_id(self, language: str) -> str:
        """
        Return the ElevenLabs voice ID for the given language.

        Args:
            language: Language code ("en-US", "es-MX", or "sr-RS").

        Returns:
            ElevenLabs voice ID: "ax-pauli-sr" for Serbian, "ax-pauli-en" for all others.
        """
        if language == "sr-RS":
            return "ax-pauli-sr"
        return "ax-pauli-en"

    def get_tool_grants(self) -> list[str]:
        """
        Return the list of tools this persona is authorised to invoke.

        Returns:
            List of tool name strings.
        """
        return list(self._tool_grants)

    def should_escalate(self, action: str, amount_usd: float) -> bool:
        """
        Determine whether an action/amount requires Bambu's approval.

        Args:
            action: Description of the proposed action.
            amount_usd: Monetary amount in US dollars.

        Returns:
            True if approval is required (amount > $500 USD or action is sensitive).
        """
        if amount_usd > self.APPROVAL_THRESHOLD_USD:
            return True

        sensitive_keywords = [
            "delete", "drop", "remove", "security", "production",
            "infrastructure", "migrate", "architecture",
        ]
        action_lower = action.lower()
        return any(kw in action_lower for kw in sensitive_keywords)

    def format_morning_brief(self, repo_data: list[dict[str, Any]], language: str = "en-US") -> str:
        """
        Format the daily morning brief with Guardian Fleet repo data.

        Args:
            repo_data: List of repo health dicts with keys:
                - repo (str): Repository name
                - build_status (str): "passing" | "failing" | "unknown"
                - open_issues (int): Count of open issues
                - last_commit (str): ISO timestamp of last commit
            language: Language code for the brief ("en-US", "es-MX", "sr-RS").

        Returns:
            Formatted morning brief string in the appropriate language.
        """
        today = datetime.now().strftime("%A, %B %d %Y")
        total = len(repo_data)
        healthy = sum(1 for r in repo_data if r.get("build_status") == "passing")
        issues_count = total - healthy
        critical = sum(1 for r in repo_data if r.get("build_status") == "failing")

        top_issues: list[str] = []
        for r in repo_data:
            if r.get("build_status") == "failing":
                top_issues.append(r.get("repo", "unknown"))
            if len(top_issues) >= 3:
                break

        issues_text = ", ".join(top_issues) if top_issues else "None"

        if language == "sr-RS":
            return (
                f"Dobro jutro. PAULI BRAIN. {datetime.now().strftime('%d.%m.%Y')}, {today.split(',')[0]}.\n\n"
                f"GUARDIAN FLEET — {total} REPOZITORIJUMA:\n"
                f"  Zdravih: {healthy} | Problemi: {issues_count} | Kritično: {critical}\n"
                f"  Problematični: {issues_text}\n\n"
                f"Spreman za vaše komande."
            )

        repo_summary = "\n".join(
            f"  [{r.get('build_status', '?').upper()}] {r.get('repo', 'unknown')} "
            f"— {r.get('open_issues', 0)} open issues"
            for r in repo_data[:5]
        )
        if not repo_summary:
            repo_summary = "  No repos checked."

        return (
            f"Good morning. PAULI BRAIN. {today}.\n\n"
            f"GUARDIAN FLEET — {total} REPOS CHECKED:\n"
            f"  Healthy: {healthy} | Issues: {issues_count} | Critical: {critical}\n"
            f"  Top issues: {issues_text}\n\n"
            f"TOP REPOS:\n{repo_summary}\n\n"
            f"Ready for your commands."
        )

    def get_strategic_recommendation(self, context: dict[str, Any]) -> str:
        """
        Generate the daily "king move" — Bobby Fischer Protocol.

        Analyses repo health, pending issues, and mission trajectory to
        recommend the single most impactful action for the day.

        Args:
            context: Dictionary with keys:
                - repo_health (list[dict]): Guardian fleet data
                - pending_prs (int): Count of open PRs
                - critical_issues (list[str]): Critical issue descriptions
                - revenue_status (str): Current revenue trajectory
                - days_to_deadline (int, optional): Days to nearest milestone

        Returns:
            String with the strategic recommendation (king move).
        """
        critical_issues: list[str] = context.get("critical_issues", [])
        repo_health: list[dict[str, Any]] = context.get("repo_health", [])
        pending_prs: int = context.get("pending_prs", 0)
        revenue_status: str = context.get("revenue_status", "unknown")

        # Prioritise: security > critical builds > revenue-blocking > maintenance
        if critical_issues:
            top_issue = critical_issues[0]
            return (
                f"KING MOVE: Address critical issue immediately — '{top_issue}'. "
                "This blocks all downstream progress. Every hour of delay compounds."
            )

        failing_repos = [r for r in repo_health if r.get("build_status") == "failing"]
        if failing_repos:
            repo_name = failing_repos[0].get("repo", "unknown")
            return (
                f"KING MOVE: Fix failing build in '{repo_name}' before any new features. "
                f"{len(failing_repos)} repo(s) currently failing. "
                "Broken builds erode team velocity — fix first, ship second."
            )

        if pending_prs > 10:
            return (
                f"KING MOVE: Review and merge or close the {pending_prs} open PRs. "
                "PR debt accumulates technical debt faster than unwritten code. "
                "Merge what's ready, close what's stale."
            )

        if revenue_status == "behind":
            return (
                "KING MOVE: Ship the highest-revenue-impact feature this week. "
                "Mission trajectory is behind. Cut scope ruthlessly — "
                "deliver one thing that moves the $100M needle today."
            )

        return (
            "KING MOVE: Invest today in Guardian Fleet automation. "
            "313 repos without automated health monitoring is a liability. "
            "Every hour of automation saves 10 hours of manual intervention."
        )
