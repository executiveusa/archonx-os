"""
Remotion Render Tool — BEAD-KM-008
====================================
Subprocess wrapper for rendering Remotion video compositions.
Agents call this to produce MP4/WebM videos from React components.

Usage:
    from archonx.tools.remotion_render import render_composition, list_compositions

    result = render_composition(
        project_path="/c/archonx-os-main/visualization/remotion",
        composition_id="KingModeIntro",
        output_path="/c/archonx-os-main/dashboard-agent-swarm/public/king-mode-intro.mp4"
    )
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger("archonx.tools.remotion_render")


def render_composition(
    project_path: str,
    composition_id: str,
    output_path: str,
    props: dict[str, Any] | None = None,
    fps: int = 30,
    width: int = 1920,
    height: int = 1080,
    codec: str = "h264",
    timeout: int = 300,
) -> dict[str, Any]:
    """
    Render a Remotion composition to video.

    Args:
        project_path: Absolute path to the Remotion project root.
        composition_id: The Composition `id` to render (must be registered in src/index.ts).
        output_path: Where to write the output video file.
        props: Optional input props dict — serialized as JSON and passed via --props.
        fps: Frames per second (default 30).
        width: Output width in pixels (default 1920).
        height: Output height in pixels (default 1080).
        codec: Video codec — h264 | h265 | vp8 | vp9 | prores (default h264).
        timeout: Max render time in seconds (default 300).

    Returns:
        dict with keys: success, output, stdout, stderr, composition_id
    """
    project = Path(project_path)
    if not project.exists():
        return {
            "success": False,
            "output": None,
            "error": f"Project path does not exist: {project_path}",
            "composition_id": composition_id,
        }

    entry = project / "src" / "index.ts"
    if not entry.exists():
        entry = project / "src" / "index.tsx"

    cmd = [
        "npx",
        "remotion",
        "render",
        str(entry),
        composition_id,
        output_path,
        f"--fps={fps}",
        f"--width={width}",
        f"--height={height}",
        f"--codec={codec}",
    ]

    if props:
        cmd += ["--props", json.dumps(props)]

    logger.info("remotion render: %s → %s", composition_id, output_path)

    try:
        result = subprocess.run(
            cmd,
            cwd=str(project),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        success = result.returncode == 0
        if success:
            logger.info("remotion render complete: %s", output_path)
        else:
            logger.error("remotion render failed: %s", result.stderr[:500])

        return {
            "success": success,
            "output": output_path if success else None,
            "stdout": result.stdout[-2000:] if result.stdout else "",
            "stderr": result.stderr[-2000:] if result.stderr else "",
            "composition_id": composition_id,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": None,
            "error": f"Render timed out after {timeout}s",
            "composition_id": composition_id,
        }
    except FileNotFoundError:
        return {
            "success": False,
            "output": None,
            "error": "npx not found — ensure Node.js is installed",
            "composition_id": composition_id,
        }


def render_still(
    project_path: str,
    composition_id: str,
    output_path: str,
    frame: int = 0,
    props: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Render a single still frame from a Remotion composition as PNG.

    Args:
        project_path: Remotion project root.
        composition_id: Composition ID.
        output_path: Output PNG path.
        frame: Which frame number to render (default 0).
        props: Optional input props.
    """
    project = Path(project_path)
    entry = project / "src" / "index.ts"
    if not entry.exists():
        entry = project / "src" / "index.tsx"

    cmd = [
        "npx",
        "remotion",
        "still",
        str(entry),
        composition_id,
        output_path,
        f"--frame={frame}",
    ]
    if props:
        cmd += ["--props", json.dumps(props)]

    try:
        result = subprocess.run(
            cmd, cwd=str(project), capture_output=True, text=True, timeout=120
        )
        return {
            "success": result.returncode == 0,
            "output": output_path if result.returncode == 0 else None,
            "stderr": result.stderr[-1000:] if result.stderr else "",
        }
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return {"success": False, "output": None, "error": str(exc)}


def list_compositions(project_path: str) -> dict[str, Any]:
    """
    List all registered compositions in a Remotion project.

    Returns dict with 'compositions' list or 'error' string.
    """
    project = Path(project_path)
    entry = project / "src" / "index.ts"
    if not entry.exists():
        entry = project / "src" / "index.tsx"

    cmd = ["npx", "remotion", "compositions", str(entry), "--json"]

    try:
        result = subprocess.run(
            cmd, cwd=str(project), capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                return {"success": True, "compositions": data}
            except json.JSONDecodeError:
                return {"success": True, "compositions": [], "raw": result.stdout}
        return {"success": False, "error": result.stderr[:500]}
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return {"success": False, "error": str(exc)}
