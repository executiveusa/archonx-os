#!/usr/bin/env python3
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ECO_DIR = ROOT / "security" / "codex" / "eco-prompts"
REGISTRY = ROOT / "security" / "registry" / "agents.json"
TOOLBOX = ROOT / "toolbox" / "toolbox.json"
REPORTS = ROOT / "ops" / "reports"
SCHEDULER = ROOT / "ops" / "scheduler"


def ts_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path):
    with path.open() as f:
        return json.load(f)


def dump_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_doctor():
    checks = {
        "runner_exists": Path(__file__).exists(),
        "eco_prompt_dir_exists": ECO_DIR.exists(),
        "registry_exists": REGISTRY.exists(),
        "toolbox_exists": TOOLBOX.exists(),
        "cron_exists": (SCHEDULER / "pauliwheel_sync.crontab").exists(),
    }
    status = "ok" if all(checks.values()) else "partial"
    return {"timestamp": ts_now(), "status": status, "checks": checks}


def meeting():
    registry = load_json(REGISTRY)
    agents = registry.get("agents", [])
    toolbox_hash = sha(TOOLBOX)
    contract_hash = sha(ROOT / "ecosystem" / "manifest.json")
    eco_files = sorted(ECO_DIR.glob("*.json"))
    eco_hash = sha(eco_files[0]) if eco_files else "missing"
    ack_bundle = hashlib.sha256(f"{toolbox_hash}:{contract_hash}:{eco_hash}".encode()).hexdigest()

    updated = []
    for agent in agents:
        if agent.get("required_skills_attached"):
            agent["last_ack_at"] = ts_now()
            agent["ack_hash"] = ack_bundle
            agent["compliance_state"] = "compliant"
        else:
            agent["compliance_state"] = "restricted"
        updated.append(agent)

    registry["agents"] = updated
    dump_json(REGISTRY, registry)

    report = {
        "timestamp": ts_now(),
        "contract_hash": contract_hash,
        "eco_prompt_hash": eco_hash,
        "toolbox_version": load_json(TOOLBOX).get("version"),
        "agents": updated,
    }
    out = REPORTS / f"pauliwheel_meeting_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    dump_json(out, report)
    return out


def compliance_matrix(repos):
    rows = []
    for repo in repos:
        slug = repo["slug"]
        rows.append({
            "repo": slug,
            "status": "partial",
            "required_files_present": slug.endswith("archonx-os"),
            "agent_lightning": "stub",
            "tests": "not_found",
            "notes": ["External repo scan requires checkout in this environment."]
        })
    return rows


def run_prompt(name: str, dry_run=False, report_only=False):
    eco_path = ECO_DIR / f"{name}.json"
    eco = load_json(eco_path)
    manifest = load_json(ROOT / "ecosystem" / "manifest.json")
    doctor = run_doctor()
    meeting_path = None if report_only else str(meeting())

    sync_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    sync_report = {
        "eco_prompt": eco["eco_prompt_name"],
        "timestamp": ts_now(),
        "dry_run": dry_run,
        "report_only": report_only,
        "doctor": doctor,
        "meeting_report": meeting_path,
        "repos_scanned": compliance_matrix(manifest.get("repos", [])),
        "blocking_issues": [
            "Ecosystem repositories are declared but not locally checked out; emitted partial compliance."
        ],
        "next_steps": [
            "Mount or clone ecosystem repos and rerun archonx-ops sync --all.",
            "Implement repo-specific test commands in ops runner config."
        ]
    }
    compliance = {
        "eco_prompt": eco["eco_prompt_name"],
        "timestamp": ts_now(),
        "repos": sync_report["repos_scanned"],
    }
    final_report = {
        "eco_prompt": eco["eco_prompt_name"],
        "timestamp": ts_now(),
        "repos_scanned": sync_report["repos_scanned"],
        "agents_scanned": load_json(REGISTRY).get("agents", []),
        "scheduler": {
            "installed": (SCHEDULER / "pauliwheel_sync.crontab").exists(),
            "mode": "cron",
            "schedules": ["0 9 * * *", "0 15 * * *", "0 21 * * *"],
            "last_run": ts_now()
        },
        "blocking_issues": sync_report["blocking_issues"],
        "next_steps": sync_report["next_steps"]
    }

    dump_json(REPORTS / f"PAULIWHEEL_SYNC_REPORT_{sync_ts}.json", sync_report)
    dump_json(REPORTS / f"PAULIWHEEL_COMPLIANCE_MATRIX_{sync_ts}.json", compliance)
    dump_json(REPORTS / "FINAL_ECO_PROMPT_REPORT.json", final_report)


def main():
    parser = argparse.ArgumentParser(prog="archonx-ops")
    sub = parser.add_subparsers(dest="command", required=True)

    run_cmd = sub.add_parser("run")
    run_cmd.add_argument("--eco-prompt", required=True)
    run_cmd.add_argument("--dry-run", action="store_true")
    run_cmd.add_argument("--report-only", action="store_true")

    sync_cmd = sub.add_parser("sync")
    sync_cmd.add_argument("--all", action="store_true")

    enroll_cmd = sub.add_parser("enroll")
    enroll_cmd.add_argument("--agent-id", required=True)

    sub.add_parser("meeting")
    sub.add_parser("doctor")

    gb_cmd = sub.add_parser("graphbrain")
    gb_cmd.add_argument("--mode", choices=["incremental", "full", "weekly-deep"], default="incremental")
    gb_cmd.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if args.command == "run":
        run_prompt(args.eco_prompt, dry_run=args.dry_run, report_only=args.report_only)
    elif args.command == "sync":
        files = sorted(ECO_DIR.glob("*.json"))
        if not files:
            raise SystemExit("No eco-prompts found")
        for f in files:
            run_prompt(f.stem)
    elif args.command == "enroll":
        import subprocess
        subprocess.check_call([str(ROOT / "ops" / "scripts" / "archonx_enroll_agent.sh"), args.agent_id])
    elif args.command == "meeting":
        print(meeting())
    elif args.command == "doctor":
        print(json.dumps(run_doctor(), indent=2))
    elif args.command == "graphbrain":
        import subprocess
        cmd = ["python", str(ROOT / "ops" / "runner" / "archonx_graphbrain_runner.py"), "--mode", args.mode]
        if args.dry_run:
            cmd.append("--dry-run")
        subprocess.check_call(cmd)


if __name__ == "__main__":
    main()
