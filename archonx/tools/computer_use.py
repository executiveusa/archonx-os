"""
Computer-Use Tool
=================
Tool wrapper around Orgo for agent-driven computer use.

Agents can use this tool to:
- Launch browser sessions
- Navigate to URLs
- Click, type, scroll
- Take screenshots
- Extract page content
"""

from __future__ import annotations

import logging
from typing import Any

from archonx.tools.base import BaseTool, ToolResult
from archonx.openclaw.orgo import OrgoClient

logger = logging.getLogger("archonx.tools.computer_use")


class ComputerUseTool(BaseTool):
    """Agent-accessible computer-use via Orgo VM sessions."""

    name = "computer_use"
    description = "Launch browser VMs and perform computer-use tasks via Orgo"

    def __init__(self, orgo_client: OrgoClient | None = None) -> None:
        self._orgo = orgo_client or OrgoClient()

    async def execute(self, params: dict[str, Any]) -> ToolResult:
        """
        Params:
            action: 'launch' | 'navigate' | 'click' | 'type' | 'screenshot' | 'close'
            session_id: (required for all except 'launch')
            url: (for 'navigate')
            selector: (for 'click', 'type')
            text: (for 'type')
            task: (for 'launch' — description of what to do)
        """
        action = params.get("action", "launch")

        if action == "launch":
            session = await self._orgo.create_session(
                task=params.get("task", ""),
                config=params.get("config"),
            )
            return ToolResult(
                tool=self.name,
                status="success",
                data={"session_id": session.session_id, "vm_url": session.vm_url},
            )

        session_id = params.get("session_id", "")
        if not session_id:
            return ToolResult(tool=self.name, status="error", error="session_id required")

        if action == "navigate":
            result = await self._orgo.execute_action(session_id, {"type": "navigate", "url": params.get("url", "")})
        elif action == "click":
            result = await self._orgo.execute_action(session_id, {"type": "click", "selector": params.get("selector", "")})
        elif action == "type":
            result = await self._orgo.execute_action(session_id, {"type": "type", "selector": params.get("selector", ""), "text": params.get("text", "")})
        elif action == "screenshot":
            url = await self._orgo.get_screenshot(session_id)
            result = {"screenshot_url": url}
        elif action == "close":
            await self._orgo.close_session(session_id)
            result = {"closed": True}
        else:
            return ToolResult(tool=self.name, status="error", error=f"Unknown action: {action}")

        return ToolResult(tool=self.name, status="success", data=result)
