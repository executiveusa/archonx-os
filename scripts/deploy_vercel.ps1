# deploy_vercel.ps1 — Phase 3B: Secure Vercel deployment
# Reads VERCEL_TOKEN from master.env without logging it.
# Usage: .\scripts\deploy_vercel.ps1

param(
    [string]$EnvFile = "$PSScriptRoot\..\master.env",
    [string]$ProjectId = "prj_T19WSaUiqLmrAewXECfctQyw4jKe"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── Load env vars from file ──────────────────────────────────────────────────
if (-not (Test-Path $EnvFile)) {
    Write-Error "master.env not found at: $EnvFile"
    exit 1
}

$envVars = @{}
Get-Content $EnvFile | Where-Object { $_ -match "^[A-Z_]+=.+" } | ForEach-Object {
    $parts = $_ -split "=", 2
    $envVars[$parts[0].Trim()] = $parts[1].Trim()
}

$token = $envVars["VERCEL_TOKEN"]
if (-not $token) {
    Write-Error "VERCEL_TOKEN not found in master.env"
    exit 1
}
Write-Host "[deploy] VERCEL_TOKEN loaded (${token.Length} chars)" -ForegroundColor Cyan

# ── Collect env vars to push to Vercel ──────────────────────────────────────
$relevantKeys = @(
    "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
    "NEXT_PUBLIC_SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "STRIPE_SECRET_KEY", "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY",
    "INFISICAL_SECRET_KEY",
    "CHESS_SERVER_WS_URL"
)

# ── Deploy chess-theater ──────────────────────────────────────────────────────
Write-Host "`n[deploy] Deploying chess-theater to Vercel..." -ForegroundColor Yellow
$env:VERCEL_TOKEN = $token
Push-Location "$PSScriptRoot\..\chess-theater"
try {
    # Pull existing project config if available, else link to project ID
    vercel pull --yes --environment=production --token=$token 2>&1 | Out-Null
    
    $result = vercel deploy --prod --token=$token --yes 2>&1
    $chessUrl = ($result | Where-Object { $_ -match "https://" } | Select-Object -Last 1).Trim()
    Write-Host "[deploy] chess-theater: $chessUrl" -ForegroundColor Green
} catch {
    Write-Warning "[deploy] chess-theater deploy error: $_"
    $chessUrl = "FAILED"
} finally {
    Pop-Location
}

# ── Deploy synthia-3-0 ────────────────────────────────────────────────────────
Write-Host "`n[deploy] Deploying synthia-3-0 to Vercel..." -ForegroundColor Yellow
Push-Location "$PSScriptRoot\..\synthia-3-0"
try {
    vercel pull --yes --environment=production --token=$token 2>&1 | Out-Null
    
    $result = vercel deploy --prod --token=$token --yes 2>&1
    $synthiaUrl = ($result | Where-Object { $_ -match "https://" } | Select-Object -Last 1).Trim()
    Write-Host "[deploy] synthia-3-0: $synthiaUrl" -ForegroundColor Green
} catch {
    Write-Warning "[deploy] synthia-3-0 deploy error: $_"
    $synthiaUrl = "FAILED"
} finally {
    Pop-Location
}

# ── Push env vars to project ──────────────────────────────────────────────────
Write-Host "`n[deploy] Setting env vars on Vercel project $ProjectId..." -ForegroundColor Yellow
foreach ($key in $relevantKeys) {
    if ($envVars.ContainsKey($key)) {
        echo $envVars[$key] | vercel env add $key production --token=$token --yes 2>&1 | Out-Null
        Write-Host "  + $key" -ForegroundColor DarkGray
    }
}

# ── Summary ───────────────────────────────────────────────────────────────────
Write-Host "`n╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  PHASE 3B DEPLOYMENT COMPLETE                       ║" -ForegroundColor Cyan
Write-Host "╠══════════════════════════════════════════════════════╣" -ForegroundColor Cyan
Write-Host "║  Chess Theater   : $chessUrl" -ForegroundColor White
Write-Host "║  Synthia 3.0     : $synthiaUrl" -ForegroundColor White
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Remove-Variable token
$env:VERCEL_TOKEN = $null
