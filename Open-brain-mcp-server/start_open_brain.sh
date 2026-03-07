#!/usr/bin/env bash
# Start Open Brain MCP Server
# Validates .env, runs schema check, then starts the server

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "================================"
echo "Open Brain MCP Server - Startup"
echo "================================"

# Check .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and fill in the required values."
    exit 1
fi

echo "✓ .env file found"

# Check Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    exit 1
fi

echo "✓ Python 3 available: $(python3 --version)"

# Install/upgrade dependencies if needed
echo ""
echo "Installing dependencies..."
python3 -m pip install -q -r requirements.txt || {
    echo "ERROR: Failed to install requirements"
    exit 1
}
echo "✓ Dependencies installed"

# Run schema check
echo ""
echo "Verifying database schema..."
python3 schema_check.py || {
    echo "ERROR: Schema check failed"
    exit 1
}
echo "✓ Schema check passed"

# Start the server
echo ""
echo "Starting Open Brain MCP Server..."
echo "Press Ctrl+C to stop"
python3 open_brain_mcp_server.py

exit 0
