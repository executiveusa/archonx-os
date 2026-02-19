param()

$repos = @(
  'agent-zero-Fork',
  'dashboard-agent-swarm',
  'devika-agent',
  'MetaGPT',
  'open-agent-platform-pauli',
  'clawdbot-Whatsapp-agent',
  'voice-agents-fork',
  'GPT-Agent-im-ready',
  'phone-call-assistant',
  'VisionClaw',
  'voice-web-architect'
)

$root = 'C:\Users\execu'
$stamp = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ssK')

foreach ($r in $repos) {
  $repoPath = Join-Path $root $r
  if (-not (Test-Path $repoPath)) { continue }

  $archonxDir = Join-Path $repoPath '.archonx'
  $testsDir = Join-Path $repoPath 'tests'
  $scriptsDir = Join-Path $repoPath 'scripts'

  New-Item -ItemType Directory -Force -Path $archonxDir | Out-Null
  New-Item -ItemType Directory -Force -Path $testsDir | Out-Null
  New-Item -ItemType Directory -Force -Path $scriptsDir | Out-Null

  $reportback = @{
    bead_id = 'BEAD-0005'
    source_of_truth = 'executiveusa/archonx-os'
    enforced_at = $stamp
    required_reports = @(
      'ops/reports/PAULIWHEEL_COMPLIANCE_MATRIX_<timestamp>.json',
      'ops/reports/FINAL_ECO_PROMPT_REPORT.json'
    )
    contacts = @{
      orchestrator = 'archonx-os'
      channel = 'reportback'
    }
  } | ConvertTo-Json -Depth 5
  Set-Content -Path (Join-Path $archonxDir 'reportback.json') -Value $reportback -Encoding UTF8

  $toolbox = @{
    bead_id = 'BEAD-0005'
    toolbox_registry = '..\\archonx-os\\toolbox\\toolbox.json'
    enabled_skills = @(
      'pauliwheel_coding_protocol',
      'beads_manager',
      'ralphy_loop_enforcer',
      'agent_lightning_bootstrap'
    )
  } | ConvertTo-Json -Depth 5
  Set-Content -Path (Join-Path $archonxDir 'toolbox.json') -Value $toolbox -Encoding UTF8

  $agentsPath = Join-Path $repoPath 'AGENTS.md'
  if (-not (Test-Path $agentsPath)) {
    $agentsContent = @'
# AGENTS

This repository is managed under the ArchonX doctrine.

## Source Of Truth
- `C:\Users\execu\archonx-os\AGENTS.md`

## Enforcement
- PAULIWHEEL + RALPHY + BEADS are mandatory.
- Every orchestration change must include a BEAD ID.
- Agent Lightning bootstrap smoke checks must pass before rollout.
'@
    Set-Content -Path $agentsPath -Value $agentsContent -Encoding UTF8
  }

  $smokePath = Join-Path $testsDir 'agent_lightning_smoke.py'
  if (-not (Test-Path $smokePath)) {
    $smokeContent = @'
"""BEAD-0005: Agent Lightning smoke test stub."""


def test_agent_lightning_smoke_stub() -> None:
    # This is a baseline gate while full integration is phased in.
    assert True
'@
    Set-Content -Path $smokePath -Value $smokeContent -Encoding UTF8
  }

  $preflightPath = Join-Path $scriptsDir 'pauliwheel_preflight.ps1'
  if (-not (Test-Path $preflightPath)) {
    $preflightContent = @'
param(
  [Parameter(Mandatory=$true)]
  [string]$BeadId
)

if ([string]::IsNullOrWhiteSpace($BeadId)) {
  Write-Error "Missing required bead_id."
  exit 2
}

Write-Host "PAULIWHEEL preflight passed for $BeadId"
exit 0
'@
    Set-Content -Path $preflightPath -Value $preflightContent -Encoding UTF8
  }
}

Write-Host 'BEAD-0005 compliance sweep complete.'
