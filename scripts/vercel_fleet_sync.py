"""Sync Vercel project inventory into ArchonX data artifacts.

Usage:
    python scripts/vercel_fleet_sync.py

Required env vars:
    VERCEL_TOKEN

Optional env vars:
    VERCEL_TEAM_ID
    VERCEL_API_BASE (defaults to https://api.vercel.com)
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx


def fetch_projects(token: str, team_id: str | None, api_base: str) -> list[dict[str, Any]]:
    headers = {"Authorization": f"Bearer {token}"}
    projects: list[dict[str, Any]] = []
    next_cursor: str | None = None

    with httpx.Client(timeout=30.0) as client:
        while True:
            params: dict[str, Any] = {"limit": 100}
            if team_id:
                params["teamId"] = team_id
            if next_cursor:
                params["until"] = next_cursor

            response = client.get(f"{api_base}/v9/projects", headers=headers, params=params)
            response.raise_for_status()
            payload = response.json()

            batch = payload.get("projects", [])
            projects.extend(batch)

            pagination = payload.get("pagination") or {}
            next_cursor = pagination.get("next")
            if not next_cursor:
                break

    return projects


def build_repo_map(projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for project in projects:
        link = project.get("link") or {}
        row = {
            "projectId": project.get("id"),
            "name": project.get("name"),
            "framework": project.get("framework"),
            "createdAt": project.get("createdAt"),
            "updatedAt": project.get("updatedAt"),
            "gitProvider": link.get("type"),
            "repo": link.get("repo"),
            "org": link.get("org"),
            "repoId": link.get("repoId"),
            "productionBranch": (project.get("gitComments") or {}).get("productionBranch"),
        }
        rows.append(row)
    return rows


def main() -> int:
    token = os.getenv("VERCEL_TOKEN", "").strip()
    if not token:
        raise SystemExit("VERCEL_TOKEN is required")

    team_id = os.getenv("VERCEL_TEAM_ID", "").strip() or None
    api_base = os.getenv("VERCEL_API_BASE", "https://api.vercel.com").strip()

    root = Path(__file__).resolve().parents[1]
    out_dir = root / "data" / "vercel"
    out_dir.mkdir(parents=True, exist_ok=True)

    projects = fetch_projects(token=token, team_id=team_id, api_base=api_base)
    repo_map = build_repo_map(projects)

    snapshot = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "projectCount": len(projects),
        "projects": projects,
    }
    mapping = {
        "generatedAt": snapshot["generatedAt"],
        "mappedCount": len(repo_map),
        "rows": repo_map,
    }

    (out_dir / "projects.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    (out_dir / "repo_map.json").write_text(json.dumps(mapping, indent=2), encoding="utf-8")

    print(json.dumps({"ok": True, "projects": len(projects), "outputDir": str(out_dir)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
