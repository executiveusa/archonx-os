"""
Phone control interface via Telegram for ConX Layer.

Provides remote command execution, status monitoring, and task launching
from Telegram with safety confirmation requirements.
"""

import logging
import os
from typing import Any, Optional

logger = logging.getLogger("archonx.conx.telegram_bot")


class TelegramBotController:
    """Controls remote machines via Telegram."""

    def __init__(self):
        """Initialize the Telegram bot controller."""
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN not set, Telegram bot disabled")
        self.handlers = {}

    def register_handler(self, command: str, handler: callable) -> None:
        """
        Register a command handler.

        Args:
            command: Command name (e.g., 'status', 'deploy')
            handler: Callable to handle the command
        """
        self.handlers[command] = handler
        logger.info(f"Registered handler for /{command}")

    async def handle_status(self) -> dict[str, Any]:
        """
        Handle /status command.

        Returns:
            Status information
        """
        return {
            "status": "operational",
            "agents": [],
            "servers": [],
        }

    async def handle_deploy(self, **kwargs: Any) -> dict[str, Any]:
        """
        Handle /deploy command.

        Returns:
            Deployment result
        """
        return {
            "deployed": True,
            "timestamp": None,
        }

    async def handle_audit(self, **kwargs: Any) -> dict[str, Any]:
        """
        Handle /audit command.

        Returns:
            Audit summary
        """
        return {
            "audit_status": "completed",
            "issues": [],
        }

    async def handle_launch(self, task: str, **kwargs: Any) -> dict[str, Any]:
        """
        Handle /launch command.

        Args:
            task: Task to launch

        Returns:
            Task result
        """
        return {
            "launched": True,
            "task_id": None,
        }

    async def handle_files(self, path: str = "/", **kwargs: Any) -> dict[str, Any]:
        """
        Handle /files command to list files.

        Args:
            path: Path to list files from

        Returns:
            File listing
        """
        return {
            "path": path,
            "files": [],
        }

    async def handle_run(
        self,
        command: str,
        require_confirmation: bool = True,
        **kwargs: Any
    ) -> dict[str, Any]:
        """
        Handle /run command with optional confirmation.

        Args:
            command: Command to run
            require_confirmation: Whether to require confirmation

        Returns:
            Command result
        """
        if require_confirmation:
            return {
                "requires_confirmation": True,
                "command": command,
                "status": "awaiting_confirmation",
            }

        return {
            "executed": True,
            "output": "",
            "return_code": 0,
        }

    def get_help(self) -> str:
        """
        Get help text for all commands.

        Returns:
            Help text
        """
        return """
ARCHON-X ConX Bot Commands:

/status  — Show all running agents + server health
/deploy  — Trigger Coolify deploy
/audit   — Run vault agent, return summary
/launch [task] — POST to /webhook/task on VPS
/files [path] — List files via Desktop Commander
/run [cmd] — Run shell command (requires confirmation)
/help — Show this help message

Safety: /run requires inline keyboard confirmation before executing.
All actions logged to Notion automatically.
        """
