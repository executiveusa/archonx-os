#!/bin/bash
# ARCHON-X ConX Layer — One-Command Machine Onboarding
# Usage: curl -fsSL https://raw.githubusercontent.com/executiveusa/archonx-os/main/scripts/conx-onboard.sh | bash

set -e

echo "🔌 ARCHON-X ConX Layer — Onboarding this machine..."

# Check Python 3.11+
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install Python 3.11+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Found Python $PYTHON_VERSION"

# Install archonx if not present
if ! python3 -c "import archonx" 2>/dev/null; then
    echo "Installing archonx-os..."
    pip3 install archonx-os 2>/dev/null || pip3 install -e . --break-system-packages
fi

# Run onboarding wizard
echo "Starting onboarding wizard..."
python3 -c "from archonx.conx.onboard import run_onboard; run_onboard()"

echo "✅ Onboarding complete!"
