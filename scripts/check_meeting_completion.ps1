param(
  [string]$Channel = 'C:\archonx-os-main\data\meeting-link\meeting.jsonl',
  [string[]]$RequiredRepos = @('archonx-os','openclaw')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$events = @()
if (Test-Path $Channel) {
  foreach ($line in Get-Content -Path $Channel -Encoding UTF8) {
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    try { $events += ($line | ConvertFrom-Json) } catch {}
  }
}

$reposWithEvents = New-Object 'System.Collections.Generic.HashSet[string]'
$openJobs = New-Object 'System.Collections.Generic.HashSet[string]'

foreach ($evt in $events) {
  if ($evt.repo) { [void]$reposWithEvents.Add([string]$evt.repo) }
  if ($evt.type -eq 'job_start' -and $evt.job) { [void]$openJobs.Add([string]$evt.job) }
  if ($evt.type -eq 'job_done' -and $evt.job) { [void]$openJobs.Remove([string]$evt.job) }
}

$missing = @()
foreach ($repo in $RequiredRepos) {
  if (-not $reposWithEvents.Contains($repo)) { $missing += $repo }
}

$payload = @{
  ok = ($missing.Count -eq 0 -and $openJobs.Count -eq 0)
  channel = $Channel
  eventCount = $events.Count
  missingRepos = $missing
  openJobs = @($openJobs | ForEach-Object { $_ } | Sort-Object)
}

$payload | ConvertTo-Json -Depth 8
if (-not $payload.ok) { exit 1 }
exit 0
