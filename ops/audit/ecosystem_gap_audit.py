#!/usr/bin/env python3
"""BEAD-101 (PAULIWHEEL): ecosystem intended-vs-actual gap audit.

Stages:
- PLAN: load required architecture domains and detection rules.
- IMPLEMENT: scan target repositories and detect signals.
- TEST: emit deterministic JSON + markdown reports.
- EVALUATE: classify fully/partial/missing/misaligned components.
- PATCH: generate remediation instructions per missing capability.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Rule:
    component: str
    patterns: tuple[str, ...]
    kind: str = "file"  # file|content


RULES: tuple[Rule, ...] = (
    Rule("toolbox_md", ("toolbox.md", "Toolbox.md", "toolbox/toolbox.json")),
    Rule("llm_txt", ("LLM.txt", "llm.txt", "public/llm.txt")),
    Rule("repo_identity_file", ("archonx/ARCHONX.json", "archonx-config.json", "archonx/identity.json")),
    Rule("repo_webhook_to_archonx", ("webhook", "report back", "heartbeat"), kind="content"),
    Rule("daily_self_report_job", ("cron", "schedule", "heartbeat"), kind="content"),
    Rule("security_self_scan", ("trivy", "codeql", "osv", "security scan"), kind="content"),
    Rule("version_reporting", ("version", "release-notes", "changelog"), kind="content"),
    Rule("cross_repo_sync_check", ("sync", "ecosystem", "policy-sync"), kind="content"),
    Rule("openclaw_fork_integration", ("openclaw", "claw"), kind="content"),
    Rule("visionclaw_integration", ("visionclaw",), kind="content"),
    Rule("subagent_agent_zero", ("agent zero", "agent-zero"), kind="content"),
    Rule("subagent_devika", ("devika",), kind="content"),
    Rule("global_sso_system", ("sso", "oauth", "jwt", "paseto"), kind="content"),
    Rule("secrets_vault_system", ("vault", "secrets", "encryption"), kind="content"),
    Rule("json_secrets_upload_mechanism", ("json secrets", "secrets upload"), kind="content"),
    Rule("webhook_repo_sync", ("webhook",), kind="content"),
    Rule("cron_jobs_3x_daily", ("3x/day", "three times per day", "cron"), kind="content"),
    Rule("repo_health_monitoring", ("healthcheck", "health"), kind="content"),
    Rule("universal_llm_txt", ("LLM.txt", "llm.txt")),
    Rule("toolbox_skill_registry", ("toolbox", "skills"), kind="content"),
    Rule("context7_integration", ("context7", "docs freshness"), kind="content"),
    Rule("security_monitoring_self_hosted", ("self-host", "sentry", "otel", "monitoring"), kind="content"),
    Rule("logging_error_pipeline", ("logging", "error pipeline", "structlog"), kind="content"),
    Rule("repo_consolidation_detection", ("consolidation",), kind="content"),
    Rule("cross_repo_similarity_detection", ("similarity", "graphbrain"), kind="content"),
    Rule("agent_zero_reasoning_engine", ("agent zero",), kind="content"),
    Rule("remotion_integration", ("remotion",), kind="content"),
    Rule("storytoolkit_integration", ("storytoolkit",), kind="content"),
    Rule("blender_skill", ("blender",), kind="content"),
    Rule("dependency_scanner", ("osv", "dependabot", "dependency scan"), kind="content"),
    Rule("secrets_leak_scanner", ("gitleaks", "secret scan"), kind="content"),
    Rule("audit_logs", ("audit log",), kind="content"),
)


def discover_repos(base: Path) -> list[Path]:
    repos: list[Path] = []
    if (base / ".git").exists():
        repos.append(base)
    for child in base.iterdir():
        if child.is_dir() and (child / ".git").exists():
            repos.append(child)
    return sorted(set(repos))


def load_spec(path: Path) -> dict[str, list[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["domains"]


def iter_text_files(repo: Path) -> Iterable[Path]:
    for p in repo.rglob("*"):
        if not p.is_file():
            continue
        if any(part in {".git", "node_modules", ".venv", "dist", "build"} for part in p.parts):
            continue
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".lock"}:
            continue
        yield p


def evaluate_component(repo: Path, component: str) -> dict[str, object]:
    rules = [rule for rule in RULES if rule.component == component]
    if not rules:
        return {"status": "missing", "evidence": [], "notes": "No detection rule defined"}

    evidence: list[str] = []
    hit_count = 0
    for rule in rules:
        if rule.kind == "file":
            for pattern in rule.patterns:
                if list(repo.glob(f"**/{pattern}")):
                    hit_count += 1
                    evidence.append(f"file:{pattern}")
                    break
        else:
            regex = re.compile("|".join(re.escape(p) for p in rule.patterns), re.IGNORECASE)
            for file in iter_text_files(repo):
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                if regex.search(content):
                    rel = file.relative_to(repo)
                    hit_count += 1
                    evidence.append(f"content:{rel}")
                    break

    status = "implemented" if hit_count == len(rules) else "partial" if hit_count else "missing"
    return {"status": status, "evidence": sorted(set(evidence)), "notes": ""}


def remediation_for(component: str) -> dict[str, object]:
    base_folder = "archonx"
    return {
        "required_files": [f"{base_folder}/ARCHONX.json", f"{base_folder}/reporting.json", f"{base_folder}/toolbox.md"],
        "required_folder_structure": [f"{base_folder}/", f"{base_folder}/agent-lightning/", "ops/reports/"],
        "required_dependency_changes": ["Add runtime + scan dependencies needed by component"],
        "required_ci_cd_updates": ["Add lint/test/build/security scan workflows", "Add heartbeat schedule (3x/day)"],
        "required_environment_variable_changes": ["ARCHONX_CONTROL_PLANE_URL", "ARCHONX_SERVICE_TOKEN", "ARCHONX_ENV"],
    }


def build_report(spec: dict[str, list[str]], repos: list[Path]) -> dict[str, object]:
    components = sorted({c for values in spec.values() for c in values})
    repo_reports: dict[str, dict[str, dict[str, object]]] = {}

    for repo in repos:
        repo_reports[repo.name] = {}
        for component in components:
            repo_reports[repo.name][component] = evaluate_component(repo, component)

    aggregate: dict[str, dict[str, object]] = {}
    for component in components:
        statuses = [repo_reports[r.name][component]["status"] for r in repos]
        if statuses and all(s == "implemented" for s in statuses):
            overall = "implemented"
        elif any(s in {"implemented", "partial"} for s in statuses):
            overall = "partial"
        else:
            overall = "missing"

        aggregate[component] = {
            "intended": "required",
            "actual": overall,
            "status": "OK" if overall == "implemented" else "GAP",
            "required_fix": "None" if overall == "implemented" else remediation_for(component),
        }

    return {"timestamp": datetime.now(timezone.utc).isoformat(), "repos": [r.name for r in repos], "by_repo": repo_reports, "delta": aggregate}


def markdown_from_report(report: dict[str, object]) -> str:
    delta = report["delta"]
    sections = {
        "SECTION A: Fully implemented components": [k for k, v in delta.items() if v["actual"] == "implemented"],
        "SECTION B: Partially implemented components": [k for k, v in delta.items() if v["actual"] == "partial"],
        "SECTION C: Missing components": [k for k, v in delta.items() if v["actual"] == "missing"],
    }

    lines = [
        "# ArchonX Ecosystem Gap Audit",
        "",
        f"Generated: {report['timestamp']}",
        f"Repositories scanned: {', '.join(report['repos'])}",
        "",
        "## Delta Table",
        "",
        "| Component | Intended | Actual | Status | Required Fix |",
        "|---|---|---|---|---|",
    ]
    for component, item in delta.items():
        required_fix = "none" if item["required_fix"] == "None" else "see remediation bundle"
        lines.append(f"| {component} | {item['intended']} | {item['actual']} | {item['status']} | {required_fix} |")

    lines.append("")
    for heading, items in sections.items():
        lines.append(f"## {heading}")
        lines.append("")
        lines.extend([f"- {i}" for i in items] or ["- (none)"])
        lines.append("")

    lines.extend(
        [
            "## SECTION D: Misaligned implementations",
            "",
            "- Components with only keyword hits but no dedicated runtime wiring should be treated as misaligned.",
            "",
            "## SECTION E: Security gaps",
            "",
            "- Review all missing/partial security domain items and prioritize secrets scanning, audit logs, intrusion detection.",
            "",
            "## SECTION F: Agent architecture gaps",
            "",
            "- Review missing `subagent_agent_zero`, `subagent_devika`, and repo reporting loop gaps.",
            "",
            "## SECTION G: Media stack gaps",
            "",
            "- Review missing `media_video_suite` entries for Remotion/StoryToolkit/Music/Blender flow.",
            "",
            "## SECTION H: SSO and auth gaps",
            "",
            "- Review SSO domain for central login, short-lived token issuance, session management, RBAC readiness.",
            "",
            "## PRIORITY REMEDIATION ORDER (High → Medium → Low)",
            "",
            "1. High: security + SSO/auth missing components.",
            "2. Medium: repo initiation/heartbeat/policy sync and graph intelligence gaps.",
            "3. Low: media-suite enhancements and dashboard polish.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="ArchonX ecosystem gap audit tool")
    parser.add_argument("--workspace", type=Path, default=Path.cwd(), help="Workspace path with one or more git repos")
    parser.add_argument("--spec", type=Path, default=Path("docs/audit/required_architecture_spec.json"), help="Spec JSON file")
    parser.add_argument("--out-dir", type=Path, default=Path("ops/reports/gap-audit"), help="Output directory")
    args = parser.parse_args()

    repos = discover_repos(args.workspace)
    if not repos:
        raise SystemExit("No git repositories discovered in workspace")

    spec = load_spec(args.spec)
    report = build_report(spec, repos)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = args.out_dir / f"GAP_AUDIT_{stamp}.json"
    md_path = args.out_dir / f"GAP_AUDIT_{stamp}.md"

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path.write_text(markdown_from_report(report), encoding="utf-8")

    print(str(json_path))
    print(str(md_path))


if __name__ == "__main__":
    main()
