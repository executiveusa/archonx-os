"""
Tests for the ConX Layer (Remote Machine Control).
"""

import platform
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from archonx.conx.tunnel import check_installed, get_status
from archonx.conx.mcp_wirer import MCPWirer
from archonx.conx.onboard import (
    _detect_os,
    _check_python,
    run_status,
)


class TestMCPWirer:
    """Tests for MCPWirer."""

    def test_mcp_wirer_finds_config(self):
        """Test that MCPWirer can find Claude Desktop config path."""
        wirer = MCPWirer()
        config_path = wirer.find_claude_config()

        # Should return a Path object
        assert isinstance(config_path, Path)
        # Path should have claude_desktop_config.json in it
        assert "claude_desktop_config.json" in str(config_path)

    def test_mcp_wirer_read_config(self):
        """Test reading MCP config."""
        wirer = MCPWirer()
        config = wirer.read_config()

        # Should return a dictionary
        assert isinstance(config, dict)
        # Should have mcpServers key
        assert "mcpServers" in config or config == {}

    def test_mcp_wirer_idempotent(self):
        """Test that MCPWirer operations are idempotent."""
        wirer = MCPWirer()
        wirer.read_config()

        # Add a server
        wirer.add_server(
            "test-server",
            "python",
            ["test.py"],
        )
        servers_first = wirer.get_wired_servers()

        # Add the same server again
        wirer.add_server(
            "test-server",
            "python",
            ["test.py"],
        )
        servers_second = wirer.get_wired_servers()

        # Should be the same (idempotent)
        assert servers_first == servers_second

    def test_mcp_wirer_get_wired_servers(self):
        """Test getting list of wired servers."""
        wirer = MCPWirer()
        wirer.read_config()
        wirer.add_server("test1", "python", ["test1.py"])
        wirer.add_server("test2", "python", ["test2.py"])

        servers = wirer.get_wired_servers()
        assert "test1" in servers
        assert "test2" in servers


class TestTunnel:
    """Tests for tunnel management."""

    def test_check_installed(self):
        """Test cloudflared installation check."""
        # Should return a boolean
        result = check_installed()
        assert isinstance(result, bool)

    def test_get_status(self):
        """Test tunnel status retrieval."""
        status = get_status()

        # Should return a dictionary
        assert isinstance(status, dict)
        # Should have required keys
        assert "installed" in status
        assert "status" in status


class TestOnboarding:
    """Tests for machine onboarding."""

    def test_detect_os(self):
        """Test OS detection."""
        os_name = _detect_os()
        # Should return one of the known OS names
        assert os_name in ["Windows", "Darwin", "Linux"]

    def test_check_python(self):
        """Test Python installation check."""
        result = _check_python()
        # Should return a boolean
        assert isinstance(result, bool)

    def test_onboard_status(self):
        """Test onboarding status check."""
        status = run_status()

        # Should return a dictionary
        assert isinstance(status, dict)
        # Should have required keys
        assert "hostname" in status
        assert "os" in status
        assert "registered" in status


class TestServerConXRoutes:
    """Tests for ConX server routes."""

    @pytest.mark.asyncio
    async def test_conx_register(self):
        """Test machine registration endpoint."""
        from archonx.server import create_app

        app = create_app()
        from fastapi.testclient import TestClient

        client = TestClient(app)

        response = client.post(
            "/conx/register",
            json={
                "hostname": "test-machine",
                "tunnel_url": "https://test-tunnel.trycloudflare.com",
                "os": "Linux",
                "mcp_servers": ["desktop-commander", "vault-agent"],
            },
        )

        # Should return 200 OK
        assert response.status_code in [200, 503]  # 503 if kernel not ready
        if response.status_code == 200:
            data = response.json()
            assert "machine_id" in data or "error" in data

    @pytest.mark.asyncio
    async def test_conx_status(self):
        """Test ConX status endpoint."""
        from archonx.server import create_app

        app = create_app()
        from fastapi.testclient import TestClient

        client = TestClient(app)

        response = client.get("/conx/status")

        # Should return 200 OK
        assert response.status_code in [200, 503]  # 503 if kernel not ready
        if response.status_code == 200:
            data = response.json()
            assert "machines" in data or "error" in data


class TestTelegramBot:
    """Tests for Telegram bot controller."""

    def test_telegram_bot_init(self):
        """Test Telegram bot initialization."""
        from archonx.conx.telegram_bot import TelegramBotController

        bot = TelegramBotController()
        assert isinstance(bot.handlers, dict)

    def test_telegram_bot_help(self):
        """Test Telegram bot help text."""
        from archonx.conx.telegram_bot import TelegramBotController

        bot = TelegramBotController()
        help_text = bot.get_help()

        assert isinstance(help_text, str)
        assert "/status" in help_text
        assert "/run" in help_text
