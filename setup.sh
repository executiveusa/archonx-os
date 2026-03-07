#!/bin/bash
# ArchonX Vault Agent Setup for Linux
# Sets up vault agent, installs dependencies, configures cron job

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "[*] ArchonX Setup Starting (Linux)"
echo "[*] Repo Root: $REPO_ROOT"

# Step 1: Check Python
echo "[*] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found. Install with: sudo apt install python3 python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "[+] Python version: $PYTHON_VERSION"

# Step 2: Install dependencies
echo "[*] Installing Python dependencies..."
cd "$REPO_ROOT"

DEPS=(
    "requests"
    "python-dotenv"
    "cryptography"
)

for dep in "${DEPS[@]}"; do
    echo "  Installing $dep..."
    python3 -m pip install --quiet "$dep" 2>/dev/null || {
        echo "  WARNING: Failed to install $dep (may already be installed)"
    }
done

echo "[+] Dependencies installed"

# Step 3: Create ops/reports directory
echo "[*] Setting up ops/reports directory..."
mkdir -p "$REPO_ROOT/ops/reports"
chmod 755 "$REPO_ROOT/ops/reports"
echo "[+] Created: $REPO_ROOT/ops/reports"

# Step 4: Make scripts executable
echo "[*] Setting executable permissions..."
chmod +x "$REPO_ROOT/vault_agent.py"
chmod +x "$REPO_ROOT/ai_advisor.py"
chmod +x "$REPO_ROOT/run_full.py"
echo "[+] Scripts are executable"

# Step 5: Test vault agent
echo "[*] Testing vault_agent.py..."
if python3 "$REPO_ROOT/vault_agent.py" --help > /dev/null 2>&1; then
    echo "[+] vault_agent.py is importable and working"
else
    echo "ERROR: vault_agent.py test failed"
    exit 1
fi

# Step 6: Test ai_advisor
echo "[*] Testing ai_advisor.py..."
if python3 -c "import sys; sys.path.insert(0, '$REPO_ROOT'); from ai_advisor import AIAdvisor; print('OK')" > /dev/null 2>&1; then
    echo "[+] ai_advisor.py is importable"
else
    echo "WARNING: ai_advisor.py import failed (may need requests)"
fi

# Step 7: Configure cron job
echo "[*] Configuring cron job..."

CRON_CMD="cd $REPO_ROOT && /usr/bin/python3 run_full.py >> $REPO_ROOT/ops/reports/cron.log 2>&1"
CRON_SCHEDULE="0 3 * * * $CRON_CMD"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "run_full.py"; then
    echo "[*] Cron job already installed"
else
    # Add cron job (runs daily at 3AM)
    (crontab -l 2>/dev/null; echo "$CRON_SCHEDULE") | crontab - 2>/dev/null || {
        echo "WARNING: Could not install cron job (may require sudo or cron service running)"
    }
    echo "[+] Added cron job: Daily at 3AM"
fi

echo ""
echo "========================================"
echo "ArchonX Setup Complete!"
echo "========================================"
echo ""
echo "Files created:"
echo "  - $REPO_ROOT/vault_agent.py"
echo "  - $REPO_ROOT/ai_advisor.py"
echo "  - $REPO_ROOT/run_full.py"
echo ""
echo "Next steps:"
echo "1. Run first audit: python3 $REPO_ROOT/vault_agent.py"
echo "2. Set environment variables if using AI backends:"
echo "   export HF_API_KEY=your_huggingface_token"
echo "   export GROQ_API_KEY=your_groq_token"
echo "   export GOOGLE_API_KEY=your_gemini_token"
echo "3. View reports: ls $REPO_ROOT/ops/reports/"
echo ""
echo "Scheduled tasks:"
echo "  - Daily audit at 3:00 AM via cron"
echo "  - View logs: tail $REPO_ROOT/ops/reports/cron.log"
echo ""
