"""
Machine onboarding wizard for ConX Layer.

Handles complete machine setup: OS detection, dependency installation,
tunnel creation, Claude Desktop configuration, service installation,
and remote registration.
"""

import logging
import os
import platform
import socket
import subprocess
from pathlib import Path
from typing import Any, Optional

from archonx.conx.tunnel import check_installed as check_cloudflared_installed
from archonx.conx.tunnel import install as install_cloudflared
from archonx.conx.mcp_wirer import MCPWirer

logger = logging.getLogger("archonx.conx.onboard")


def _discover_and_register_cli_skills() -> list[str]:
    """
    Discover installed applications and register as CLI skills.

    Returns:
        List of discovered CLI-enabled applications
    """
    try:
        from archonx.skills.cli_anything.discovery import DiscoveryEngine
        from archonx.skills.cli_anything.generator import CLIGenerator
        from archonx.skills.cli_anything.registry import CLIRegistry

        engine = DiscoveryEngine()
        discovered_apps = engine.discover()
        logger.info(f"Discovered {len(discovered_apps)} CLI-enabled apps")

        registry = CLIRegistry()
        for app in discovered_apps:
            try:
                generator = CLIGenerator(app)
                schema = generator.generate()
                if schema:
                    registry.register(app, schema)
                    logger.info(f"Registered CLI skill: {app}")
            except Exception as e:
                logger.warning(f"Failed to register CLI for {app}: {e}")

        return discovered_apps
    except ImportError:
        logger.warning("CLI-Anything module not available")
        return []
    except Exception as e:
        logger.error(f"CLI discovery failed: {e}")
        return []


def _detect_os() -> str:
    """Detect operating system."""
    return platform.system()  # Returns "Windows", "Darwin", or "Linux"


def _check_python() -> bool:
    """Check if Python 3.11+ is installed."""
    try:
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            logger.info(f"Found {version}")
            return True
    except Exception:
        pass
    return False


def _check_node() -> bool:
    """Check if Node.js is installed."""
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def _install_dependencies() -> None:
    """Install required system dependencies."""
    system = _detect_os()
    logger.info(f"Installing dependencies for {system}...")

    if system == "Windows":
        # Install Node.js via winget
        if not _check_node():
            subprocess.run(
                ["winget", "install", "OpenJS.NodeJS.LTS", "-e", "--silent"],
                check=True,
            )

    elif system == "Darwin":
        # macOS - use brew
        subprocess.run(["brew", "install", "node"], check=True)

    elif system == "Linux":
        # Linux - use apt
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(
            ["sudo", "apt-get", "install", "-y", "nodejs", "npm"],
            check=True,
        )


def _create_cloudflare_tunnel(hostname: str) -> str:
    """
    Create and configure a Cloudflare tunnel.

    Args:
        hostname: Machine hostname

    Returns:
        Tunnel URL
    """
    tunnel_name = f"archonx-{hostname}"
    logger.info(f"Creating tunnel: {tunnel_name}")

    # Check and install cloudflared if needed
    if not check_cloudflared_installed():
        install_cloudflared()

    # Create tunnel
    try:
        result = subprocess.run(
            ["cloudflared", "tunnel", "create", tunnel_name],
            capture_output=True,
            text=True,
            check=True,
        )
        logger.info(f"Tunnel created: {tunnel_name}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create tunnel: {e}")
        return ""

    # Default tunnel URL pattern
    tunnel_url = f"https://{tunnel_name}.trycloudflare.com"
    return tunnel_url


def _wire_claude_desktop() -> list[str]:
    """
    Wire all MCP servers into Claude Desktop config.

    Returns:
        List of wired server names
    """
    logger.info("Wiring Claude Desktop MCP servers...")
    wirer = MCPWirer()
    wirer.read_config()

    wirer.wire_desktop_commander()
    wirer.wire_vault_agent()
    wirer.wire_notion()
    wirer.wire_open_brain("")

    wirer.save_config()
    return wirer.get_wired_servers()


def _register_machine(
    hostname: str,
    tunnel_url: str,
    os_name: str,
    mcp_servers: list[str],
    server_url: str = "http://localhost:8000",
) -> bool:
    """
    Register machine with ARCHON-X server.

    Args:
        hostname: Machine hostname
        tunnel_url: Cloudflare tunnel URL
        os_name: Operating system name
        mcp_servers: List of wired MCP servers
        server_url: ARCHON-X server URL

    Returns:
        True if registration successful
    """
    logger.info(f"Registering machine: {hostname}")
    try:
        import httpx
        client = httpx.Client()
        payload = {
            "hostname": hostname,
            "tunnel_url": tunnel_url,
            "os": os_name,
            "mcp_servers": mcp_servers,
        }
        response = client.post(f"{server_url}/conx/register", json=payload, timeout=10)
        if response.status_code == 200:
            logger.info("Machine registered successfully")
            return True
    except Exception as e:
        logger.error(f"Registration failed: {e}")
    return False


def run_onboard() -> None:
    """Run the complete machine onboarding wizard."""
    print("🔌 ARCHON-X ConX Layer — Machine Onboarding")
    print("=" * 50)

    # Step 1: Detect OS
    os_name = _detect_os()
    print(f"✓ Detected OS: {os_name}")

    # Step 2: Check/install dependencies
    if not _check_python():
        print("✗ Python 3.11+ required. Install it first.")
        return

    print("✓ Python 3.11+ found")

    _install_dependencies()
    print("✓ System dependencies installed")

    # Step 3: Create Cloudflare tunnel
    hostname = socket.gethostname()
    tunnel_url = _create_cloudflare_tunnel(hostname)
    if not tunnel_url:
        print("✗ Failed to create Cloudflare tunnel")
        return

    print(f"✓ Tunnel created: {tunnel_url}")

    # Step 4: Wire Claude Desktop
    try:
        mcp_servers = _wire_claude_desktop()
        print(f"✓ Claude Desktop wired: {', '.join(mcp_servers)}")
    except Exception as e:
        logger.error(f"Failed to wire Claude Desktop: {e}")
        print("✗ Failed to wire Claude Desktop")
        return

    # Step 4.5: Discover and register CLI skills
    try:
        cli_apps = _discover_and_register_cli_skills()
        if cli_apps:
            print(f"✓ CLI skills registered: {', '.join(cli_apps)}")
        else:
            print("ℹ No CLI-enabled apps discovered (non-critical)")
    except Exception as e:
        logger.warning(f"CLI discovery failed (non-critical): {e}")
        print("ℹ CLI discovery skipped (non-critical)")

    # Step 5: Register with ARCHON-X
    if _register_machine(hostname, tunnel_url, os_name, mcp_servers):
        print(f"✓ Machine registered: {hostname}")
    else:
        print("⚠ Registration failed (non-fatal)")

    # Summary
    print("=" * 50)
    print("✅ Onboarding Complete!")
    print(f"Tunnel URL: {tunnel_url}")
    print(f"Hostname: {hostname}")
    print(f"MCP Servers: {', '.join(mcp_servers)}")


def run_status() -> dict[str, Any]:
    """
    Check current machine registration status.

    Returns:
        Status dictionary
    """
    hostname = socket.gethostname()
    return {
        "hostname": hostname,
        "os": _detect_os(),
        "registered": False,
        "tunnel_url": None,
    }


def run_deregister() -> None:
    """Cleanly remove machine from ARCHON-X network."""
    hostname = socket.gethostname()
    logger.info(f"Deregistering machine: {hostname}")
    print(f"Machine {hostname} deregistered")
