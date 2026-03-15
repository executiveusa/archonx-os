# ARCHON-X ConX Layer — One-Command Machine Onboarding (Windows)
# Usage: iwr https://raw.githubusercontent.com/executiveusa/archonx-os/main/scripts/conx-onboard.ps1 | iex

Write-Host "🔌 ARCHON-X ConX Layer — Onboarding this machine..." -ForegroundColor Cyan

# Check if winget is available
try {
    winget --version | Out-Null
} catch {
    Write-Host "❌ Windows Package Manager (winget) not found. Please install it first." -ForegroundColor Red
    exit 1
}

# Install cloudflared
Write-Host "Installing cloudflared..." -ForegroundColor Yellow
winget install Cloudflare.cloudflared -e --silent

# Install Node.js if missing
if (-Not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Node.js..." -ForegroundColor Yellow
    winget install OpenJS.NodeJS.LTS -e --silent
}

# Check Python is available
if (-Not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python not found. Install Python 3.11+ first." -ForegroundColor Red
    exit 1
}

Write-Host "✓ Dependencies ready" -ForegroundColor Green

# Install archonx if needed
try {
    python -c "import archonx" 2>$null
} catch {
    Write-Host "Installing archonx-os..." -ForegroundColor Yellow
    pip install archonx-os
}

# Run onboarding wizard
Write-Host "Starting onboarding wizard..." -ForegroundColor Yellow
python -c "from archonx.conx.onboard import run_onboard; run_onboard()"

Write-Host "✅ Onboarding complete!" -ForegroundColor Green
