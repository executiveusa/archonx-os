"""
BEAD: AX-MERGE-007
CAD Gen Tool
=============
Generate CAD models from voice descriptions (voice → STL).
Mock generates a simple primitive STL when build123d is not available.
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

from archonx.tools.base import BaseTool, ToolResult

logger = logging.getLogger("archonx.tools.cad_gen")

_DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent.parent / "ops" / "cad_output"

# Minimal ASCII STL for a unit cube (mock output)
_MOCK_STL_TEMPLATE = """solid mock_primitive
  facet normal 0 0 -1
    outer loop
      vertex 0 0 0
      vertex 1 0 0
      vertex 1 1 0
    endloop
  endfacet
  facet normal 0 0 -1
    outer loop
      vertex 0 0 0
      vertex 1 1 0
      vertex 0 1 0
    endloop
  endfacet
  facet normal 0 0 1
    outer loop
      vertex 0 0 1
      vertex 1 1 1
      vertex 1 0 1
    endloop
  endfacet
  facet normal 0 0 1
    outer loop
      vertex 0 0 1
      vertex 0 1 1
      vertex 1 1 1
    endloop
  endfacet
endsolid mock_primitive
"""


class CADGenTool(BaseTool):
    """
    CAD model generator from natural language voice descriptions.

    Primary: Uses build123d for parametric CAD generation.
    Mock: Generates a simple primitive STL when build123d is unavailable.
    Output: ASCII STL files written to ops/cad_output/.
    """

    name: str = "cad_gen"
    description: str = "Generate CAD models from voice descriptions (voice → STL)"

    def __init__(self) -> None:
        """Initialise CAD gen tool and ensure output directory exists."""
        _DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self._has_build123d: bool = self._check_build123d()
        if not self._has_build123d:
            logger.warning(
                "CADGenTool: build123d not available — mock STL generation active"
            )

    def _check_build123d(self) -> bool:
        """Check if build123d is installed."""
        try:
            import build123d  # type: ignore[import-untyped]  # noqa: F401
            return True
        except ImportError:
            return False

    def run(
        self,
        bead_id: str,
        description: str,
        output_path: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate a CAD model from a text description.

        Args:
            bead_id: BEAD ID for traceability (required).
            description: Natural language description of the model to generate.
            output_path: Optional output path for the STL file.

        Returns:
            Dict with keys:
                - stl_path (str): Absolute path to the generated STL file.
                - model_description (str): Description of what was generated.
                - generation_time_ms (int): Time taken in milliseconds.
        """
        if not bead_id:
            return {"error": "bead_id is required", "status": "error"}

        if not description:
            return {"error": "description is required", "status": "error"}

        start = time.monotonic()

        # Determine output path
        slug = description[:30].lower().replace(" ", "_").replace("/", "-")
        slug = "".join(c for c in slug if c.isalnum() or c == "_")
        timestamp = int(time.time())
        filename = f"{slug}_{timestamp}.stl"

        if output_path:
            stl_path = Path(output_path)
        else:
            stl_path = _DEFAULT_OUTPUT_DIR / filename

        stl_path.parent.mkdir(parents=True, exist_ok=True)

        if self._has_build123d:
            result = self._generate_with_build123d(description, stl_path)
        else:
            result = self._generate_mock_stl(description, stl_path)

        elapsed_ms = int((time.monotonic() - start) * 1000)
        result["generation_time_ms"] = elapsed_ms
        result["stl_path"] = str(stl_path)
        logger.info(
            "CADGen: bead=%s, desc='%.40s', path=%s, time=%dms",
            bead_id,
            description,
            stl_path,
            elapsed_ms,
        )
        return result

    def _generate_mock_stl(
        self, description: str, stl_path: Path
    ) -> dict[str, Any]:
        """Write a minimal primitive STL as mock output."""
        stl_path.write_text(_MOCK_STL_TEMPLATE, encoding="utf-8")
        return {
            "model_description": (
                f"Mock primitive (unit cube) generated for description: '{description[:60]}'"
            ),
            "mock": True,
        }

    def _generate_with_build123d(
        self, description: str, stl_path: Path
    ) -> dict[str, Any]:
        """Attempt CAD generation using build123d."""
        try:
            from build123d import Box, export_stl  # type: ignore[import-untyped]

            # Simple heuristic: generate a box with dimensions from description keywords
            dim = 10.0
            words = description.lower().split()
            for i, word in enumerate(words):
                if word.isdigit():
                    dim = float(word)
                    break
                if word in ("mm", "cm") and i > 0 and words[i - 1].replace(".", "").isdigit():
                    dim = float(words[i - 1])
                    break

            box = Box(dim, dim, dim)
            export_stl(box, str(stl_path))
            return {
                "model_description": (
                    f"build123d Box({dim}x{dim}x{dim}mm) for: '{description[:60]}'"
                ),
                "mock": False,
            }
        except Exception as exc:
            logger.warning("build123d generation failed (%s) — falling back to mock", exc)
            return self._generate_mock_stl(description, stl_path)

    async def execute(self, params: dict[str, Any]) -> ToolResult:
        """
        Execute via ToolRegistry interface.

        Args:
            params: Dict with bead_id, description, and optional output_path.

        Returns:
            ToolResult wrapping run() output.
        """
        bead_id = params.get("bead_id", "")
        description = params.get("description", "")
        output_path: str | None = params.get("output_path")

        data = self.run(bead_id=bead_id, description=description, output_path=output_path)
        if "error" in data:
            return ToolResult(tool=self.name, status="error", data=data, error=data["error"])
        return ToolResult(tool=self.name, status="success", data=data)
