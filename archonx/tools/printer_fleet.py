"""
BEAD: AX-MERGE-007
Printer Fleet Tool
===================
Controls 3D printer fleet via Moonraker/OctoPrint/PrusaLink APIs.
Only PAULI BRAIN (AX-PAULI-BRAIN-002) can invoke printer actions.
Mock mode when no printer host is configured.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from archonx.tools.base import BaseTool, ToolResult

logger = logging.getLogger("archonx.tools.printer_fleet")

_SAFE_PERSONAS = {"AX-PAULI-BRAIN-002"}
_PRINTER_HOST_ENV = "PRINTER_HOST"
_TIMEOUT = 10.0

_VALID_ACTIONS = frozenset(
    ["status", "print_file", "cancel", "pause", "resume", "get_temperature"]
)


class PrinterFleetTool(BaseTool):
    """
    3D printer fleet controller for Moonraker/OctoPrint/PrusaLink.

    Enforces persona safety gate: only AX-PAULI-BRAIN-002 can invoke
    printer actions. Mock mode when no printer host is configured.
    """

    name: str = "printer_fleet"
    description: str = "Control 3D printer fleet (Moonraker/OctoPrint/PrusaLink)"

    def __init__(self) -> None:
        """Initialise printer fleet tool."""
        self._default_host: str | None = os.environ.get(_PRINTER_HOST_ENV)
        self._mock: bool = not bool(self._default_host)
        if self._mock:
            logger.warning(
                "PrinterFleetTool: %s not set — mock mode", _PRINTER_HOST_ENV
            )

    def run(
        self,
        bead_id: str,
        action: str,
        printer_host: str | None = None,
        persona_id: str = "AX-PAULI-BRAIN-002",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Execute a printer fleet action.

        Args:
            bead_id: BEAD ID for traceability (required).
            action: One of: status, print_file, cancel, pause, resume, get_temperature.
            printer_host: Printer API host URL (falls back to PRINTER_HOST env var).
            persona_id: Invoking persona — must be AX-PAULI-BRAIN-002.
            **kwargs: Action-specific parameters (e.g. filename for print_file).

        Returns:
            Dict with action result data.

        Raises:
            PermissionError: If persona is not authorised.
            ValueError: If action is unknown or bead_id is missing.
        """
        if not bead_id:
            return {"error": "bead_id is required", "status": "error"}

        # Safety gate
        if persona_id not in _SAFE_PERSONAS:
            logger.warning(
                "PrinterFleet: access denied for persona %s (bead=%s)", persona_id, bead_id
            )
            return {
                "error": f"Persona {persona_id!r} is not authorised to control the printer fleet.",
                "status": "denied",
            }

        if action not in _VALID_ACTIONS:
            return {
                "error": f"Unknown action: {action!r}. Valid: {sorted(_VALID_ACTIONS)}",
                "status": "error",
            }

        host = printer_host or self._default_host
        if not host or self._mock:
            return self._mock_action(action, host, **kwargs)

        return self._live_action(action, host, bead_id, **kwargs)

    def _mock_action(
        self, action: str, host: str | None, **kwargs: Any
    ) -> dict[str, Any]:
        """Return simulated printer response."""
        logger.info("PrinterFleet mock action: %s", action)
        mock_responses: dict[str, dict[str, Any]] = {
            "status": {
                "status": "mock",
                "printer_status": "idle",
                "filename": None,
                "progress": 0.0,
                "host": host or "not_configured",
            },
            "get_temperature": {
                "status": "mock",
                "hotend": {"actual": 22.5, "target": 0.0},
                "bed": {"actual": 21.0, "target": 0.0},
                "host": host or "not_configured",
            },
            "print_file": {
                "status": "mock",
                "message": f"Mock print started: {kwargs.get('filename', 'unknown.gcode')}",
            },
            "cancel": {"status": "mock", "message": "Mock cancel sent"},
            "pause": {"status": "mock", "message": "Mock pause sent"},
            "resume": {"status": "mock", "message": "Mock resume sent"},
        }
        return mock_responses.get(action, {"status": "mock", "action": action})

    def _live_action(
        self, action: str, host: str, bead_id: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Execute a live Moonraker API action."""
        try:
            with httpx.Client(timeout=_TIMEOUT) as client:
                if action == "status":
                    resp = client.get(f"{host}/printer/info")
                    resp.raise_for_status()
                    data: dict[str, Any] = resp.json()
                    return {"status": "success", "data": data}

                if action == "get_temperature":
                    resp = client.get(
                        f"{host}/printer/objects/query",
                        params={"extruder": None, "heater_bed": None},
                    )
                    resp.raise_for_status()
                    return {"status": "success", "data": resp.json()}

                if action == "print_file":
                    filename = kwargs.get("filename", "")
                    if not filename:
                        return {"status": "error", "error": "filename required for print_file"}
                    resp = client.post(
                        f"{host}/printer/print/start",
                        json={"filename": filename},
                    )
                    resp.raise_for_status()
                    return {"status": "success", "data": resp.json()}

                if action == "cancel":
                    resp = client.post(f"{host}/printer/print/cancel")
                    resp.raise_for_status()
                    return {"status": "success"}

                if action == "pause":
                    resp = client.post(f"{host}/printer/print/pause")
                    resp.raise_for_status()
                    return {"status": "success"}

                if action == "resume":
                    resp = client.post(f"{host}/printer/print/resume")
                    resp.raise_for_status()
                    return {"status": "success"}

        except httpx.HTTPError as exc:
            logger.error("PrinterFleet HTTP error for action %s: %s", action, exc)
            return {"status": "error", "error": str(exc)}
        except Exception as exc:
            logger.exception("PrinterFleet unexpected error: %s", exc)
            return {"status": "error", "error": str(exc)}

        return {"status": "error", "error": f"Unhandled action: {action}"}

    async def execute(self, params: dict[str, Any]) -> ToolResult:
        """
        Execute via ToolRegistry interface.

        Args:
            params: Dict with bead_id, action, and optional printer_host and kwargs.

        Returns:
            ToolResult wrapping run() output.
        """
        bead_id = params.get("bead_id", "")
        action = params.get("action", "status")
        printer_host: str | None = params.get("printer_host")
        persona_id = params.get("persona_id", "AX-PAULI-BRAIN-002")
        extra = {k: v for k, v in params.items() if k not in ("bead_id", "action", "printer_host", "persona_id")}

        data = self.run(
            bead_id=bead_id,
            action=action,
            printer_host=printer_host,
            persona_id=persona_id,
            **extra,
        )
        status = data.get("status", "error")
        if status in ("error", "denied"):
            return ToolResult(
                tool=self.name, status="error", data=data, error=data.get("error", "")
            )
        return ToolResult(tool=self.name, status="success", data=data)
