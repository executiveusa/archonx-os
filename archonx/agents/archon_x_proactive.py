"""
BEAD: AX-MERGE-008
Archon-X Proactive Engine
==========================
Generates morning briefs and event-driven voice messages for
SYNTHIA (AX-SYNTHIA-001) and PAULI BRAIN (AX-PAULI-BRAIN-002).
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from archonx.agents.archon_x_guardian_fleet import GuardianFleet
from archonx.agents.pauli_brain_persona import PauliBrainPersona
from archonx.agents.synthia_persona import SynthiaPersona

logger = logging.getLogger("archonx.agents.archon_x_proactive")

# Event type constants
EVENT_BUILD_FAILURE = "build_failure"
EVENT_NEW_ISSUE = "new_issue"
EVENT_INBOUND_CALL = "inbound_call"
EVENT_SECURITY_ALERT = "security_alert"


class ProactiveEngine:
    """
    Proactive voice and message generation engine.

    Monitors Guardian Fleet state and generates natural language
    morning briefs, event-triggered notifications, and daily
    strategic recommendations for active personas.
    """

    def __init__(self) -> None:
        """Initialise proactive engine with fleet and persona instances."""
        self._fleet = GuardianFleet()
        self._synthia = SynthiaPersona()
        self._pauli = PauliBrainPersona()
        logger.info("ProactiveEngine initialised")

    def generate_morning_brief(self, persona_id: str) -> str:
        """
        Generate a natural language morning brief for the given persona.

        - SYNTHIA: Spanish brief for Ivette — calls, leads, tasks, alerts.
        - PAULI BRAIN: English (or Serbian) brief for Bambu — fleet status, king move.

        Args:
            persona_id: Persona ID string ("AX-SYNTHIA-001" or "AX-PAULI-BRAIN-002").

        Returns:
            Morning brief as a plain text string ready for TTS.
        """
        repo_data = self._fleet.check_all_repos(limit=10)

        if persona_id == "AX-SYNTHIA-001":
            # Synthia morning brief: build from fleet alerts into call/task format
            alerts = []
            for r in repo_data:
                if r.get("build_status") == "failing":
                    alerts.append(f"Repo {r['repo']} build failing")
                issues = r.get("open_issues", 0)
                if isinstance(issues, int) and issues > 10:
                    alerts.append(f"Repo {r['repo']} has {issues} open issues")

            data: dict[str, Any] = {
                "date": datetime.now().strftime("%d de %B de %Y"),
                "calls": [],
                "leads": [],
                "tasks": [],
                "alerts": alerts[:5] if alerts else [],
            }
            return self._synthia.format_morning_brief(data)

        if persona_id == "AX-PAULI-BRAIN-002":
            return self._pauli.format_morning_brief(repo_data, language="en-US")

        return f"Good morning. No morning brief configured for persona '{persona_id}'."

    def trigger_on_event(
        self,
        event_type: str,
        event_data: dict[str, Any],
        persona_id: str,
    ) -> str | None:
        """
        Generate a voice message in response to a system event.

        Args:
            event_type: One of: build_failure, new_issue, inbound_call, security_alert.
            event_data: Event-specific data dict.
            persona_id: Active persona to use for tone/language.

        Returns:
            Voice message string, or None if no action is needed.
        """
        logger.info(
            "ProactiveEngine: event=%s, persona=%s, data=%s",
            event_type,
            persona_id,
            event_data,
        )

        if event_type == EVENT_BUILD_FAILURE:
            repo = event_data.get("repo", "unknown")
            branch = event_data.get("branch", "main")
            if persona_id == "AX-SYNTHIA-001":
                return (
                    f"Alerta: el build del repositorio {repo} en la rama {branch} ha fallado. "
                    "Por favor revisa el pipeline lo antes posible."
                )
            return (
                f"ALERT: Build failure in '{repo}' on branch '{branch}'. "
                "Guardian Fleet has logged the event. Immediate review recommended."
            )

        if event_type == EVENT_NEW_ISSUE:
            repo = event_data.get("repo", "unknown")
            severity = event_data.get("severity", "normal")
            title = event_data.get("title", "New issue")
            if severity == "critical":
                if persona_id == "AX-SYNTHIA-001":
                    return (
                        f"Issue crítico en {repo}: {title}. "
                        "Se requiere atención inmediata."
                    )
                return (
                    f"CRITICAL ISSUE in '{repo}': {title}. "
                    "Escalating to Guardian Fleet — immediate action required."
                )
            # Non-critical: log but don't interrupt
            logger.info("New issue (non-critical): repo=%s, title=%s", repo, title)
            return None

        if event_type == EVENT_INBOUND_CALL:
            caller = event_data.get("from_number", "unknown")
            if persona_id == "AX-SYNTHIA-001":
                return (
                    f"Llamada entrante de {caller}. SYNTHIA está lista para atender."
                )
            return f"Inbound call from {caller}. PAULI BRAIN standing by."

        if event_type == EVENT_SECURITY_ALERT:
            repo = event_data.get("repo", "unknown")
            cve = event_data.get("cve", "")
            msg = f"SECURITY ALERT in '{repo}'"
            if cve:
                msg += f" — {cve}"
            msg += ". Escalating to Iron Claw. Human review required immediately."
            logger.critical("Security alert: %s", msg)
            return msg

        logger.warning("ProactiveEngine: unknown event_type '%s'", event_type)
        return None

    def get_strategic_recommendation(self, persona_id: str) -> str:
        """
        Generate the daily strategic recommendation (king move).

        Only meaningful for PAULI BRAIN. SYNTHIA returns a daily call tip.

        Args:
            persona_id: Persona ID to generate recommendation for.

        Returns:
            Strategic recommendation string.
        """
        if persona_id != "AX-PAULI-BRAIN-002":
            return (
                "Daily tip for SYNTHIA: Focus on the highest-priority lead today. "
                "One quality follow-up call is worth five cold attempts."
            )

        repo_data = self._fleet.check_all_repos(limit=10)
        failing_repos = [r for r in repo_data if r.get("build_status") == "failing"]
        total_issues = sum(r.get("open_issues", 0) for r in repo_data if isinstance(r.get("open_issues"), int))

        context: dict[str, Any] = {
            "repo_health": repo_data,
            "pending_prs": 0,
            "critical_issues": [r["repo"] for r in failing_repos],
            "revenue_status": "on_track",
        }

        return self._pauli.get_strategic_recommendation(context)
