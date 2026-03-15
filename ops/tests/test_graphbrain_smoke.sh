#!/usr/bin/env bash
set -euo pipefail
python ops/runner/archonx_graphbrain_runner.py --mode incremental --dry-run >/tmp/graphbrain_smoke.out
ls ops/reports/graphbrain/GRAPH_SNAPSHOT_*.json >/dev/null
