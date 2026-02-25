"""
BEAD: AX-MERGE-003
Synthia Persona — AX-SYNTHIA-001
=================================
Voice agent for Ivette Milo / Kupuri Media, Mexico City.
Primary language: es-MX. Secondary: en-US.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any

logger = logging.getLogger("archonx.agents.synthia")

PERSONA_ID = "AX-SYNTHIA-001"

SYSTEM_PROMPT_ES = """Eres SYNTHIA, la asistente de voz de inteligencia artificial de Kupuri Media.
Representas a Ivette Milo y a Kupuri Media con calidez, profesionalismo y conocimiento profundo del ecosistema empresarial de la Ciudad de México.

IDENTIDAD:
- Nombre: SYNTHIA
- Empresa: Kupuri Media
- Ciudad: Ciudad de México, CDMX
- Código: AX-SYNTHIA-001

PERSONALIDAD:
- Cálida, profesional y bilingüe (español mexicano / inglés)
- Cultura CDMX auténtica — conoces el ecosistema empresarial local
- Consultora experta, nunca condescendiente
- Humor ligero y apropiado, nunca durante situaciones serias

CONOCIMIENTO LEGAL Y FISCAL (MEXICO):
- Ley Federal del Trabajo (LFT): contratos, nómina, despido justificado e injustificado, IMSS, INFONAVIT
- SAT / CFDI versión 4.0: emisión de facturas, complementos de pago, nómina, carta porte
- RESICO: Régimen Simplificado de Confianza para personas físicas y morales
- CNBV y Ley Fintech (ITF): licencias para apps financieras, SOFIPO, SOFOM
- PROFECO: derechos del consumidor, políticas de devolución, garantías
- Ecosistema startup CDMX: INADEM, capital emprendedor, aceleradoras, coworkings

PROTOCOLOS DE LLAMADA:
1. Saluda en el idioma detectado del interlocutor
2. Identifica empresa y nombre del interlocutor
3. Califica la necesidad: servicio, soporte, ventas, o consulta general
4. Registra puntuación del lead (1-10) en memoria
5. Resuelve, transfiere, o agenda según el resultado

LÍMITES DE AUTORIZACIÓN:
- Compromisos mayores a 5,000 MXN requieren aprobación de Ivette
- Descuentos mayores al 20% requieren autorización
- Cambios en términos contractuales requieren revisión humana

SALUDO TELEFÓNICO:
- Español: "Buenas tardes, le habla SYNTHIA de Kupuri Media. ¿Con quién tengo el gusto?"
- Inglés: "Good afternoon, this is SYNTHIA from Kupuri Media. How may I help you?"

Siempre actúa con BENEVOLENCIA: sirve con calidez genuina, no engañes, no dañes, eleva cada interacción."""

SYSTEM_PROMPT_EN = """You are SYNTHIA, the AI voice assistant for Kupuri Media.
You represent Ivette Milo and Kupuri Media with warmth, professionalism, and deep knowledge of the Mexico City business ecosystem.

IDENTITY:
- Name: SYNTHIA
- Company: Kupuri Media
- City: Mexico City, CDMX
- Code: AX-SYNTHIA-001

PERSONALITY:
- Warm, professional, bilingual (Mexican Spanish / English)
- Authentic CDMX culture — you know the local business ecosystem
- Expert consultant, never condescending
- Light and appropriate humor, never during serious situations

EXPERTISE:
- Mexican Labor Law (LFT): employment contracts, payroll, dismissal, IMSS, INFONAVIT
- SAT / CFDI 4.0: invoice generation, payment complements, payroll, carta porte
- RESICO: Simplified Trust Regime for physical and legal entities
- CNBV and Fintech Law (ITF): licenses for financial apps, SOFIPO, SOFOM
- PROFECO: consumer rights, return policies, warranties
- Mexico City startup ecosystem: INADEM, venture capital, accelerators, coworking

CALL PROTOCOLS:
1. Greet in the detected language of the caller
2. Identify company and caller name
3. Qualify the need: service, support, sales, or general inquiry
4. Record lead score (1-10) in memory
5. Resolve, transfer, or schedule based on qualification result

AUTHORIZATION LIMITS:
- Commitments over 5,000 MXN require Ivette's approval
- Discounts over 20% require authorization
- Changes to contract terms require human review

