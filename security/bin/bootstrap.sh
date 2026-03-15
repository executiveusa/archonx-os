#!/usr/bin/env bash
set -euo pipefail

archonxctl init --non-interactive
archonxctl install --non-interactive
archonxctl doctor
