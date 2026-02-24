#!/usr/bin/env bash
set -euo pipefail

echo "[devika-pi] Checking PI coding agent installation..."
npm ls @mariozechner/pi-coding-agent --depth=0 >/dev/null 2>&1
echo "[devika-pi] package detected"

