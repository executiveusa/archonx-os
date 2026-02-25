"""
BEAD: AX-MERGE-007
Smart Home Kasa Tool
=====================
Controls TP-Link Kasa smart home devices.
Returns simulated device states in mock mode.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from archonx.tools.base import BaseTool, ToolResult

logger = logging.getLogger("archonx.tools.smart_home_kasa")

_VALID_ACTIONS = frozenset(
    ["turn_on", "turn_off", "toggle", "get_status", "list_devices"]
)

# Simulated device registry for mock mode
_MOCK_DEVICES: list[dict[str, Any]] = [
    {"alias": "office_light", "host": "192.168.1.101", "state": False, "type": "smartplug"},
    {"alias": "desk_lamp", "host": "192.168.1.102", "state": True, "type": "smartplug"},
    {"alias": "3d_printer_outlet", "host": "192.168.1.103", "state": False, "type": "smartplug"},
    {"alias": "monitor_strip", "host": "192.168.1.104", "state": True, "type": "smartstrip"},
]


class SmartHomeKasaTool(BaseTool):
    """
    TP-Link Kasa smart home device controller.

    Supports turn_on, turn_off, toggle, get_status, and list_devices.
    Returns simulated device states when real devices are unavailable.
    """

    name: str = "smart_home_kasa"
    description: str = "Control TP-Link Kasa smart home devices"

    def __init__(self) -> None:
        """Initialise the Kasa tool."""
        self._mock_state: dict[str, bool] = {
            d["alias"]: d["state"] for d in _MOCK_DEVICES
        }
        logger.info("SmartHomeKasaTool initialised (mock state loaded)")

    def run(
        self,
        bead_id: str,
        action: str,
        device: str = "",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Execute a Kasa smart home action.

        Args:
            bead_id: BEAD ID for traceability (required).
            action: One of: turn_on, turn_off, toggle, get_status, list_devices.
            device: Device alias or IP (required for device-specific actions).
            **kwargs: Additional parameters.

        Returns:
            Dict with action result.
        """
        if not bead_id:
            return {"error": "bead_id is required", "status": "error"}

        if action not in _VALID_ACTIONS:
            return {
                "error": f"Unknown action: {action!r}. Valid: {sorted(_VALID_ACTIONS)}",
                "status": "error",
            }

        # Try live mode first; fall back to mock
        try:
            return self._live_action(action, device, **kwargs)
        except ImportError:
            logger.warning(
                "python-kasa not installed — using mock for action '%s'", action
            )
            return self._mock_action(action, device)
        except Exception as exc:
            logger.warning(
                "Kasa live action '%s' failed (%s) — using mock", action, exc
            )
            return self._mock_action(action, device)

    def _mock_action(self, action: str, device: str) -> dict[str, Any]:
        """Return simulated device state for testing."""
        if action == "list_devices":
            return {
                "status": "mock",
                "devices": [
                    {
                        "alias": d["alias"],
                        "host": d["host"],
                        "state": self._mock_state.get(d["alias"], False),
                        "type": d["type"],
                    }
                    for d in _MOCK_DEVICES
                ],
            }

        if not device:
            return {"error": "device is required for this action", "status": "error"}

        if device not in self._mock_state:
            # Try to find by partial match
            matches = [k for k in self._mock_state if device in k]
            if not matches:
                return {"error": f"Device '{device}' not found in mock registry", "status": "error"}
            device = matches[0]

        if action == "get_status":
            return {
                "status": "mock",
                "device": device,
                "is_on": self._mock_state[device],
            }

        if action == "turn_on":
            self._mock_state[device] = True
            return {"status": "mock", "device": device, "is_on": True, "action": "turned_on"}

        if action == "turn_off":
            self._mock_state[device] = False
            return {"status": "mock", "device": device, "is_on": False, "action": "turned_off"}

        if action == "toggle":
            new_state = not self._mock_state.get(device, False)
            self._mock_state[device] = new_state
            return {
                "status": "mock",
                "device": device,
                "is_on": new_state,
                "action": "toggled",
            }

        return {"status": "mock", "action": action, "device": device}

    def _live_action(self, action: str, device: str, **kwargs: Any) -> dict[str, Any]:
        """Execute a live Kasa action using python-kasa."""
        import asyncio

        from kasa import SmartDevice, SmartPlug  # type: ignore[import-untyped]

        if action == "list_devices":
            from kasa import Discover  # type: ignore[import-untyped]

            discovered = asyncio.run(Discover.discover())
            devices = [
                {"alias": d.alias, "host": ip, "state": d.is_on}
                for ip, d in discovered.items()
            ]
            return {"status": "success", "devices": devices}

        dev = SmartPlug(device)
        asyncio.run(dev.update())

        if action == "get_status":
            return {"status": "success", "device": device, "is_on": dev.is_on}

        if action == "turn_on":
            asyncio.run(dev.turn_on())
            return {"status": "success", "device": device, "is_on": True}

        if action == "turn_off":
            asyncio.run(dev.turn_off())
            return {"status": "success", "device": device, "is_on": False}

        if action == "toggle":
            if dev.is_on:
                asyncio.run(dev.turn_off())
                return {"status": "success", "device": device, "is_on": False}
            asyncio.run(dev.turn_on())
            return {"status": "success", "device": device, "is_on": True}

        return {"status": "error", "error": f"Unhandled action: {action}"}

    async def execute(self, params: dict[str, Any]) -> ToolResult:
        """
        Execute via ToolRegistry interface.

        Args:
            params: Dict with bead_id, action, device, and optional kwargs.

        Returns:
            ToolResult wrapping run() output.
        """
        bead_id = params.get("bead_id", "")
        action = params.get("action", "get_status")
        device: str = params.get("device", "")
        extra = {k: v for k, v in params.items() if k not in ("bead_id", "action", "device")}

        data = self.run(bead_id=bead_id, action=action, device=device, **extra)
        if data.get("status") == "error":
            return ToolResult(
                tool=self.name, status="error", data=data, error=data.get("error", "")
            )
        return ToolResult(tool=self.name, status="success", data=data)
