#!/usr/bin/env python3
"""Checks cross-repo meeting channel completion state.

Fails with exit code 1 when required repos have no activity or open jobs remain.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_events(path: Path) -> list[dict]:
    if not path.exists():
        return []
    events: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate cross-repo meeting completion")
    parser.add_argument(
        "--channel",
        default=r"C:\archonx-os-main\data\meeting-link\meeting.jsonl",
        help="Path to meeting.jsonl",
    )
    parser.add_argument(
        "--required-repo",
        action="append",
        default=["archonx-os", "openclaw"],
        help="Repo names that must have at least one event",
    )
    args = parser.parse_args()

    channel = Path(args.channel)
    events = read_events(channel)

    repos_with_events = {str(evt.get("repo", "")) for evt in events}
    missing = [repo for repo in args.required_repo if repo not in repos_with_events]

    open_jobs: set[str] = set()
    for evt in events:
        etype = evt.get("type")
        job = str(evt.get("job", ""))
        if etype == "job_start" and job:
            open_jobs.add(job)
        if etype == "job_done" and job:
            open_jobs.discard(job)

    payload = {
        "ok": not missing and not open_jobs,
        "channel": str(channel),
        "eventCount": len(events),
        "missingRepos": missing,
        "openJobs": sorted(open_jobs),
    }
    print(json.dumps(payload, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
