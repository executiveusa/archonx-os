"""Bead: bead.graphbrain.runtime.v1 | Ralphy: PLAN->IMPLEMENT->TEST->EVALUATE->PATCH->REPEAT."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

SCAN_PATTERNS = [
    "README*",
    "docs/**/*",
    "src/**/*",
    "app/**/*",
    "server/**/*",
    "archonx/**/*",
    "core/**/*",
    ".github/workflows/*",
    "*.md",
    "*.json",
    "pyproject.toml",
    "requirements.txt",
]
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}")


@dataclass
class RepoDocument:
    path: str
    content: str


@dataclass
class RepoIndex:
    slug: str
    status: str
    docs: list[RepoDocument]
    terms: list[str]
    metadata: dict[str, str]


class RepoIndexer:
    def __init__(self, root: Path, repos: list[str]):
        self.root = root
        self.repos = repos

    def _slug_to_dirname(self, slug: str) -> str:
        return slug.replace("/", "__")

    def _repo_local_path(self, slug: str) -> Path:
        if slug == "executiveusa/archonx-os":
            return self.root
        return self.root / "data" / "repos" / self._slug_to_dirname(slug)

    def ensure_repo_checkout(self, slug: str) -> tuple[Path, str]:
        repo_path = self._repo_local_path(slug)
        if repo_path.exists():
            return repo_path, "available"

        repo_path.parent.mkdir(parents=True, exist_ok=True)
        clone_url = f"git@github.com:{slug}.git"
        cmd = ["git", "clone", "--depth", "1", clone_url, str(repo_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode == 0:
            return repo_path, "available"

        return repo_path, "unavailable"

    def index_repo(self, slug: str) -> RepoIndex:
        repo_path, status = self.ensure_repo_checkout(slug)
        if status != "available":
            return RepoIndex(slug=slug, status=status, docs=[], terms=[], metadata={"reason": "clone_failed"})

        docs: list[RepoDocument] = []
        for pattern in SCAN_PATTERNS:
            for path in repo_path.glob(pattern):
                if not path.is_file():
                    continue
                if ".git/" in str(path):
                    continue
                try:
                    content = path.read_text(errors="ignore")[:25000]
                except OSError:
                    continue
                docs.append(RepoDocument(path=str(path.relative_to(repo_path)), content=content))

        joined = "\n".join(doc.content for doc in docs)
        terms = [t.lower() for t in TOKEN_RE.findall(joined)]
        return RepoIndex(slug=slug, status=status, docs=docs, terms=terms, metadata={"doc_count": str(len(docs))})

    def index_all(self) -> list[RepoIndex]:
        return [self.index_repo(slug) for slug in self.repos]


def load_target_repos(root: Path) -> list[str]:
    targets_path = root / "data" / "graphbrain" / "targets.json"
    if targets_path.exists():
        payload = json.loads(targets_path.read_text())
        return payload.get("repos", [])

    return [
        "executiveusa/phone-call-assistant",
        "executiveusa/VisionClaw",
        "executiveusa/clawdbot-Whatsapp-agent",
        "executiveusa/dashboard-agent-swarm",
        "executiveusa/agent-zero-Fork",
        "executiveusa/archonx-os",
        "executiveusa/Darya-designs",
        "executiveusa/cult-directory-template",
        "executiveusa/pauli-comic-funnel",
        "executiveusa/Pauli-claw-work",
        "executiveusa/amentislibrary",
        "executiveusa/agent_flywheel_clawdbot_skills_and_integrations",
        "executiveusa/goat-alliance-scaffold",
        "executiveusa/vallarta-voyage-explorer",
        "executiveusa/paulisworld-openclaw-3d",
    ]
