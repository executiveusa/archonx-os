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
$reportDir = 'C:\Users\execu\archonx-os\ops\reports'
$timestamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$outFile = Join-Path $reportDir ("PAULIWHEEL_COMPLIANCE_MATRIX_{0}.json" -f $timestamp)

$rows = @()
foreach ($r in $repos) {
  $repoPath = Join-Path $root $r
  if (-not (Test-Path $repoPath)) {
    $rows += [ordered]@{
      repo = $r
      exists = $false
      reportback = $false
      toolbox = $false
      agents = $false
      smoke = $false
      preflight = $false
      compliant = $false
    }
    continue
  }

  $reportback = Test-Path (Join-Path $repoPath '.archonx\reportback.json')
  $toolbox = Test-Path (Join-Path $repoPath '.archonx\toolbox.json')
  $agents = Test-Path (Join-Path $repoPath 'AGENTS.md')
  $smoke = Test-Path (Join-Path $repoPath 'tests\agent_lightning_smoke.py')
  $preflight = Test-Path (Join-Path $repoPath 'scripts\pauliwheel_preflight.ps1')

  $rows += [ordered]@{
    repo = $r
    exists = $true
    reportback = $reportback
    toolbox = $toolbox
    agents = $agents
    smoke = $smoke
    preflight = $preflight
    compliant = ($reportback -and $toolbox -and $agents -and $smoke -and $preflight)
  }
}

$payload = [ordered]@{
  generatedAt = (Get-Date).ToUniversalTime().ToString('o')
  bead_id = 'BEAD-0006'
  source_of_truth = 'executiveusa/archonx-os'
  repos = $rows
}

New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$payload | ConvertTo-Json -Depth 6 | Set-Content -Path $outFile -Encoding UTF8
Write-Host $outFile
