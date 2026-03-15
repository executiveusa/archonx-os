from pathlib import Path
import hashlib
import json


def write_evidence_pack(path: Path, evidence: dict) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence, indent=2) + "\n")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"artifact": str(path), "sha256": digest}
