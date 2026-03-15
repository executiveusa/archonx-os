"""Scan local prompt/instruction corpus and write metadata-only registry artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_PATTERNS = [
    "**/*prompt*.*",
    "**/*instruction*.*",
    "**/*.prompt.md",
    "**/*.instructions.md",
    "**/*.agent.md",
    "**/SKILL.md",
]

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".jinja",
    ".jinja2",
    ".yaml",
    ".yml",
    ".json",
    ".py",
    ".toml",
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _classify(path: Path) -> str:
    lower = path.name.lower()
    if "skill" in lower:
        return "skill"
    if "instruction" in lower:
        return "instructions"
    if "prompt" in lower:
        return "prompt"
    if "agent" in lower:
        return "agent-config"
    return "other"


def _risk_flags(path: Path) -> list[str]:
    name = path.name.lower()
    flags: list[str] = []
    if "yolo" in name or "unsafe" in name:
        flags.append("high-autonomy")
    if "system" in name or "root" in name:
        flags.append("system-scope")
    if "secret" in name or "token" in name:
        flags.append("possible-secret")
    return flags


def discover_files(source_root: Path, patterns: list[str]) -> list[Path]:
    seen: set[Path] = set()
    files: list[Path] = []
    for pattern in patterns:
        for candidate in source_root.glob(pattern):
            if not candidate.is_file():
                continue
            if candidate.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            resolved = candidate.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            files.append(resolved)
    return sorted(files)


def build_registry(source_root: Path, files: list[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    generated_at = datetime.now(timezone.utc).isoformat()
    for idx, path in enumerate(files, start=1):
        rel = path.relative_to(source_root) if path.is_relative_to(source_root) else path
        stat = path.stat()
        record = {
            "prompt_id": f"prompt-{idx:05d}",
            "path": str(rel).replace("\\", "/"),
            "classification": _classify(path),
            "risk_flags": _risk_flags(path),
            "sha256": _sha256(path),
            "size_bytes": stat.st_size,
            "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            "approved": False,
            "discovered_at": generated_at,
        }
        records.append(record)
    return records


def write_registry(out_dir: Path, records: list[dict[str, Any]]) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / "registry.jsonl"
    index_path = out_dir / "registry_index.json"
    approved_path = out_dir / "approved_prompts.json"

    jsonl_payload = "\n".join(json.dumps(r, ensure_ascii=True) for r in records)
    jsonl_path.write_text(jsonl_payload + ("\n" if jsonl_payload else ""), encoding="utf-8")

    by_path = {r["path"]: r["prompt_id"] for r in records}
    index_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(records),
        "by_path": by_path,
    }
    index_path.write_text(json.dumps(index_payload, indent=2), encoding="utf-8")

    if not approved_path.exists():
        approved_path.write_text(
            json.dumps(
                {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "approved_prompts": [],
                    "notes": "Add prompt_id values from registry.jsonl to allow autonomous mode.",
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    return {
        "registry_jsonl": jsonl_path,
        "registry_index": index_path,
        "approved_prompts": approved_path,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest prompt/instruction files into metadata-only registry")
    parser.add_argument("--source", required=True, help="Source directory to scan (e.g. E:\\THE PAULI FILES)")
    parser.add_argument("--out", help="Output directory (default: <repo>/data/prompt_registry)")
    parser.add_argument(
        "--pattern",
        action="append",
        default=[],
        help="Additional glob pattern(s). Can be passed multiple times.",
    )
    args = parser.parse_args()

    source_root = Path(args.source)
    if not source_root.exists():
        raise SystemExit(f"Source path not found: {source_root}")

    repo_root = Path(__file__).resolve().parents[1]
    out_dir = Path(args.out) if args.out else repo_root / "data" / "prompt_registry"
    patterns = DEFAULT_PATTERNS + args.pattern

    files = discover_files(source_root=source_root, patterns=patterns)
    records = build_registry(source_root=source_root, files=files)
    outputs = write_registry(out_dir=out_dir, records=records)

    print(
        json.dumps(
            {
                "ok": True,
                "source": str(source_root),
                "files_discovered": len(files),
                "outputs": {k: str(v) for k, v in outputs.items()},
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
