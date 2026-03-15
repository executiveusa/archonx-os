"""Bead: bead.graphbrain.runtime.v1 | Ralphy: PLAN->IMPLEMENT->TEST->EVALUATE->PATCH->REPEAT."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

REQUIRED_FILES = [
    "ARCHONX.json",
    "HEART.md",
    "SOUL.md",
    "TOOLBOX.md",
    "SECURITY.md",
    "REPORTING.md",
    "OWNERSHIP.md",
    "WEBHOOKS.json",
    "AGENTS.md",
]


@dataclass
class PropagationResult:
    repo: str
    status: str
    detail: str


class Propagator:
    def __init__(self, root: Path, template_dir: Path):
        self.root = root
        self.template_dir = template_dir
        self.workspace = root / "data" / "propagation"
        self.workspace.mkdir(parents=True, exist_ok=True)

    def init_repo(self, repo_name: str, repo_root: Path) -> None:
        archonx_dir = repo_root / ".archonx"
        archonx_dir.mkdir(parents=True, exist_ok=True)
        for name in REQUIRED_FILES:
            template = self.template_dir / name
            target = archonx_dir / name
            text = template.read_text()
            text = text.replace("__REPO__", repo_name)
            target.write_text(text)

        scripts_dir = repo_root / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        script_target = scripts_dir / "archonx_daily_report.py"
        script_text = (self.root / "scripts" / "archonx_daily_report.py").read_text()
        script_target.write_text(script_text.replace("__REPO__", repo_name))

        workflows_dir = repo_root / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(
            self.root / "templates" / "archonx" / "archonx-report.yml",
            workflows_dir / "archonx-report.yml",
        )

    def propagate_all(self, repos: list[str]) -> list[PropagationResult]:
        results: list[PropagationResult] = []
        for slug in repos:
            if slug == "executiveusa/archonx-os":
                self.init_repo(slug, self.root)
                results.append(PropagationResult(repo=slug, status="updated_local", detail="template_synced"))
                continue

            repo_dir = self.workspace / slug.replace("/", "__")
            clone_cmd = ["git", "clone", "--depth", "1", f"git@github.com:{slug}.git", str(repo_dir)]
            proc = subprocess.run(clone_cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                results.append(PropagationResult(repo=slug, status="dry_run", detail="clone_failed_no_credentials"))
                continue

            self.init_repo(slug, repo_dir)
            results.append(PropagationResult(repo=slug, status="pr_ready", detail=str(repo_dir)))

        report_path = self.root / "data" / "reports" / "propagation_latest.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps([result.__dict__ for result in results], indent=2) + "\n"
        )
        return results