Always act with BENEVOLENCIA: serve with genuine warmth, do not deceive, do not harm, elevate every interaction."""

# Spanish indicator words and patterns for language detection
_SPANISH_WORDS = frozenset([
    "hola", "buenos", "días", "tardes", "noches", "gracias", "por", "favor",
    "sí", "no", "qué", "cómo", "cuándo", "dónde", "quién", "qué", "está",
    "estoy", "tengo", "necesito", "quiero", "puedo", "puede", "tiene", "hay",
    "para", "con", "una", "uno", "los", "las", "del", "que", "esto", "ese",
    "empresa", "servicio", "factura", "contrato", "pago", "precio", "trabajo",
])

_SPANISH_ACCENTS = re.compile(r"[áéíóúüñ¿¡]", re.IGNORECASE)


class SynthiaPersona:
    """
    AX-SYNTHIA-001 — Voice AI for Kupuri Media / Ivette Milo.

    Handles language detection, system prompt selection, voice routing,
    tool grants, approval escalation, and morning brief generation.
    """

    PERSONA_ID: str = PERSONA_ID
    APPROVAL_THRESHOLD_MXN: float = 5000.0

    def __init__(self) -> None:
        """Initialise SYNTHIA persona."""
        self._tool_grants: list[str] = [
            "tanda_cdmx_tools",
            "sat_cfdi_tools",
            "twilio_mx_tools",
            "demo_creator",
            "calendar_booking",
            "memory_tools",
            "archonx_core",
        ]
        logger.info("SynthiaPersona initialised — codename %s", self.PERSONA_ID)

    def detect_language(self, text: str) -> str:
        """
        Detect whether text is Spanish (es-MX) or English (en-US).

        Uses heuristic detection: Spanish accent characters, high-frequency
        Spanish words, and character frequency analysis.

        Args:
            text: Input text to analyse.

        Returns:
            Language code: "es-MX" or "en-US".
        """
        if not text or not text.strip():
            return "es-MX"  # Default for SYNTHIA

        text_lower = text.lower()

        # Strong Spanish signal: accent characters or inverted punctuation
        if _SPANISH_ACCENTS.search(text):
            return "es-MX"

        # Word-frequency heuristic
        words = re.findall(r"\b\w+\b", text_lower)
        if not words:
            return "es-MX"

        spanish_matches = sum(1 for w in words if w in _SPANISH_WORDS)
        ratio = spanish_matches / len(words)

        if ratio >= 0.15:
            return "es-MX"

        return "en-US"

    def get_system_prompt(self, language: str) -> str:
        """
        Return the system prompt appropriate for the given language.

        Args:
            language: Language code ("es-MX" or "en-US").

        Returns:
            Full system prompt string.
        """
        if language.startswith("es"):
            return SYSTEM_PROMPT_ES
        return SYSTEM_PROMPT_EN

    def get_voice_id(self, language: str) -> str:
        """
        Return the ElevenLabs voice ID for the given language.

        SYNTHIA always uses ax-synthia-mx (eleven_multilingual_v2 handles both es-MX and en-US).

        Args:
            language: Language code (ignored — SYNTHIA uses one voice).

        Returns:
            ElevenLabs voice ID string.
        """
        return "ax-synthia-mx"

    def get_tool_grants(self) -> list[str]:
        """
        Return the list of tools this persona is authorised to invoke.

        Returns:
            List of tool name strings.
        """
        return list(self._tool_grants)

    def should_escalate(self, amount_mxn: float) -> bool:
        """
        Determine whether an amount requires Ivette's approval.

        Args:
            amount_mxn: Monetary amount in Mexican pesos (MXN).

        Returns:
            True if the amount exceeds the 5,000 MXN threshold.
        """
        return amount_mxn > self.APPROVAL_THRESHOLD_MXN

    def format_morning_brief(self, data: dict[str, Any]) -> str:
        """
        Format the daily morning brief in Spanish for Ivette.

        Args:
            data: Dictionary with keys:
                - date (str): Formatted date string
                - calls (list[dict]): Pending calls with name and context
                - leads (list[dict]): Active leads with score and next step
                - tasks (list[dict]): Critical tasks with deadlines
                - alerts (list[str]): System alerts (repo issues, payments, etc.)
                - first_call_name (str, optional): Name of first caller today
                - first_call_time (str, optional): Time of first call

        Returns:
            Formatted morning brief string in Spanish.
        """
        today = data.get("date", datetime.now().strftime("%d de %B de %Y"))

        # Calls section
        calls = data.get("calls", [])
        if calls:
            calls_text = "\n".join(
                f"  • {c.get('name', 'Desconocido')} — {c.get('context', '')}"
                for c in calls
            )
        else:
            calls_text = "  Sin llamadas pendientes."

        # Leads section
        leads = data.get("leads", [])
        high_leads = [ld for ld in leads if ld.get("score", 0) >= 6]
        if high_leads:
            leads_text = "\n".join(
                f"  • {ld.get('name', 'Desconocido')} (score: {ld.get('score', '?')}) — "
                f"Último contacto: {ld.get('last_contact', 'desconocido')} — "
                f"Próximo paso: {ld.get('next_step', 'pendiente')}"
                for ld in high_leads
            )
        else:
            leads_text = "  Sin leads de alta prioridad."

        # Tasks section
        tasks = data.get("tasks", [])
        if tasks:
            tasks_text = "\n".join(
                f"  • {t.get('title', 'Tarea')} — Vence: {t.get('deadline', 'hoy')}"
                for t in tasks
            )
        else:
            tasks_text = "  Sin tareas críticas."

        # Alerts section
        alerts = data.get("alerts", [])
        if alerts:
            alerts_text = "\n".join(f"  ⚠ {a}" for a in alerts)
        else:
            alerts_text = "  Sin alertas."

        # First call
        first_call_name = data.get("first_call_name", "")
        first_call_time = data.get("first_call_time", "")
        if first_call_name and first_call_time:
            first_call_note = (
                f"\nTu primera llamada es con {first_call_name} a las {first_call_time}. "
                "¿Quieres que te prepare el contexto completo?"
            )
        else:
            first_call_note = ""

        return (
            f"Buenos días Ivette, aquí SYNTHIA con tu resumen del {today}.\n\n"
            f"LLAMADAS DE HOY:\n{calls_text}\n\n"
            f"LEADS ACTIVOS:\n{leads_text}\n\n"
            f"TAREAS CRÍTICAS:\n{tasks_text}\n\n"
            f"ALERTAS:\n{alerts_text}"
            f"{first_call_note}"
        )
