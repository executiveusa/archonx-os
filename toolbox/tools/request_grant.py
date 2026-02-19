#!/usr/bin/env python3
"""Minimal toolbox wrapper for grant requests."""

import json
import os
import sys


def main() -> int:
    work_item_id = os.getenv("ARCHONX_WORK_ITEM_ID", "")
    if not work_item_id:
        print(json.dumps({"error": "missing_work_item_id"}))
        return 1

    payload = {
        "kernel_url": os.getenv("ARCHONX_KERNEL_URL", "http://localhost:7447"),
        "work_item_id": work_item_id,
        "action": sys.argv[1] if len(sys.argv) > 1 else "unknown",
        "resource": sys.argv[2] if len(sys.argv) > 2 else "unknown",
    }
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
