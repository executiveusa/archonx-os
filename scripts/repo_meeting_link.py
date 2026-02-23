#!/usr/bin/env python3
"""Cross-repo meeting link for ArchonX <-> OpenClaw.

Writes and reads JSONL events in a shared channel directory so both repos can
chat and track job completion without extra infrastructure.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

DEFAULT_CHANNEL_DIR = Path(os.getenv("ARCHONX_MEETING_DIR", r"C:\archonx-os-main\data\meeting-link"))
DEFAULT_REPO = "archonx-os"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _channel_path(channel_dir: Path) -> Path:
    channel_dir.mkdir(parents=True, exist_ok=True)
    return channel_dir / "meeting.jsonl"


def _append_event(channel_dir: Path, event: dict) -> None:
    path = _channel_path(channel_dir)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=True) + "\n")


def _read_events(channel_dir: Path) -> list[dict]:
    path = _channel_path(channel_dir)
    if not path.exists():
        return []
    events: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def cmd_send(args: argparse.Namespace) -> int:
    event = {
        "id": f"evt_{uuid4().hex[:10]}",
        "ts": _utc_now(),
        "type": "chat",
        "repo": args.repo,
        "author": args.author,
        "text": args.text,
    }
    _append_event(args.channel_dir, event)
    print(json.dumps({"ok": True, "event": event}, indent=2))
    return 0


def cmd_job_start(args: argparse.Namespace) -> int:
    event = {
        "id": f"job_{uuid4().hex[:10]}",
        "ts": _utc_now(),
        "type": "job_start",
        "repo": args.repo,
        "job": args.job,
        "detail": args.detail,
    }
    _append_event(args.channel_dir, event)
    print(json.dumps({"ok": True, "event": event}, indent=2))
    return 0


def cmd_job_done(args: argparse.Namespace) -> int:
    event = {
        "id": f"job_{uuid4().hex[:10]}",
        "ts": _utc_now(),
        "type": "job_done",
        "repo": args.repo,
        "job": args.job,
        "detail": args.detail,
        "status": args.status,
    }
    _append_event(args.channel_dir, event)
    print(json.dumps({"ok": True, "event": event}, indent=2))
    return 0


def cmd_tail(args: argparse.Namespace) -> int:
    events = _read_events(args.channel_dir)
    for event in events[-args.limit :]:
        print(json.dumps(event, ensure_ascii=True))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    events = _read_events(args.channel_dir)
    by_repo: dict[str, int] = defaultdict(int)
    open_jobs: set[str] = set()
    last_chat: dict[str, str] = {}

    for event in events:
        repo = str(event.get("repo", "unknown"))
        by_repo[repo] += 1
        etype = event.get("type")
        job = str(event.get("job", ""))
        if etype == "job_start" and job:
            open_jobs.add(job)
        if etype == "job_done" and job:
            open_jobs.discard(job)
        if etype == "chat":
            last_chat[repo] = str(event.get("text", ""))

    payload = {
        "ok": True,
        "events": len(events),
        "repos": dict(by_repo),
        "openJobs": sorted(open_jobs),
        "lastChat": last_chat,
        "channel": str(_channel_path(args.channel_dir)),
    }
    print(json.dumps(payload, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ArchonX/OpenClaw meeting link")
    parser.add_argument("--channel-dir", type=Path, default=DEFAULT_CHANNEL_DIR)
    parser.add_argument("--repo", default=DEFAULT_REPO)

    sub = parser.add_subparsers(dest="command", required=True)

    send = sub.add_parser("send", help="send a chat event")
    send.add_argument("text")
    send.add_argument("--author", default="system")
    send.set_defaults(func=cmd_send)

    start = sub.add_parser("job-start", help="mark job started")
    start.add_argument("job")
    start.add_argument("--detail", default="")
    start.set_defaults(func=cmd_job_start)

    done = sub.add_parser("job-done", help="mark job completed")
    done.add_argument("job")
    done.add_argument("--status", default="done")
    done.add_argument("--detail", default="")
    done.set_defaults(func=cmd_job_done)

    tail = sub.add_parser("tail", help="show recent events")
    tail.add_argument("--limit", type=int, default=20)
    tail.set_defaults(func=cmd_tail)

    status = sub.add_parser("status", help="show meeting/job status")
    status.set_defaults(func=cmd_status)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
