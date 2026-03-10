"""
Cloudflare Tunnel manager for ConX Layer.

Handles tunnel lifecycle: check installation, install cloudflared,
create/start tunnels, and system service installation.
"""

import os
import platform
import subprocess
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("archonx.conx.tunnel")


def check_installed() -> bool:
    """Check if cloudflared is installed on the system."""
    try:
        result = subprocess.run(
            ["cloudflared", "--version"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def install() -> None:
    """Install cloudflared for the current OS (Windows/Mac/Linux)."""
    system = platform.system()
    logger.info(f"Installing cloudflared for {system}...")

    if system == "Windows":
        # Use winget on Windows
        subprocess.run(
            ["winget", "install", "Cloudflare.cloudflared", "-e", "--silent"],
            check=True,
        )
    elif system == "Darwin":
        # Use brew on macOS
        subprocess.run(["brew", "install", "cloudflare/cloudflare/cloudflared"], check=True)
    elif system == "Linux":
        # Use apt on Linux (Debian/Ubuntu)
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(
            ["sudo", "apt-get", "install", "-y", "cloudflared"],
            check=True,
        )
    else:
        raise RuntimeError(f"Unsupported OS: {system}")

    logger.info("cloudflared installed successfully")


def create_tunnel(name: str) -> str:
    """
    Create a Cloudflare tunnel.

    Args:
        name: Tunnel name (e.g., 'archonx-hostname')

    Returns:
        Tunnel ID
    """
    logger.info(f"Creating tunnel: {name}")
    result = subprocess.run(
        ["cloudflared", "tunnel", "create", name],
        capture_output=True,
        text=True,
        check=True,
    )
    # Extract tunnel ID from output
    tunnel_id = result.stdout.strip().split()[-1] if result.stdout else ""
    logger.info(f"Tunnel created: {tunnel_id}")
    return tunnel_id


def start_tunnel(config_path: str) -> None:
    """
    Start a tunnel as a background process.

    Args:
        config_path: Path to cloudflared config file
    """
    logger.info(f"Starting tunnel from config: {config_path}")
    subprocess.Popen(
        ["cloudflared", "tunnel", "run", "--config", config_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def install_service(config_path: str) -> None:
    """
    Install tunnel as a system service.

    Args:
        config_path: Path to cloudflared config file
    """
    logger.info("Installing tunnel as system service...")
    system = platform.system()

    if system == "Windows":
        subprocess.run(
            ["cloudflared", "service", "install", "--config", config_path],
            check=True,
        )
    elif system in ["Darwin", "Linux"]:
        subprocess.run(
            ["sudo", "cloudflared", "service", "install", "--config", config_path],
            check=True,
        )

    logger.info("Service installed successfully")


def get_status() -> dict:
    """
    Get tunnel status information.

    Returns:
        Dictionary with keys: name, domain, status, uptime
    """
    try:
        result = subprocess.run(
            ["cloudflared", "tunnel", "list"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return {
                "installed": True,
                "status": "running",
                "version": _get_version(),
            }
    except Exception as e:
        logger.error(f"Error getting tunnel status: {e}")

    return {
        "installed": check_installed(),
        "status": "unknown",
        "version": None,
    }


def _get_version() -> Optional[str]:
    """Get cloudflared version."""
    try:
        result = subprocess.run(
            ["cloudflared", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None
