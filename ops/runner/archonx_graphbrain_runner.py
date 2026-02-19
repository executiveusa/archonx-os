#!/usr/bin/env python3
"""ArchonX GraphBrain runner.
Bead: bead.graphbrain.bootstrap.v1
Ralphy loop: PLAN->IMPLEMENT->TEST->EVALUATE->PATCH->REPEAT
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.graphbrain.audit import emit_audit_event
from core.graphbrain.evidence import write_evidence_pack
from core.graphbrain.indexer import GraphBrainIndexer
from core.graphbrain.recommend import GraphBrainPipeline
REPORT_DIR = ROOT / "ops" / "reports" / "graphbrain"
AUDIT_PATH = REPORT_DIR / f"AUDIT_{datetime.now(timezone.utc).strftime('%Y%m%d')}.jsonl"


def _ts_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run(mode: str = "incremental", dry_run: bool = False) -> dict:
    emit_audit_event(AUDIT_PATH, {"event_id": _ts_tag(), "action": "indexing_start", "mode": mode})
    indexer = GraphBrainIndexer(ROOT)
    corpus = indexer.build_corpus()

    pipeline = GraphBrainPipeline()
    result = pipeline.run(corpus)

    ts = _ts_tag()
    snapshot = {
        "report_id": "graphbrain.graph_snapshot.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repos_indexed": 1,
        "mode": mode,
        **result,
        "dry_run": dry_run,
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    graph_path = REPORT_DIR / f"GRAPH_SNAPSHOT_{ts}.json"
    sim_path = REPORT_DIR / f"REPO_SIMILARITY_{ts}.json"
    rec_path = REPORT_DIR / f"CONSOLIDATION_RECS_{ts}.json"

    graph_path.write_text(json.dumps(snapshot, indent=2) + "\n")
    sim_path.write_text(json.dumps({"generated_at": snapshot["generated_at"], "pairs": []}, indent=2) + "\n")
    rec_payload = {
        "generated_at": snapshot["generated_at"],
        "recommendations": [{
            "rec_id": "rec-001",
            "type": "keep_separate",
            "repos": ["executiveusa/archonx-os"],
            "confidence": snapshot["confidence_example"],
            "why": {"note": "Single-repo local execution baseline."},
        }],
    }
    rec_path.write_text(json.dumps(rec_payload, indent=2) + "\n")

    evidence = write_evidence_pack(REPORT_DIR / f"EVIDENCE_PACK_{ts}.json", {
        "files_indexed": len(indexer.discover_files()),
        "top_bridges": snapshot["graph"]["bridge_terms_top"][:5],
    })
    emit_audit_event(AUDIT_PATH, {"event_id": _ts_tag(), "action": "indexing_end", "result": "ok", "evidence": evidence})
    return {"graph": str(graph_path), "similarity": str(sim_path), "recommendations": str(rec_path), "evidence": evidence}


def main() -> None:
    parser = argparse.ArgumentParser(prog="archonx-ops graphbrain")
    parser.add_argument("--mode", choices=["incremental", "full", "weekly-deep"], default="incremental")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    out = run(mode=args.mode, dry_run=args.dry_run)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
