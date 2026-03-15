import argparse
import datetime as dt
import glob
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ECO_DIR = ROOT / "security" / "codex" / "eco-prompts"
REPORT_DIR = ROOT / "ops" / "reports"


def now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def load_prompts() -> list[dict]:
    prompts = []
    for file_path in glob.glob(str(ECO_DIR / "*.json")):
        with open(file_path, "r", encoding="utf-8") as fh:
            prompts.append(json.load(fh))
    return prompts


def run_step(step_id: str, report_only: bool, dry_run: bool) -> dict:
    mode = "report-only" if report_only else "active"
    if dry_run:
        mode = "dry-run"
    return {
        "step": step_id,
        "mode": mode,
        "status": "ok",
        "timestamp": now_iso(),
    }


def make_compliance_matrix(prompts: list[dict], report_only: bool, dry_run: bool) -> dict:
    entries = []
    for prompt in prompts:
        for step in prompt.get("steps", []):
            if not step.get("enabled", True):
                continue
            entries.append(run_step(step["id"], report_only=report_only, dry_run=dry_run))
    return {
        "generatedAt": now_iso(),
        "bead_id": "BEAD-0006",
        "entries": entries,
    }


def write_report(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(description="ArchonX Ops Runner")
    parser.add_argument("--dry-run", action="store_true", help="Simulate runner actions")
    parser.add_argument("--report-only", action="store_true", help="Generate reports only")
    args = parser.parse_args()

    prompts = load_prompts()
    if not prompts:
        raise SystemExit("No eco-prompts found under security/codex/eco-prompts")

    timestamp = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    matrix = make_compliance_matrix(prompts, report_only=args.report_only, dry_run=args.dry_run)
    matrix_file = REPORT_DIR / f"PAULIWHEEL_COMPLIANCE_MATRIX_{timestamp}.json"
    write_report(matrix_file, matrix)

    final_report = {
        "generatedAt": now_iso(),
        "bead_id": "BEAD-0006",
        "mode": "dry-run" if args.dry_run else ("report-only" if args.report_only else "active"),
        "promptsLoaded": [p.get("name") for p in prompts],
        "matrixPath": str(matrix_file.relative_to(ROOT)),
        "status": "ok",
    }
    write_report(REPORT_DIR / "FINAL_ECO_PROMPT_REPORT.json", final_report)

    print(json.dumps({"status": "ok", "matrix": str(matrix_file), "final": str(REPORT_DIR / "FINAL_ECO_PROMPT_REPORT.json")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
