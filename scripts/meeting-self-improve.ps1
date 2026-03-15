param(
  [string]$ArchonxPath = 'C:\archonx-os-main',
  [string]$OpenClawPath = 'C:\Users\execu\clawdbot-Whatsapp-agent',
  [string]$ChannelDir = 'C:\archonx-os-main\data\meeting-link',
  [int]$StaleMinutes = 60,
  [switch]$ApplyQuickFixes
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Add-Recommendation([System.Collections.Generic.List[string]]$list, [string]$message) {
  if (-not $list.Contains($message)) { [void]$list.Add($message) }
}

$recommendations = New-Object 'System.Collections.Generic.List[string]'
$actionsTaken = New-Object 'System.Collections.Generic.List[string]'
$checks = @{}

$meetingFile = Join-Path $ChannelDir 'meeting.jsonl'

$checks.archonxScript = Test-Path (Join-Path $ArchonxPath 'scripts\repo_meeting_link.ps1')
$checks.openclawScript = Test-Path (Join-Path $OpenClawPath 'scripts\repo-meeting-link.mjs')
$checks.checkerScript = Test-Path (Join-Path $ArchonxPath 'scripts\check_meeting_completion.ps1')
$checks.node = [bool](Get-Command node -ErrorAction SilentlyContinue)
$checks.powershell = [bool](Get-Command powershell -ErrorAction SilentlyContinue)

if (!(Test-Path $ChannelDir)) {
  if ($ApplyQuickFixes) {
    New-Item -ItemType Directory -Path $ChannelDir -Force | Out-Null
    [void]$actionsTaken.Add("Created channel dir: $ChannelDir")
  } else {
    Add-Recommendation $recommendations "Create channel directory: $ChannelDir"
  }
}

$events = @()
if (Test-Path $meetingFile) {
  foreach ($line in Get-Content -Path $meetingFile -Encoding UTF8) {
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    try { $events += ($line | ConvertFrom-Json) } catch {}
  }
}

$repoCounts = @{}
$openJobs = New-Object 'System.Collections.Generic.HashSet[string]'
$lastTs = $null

foreach ($evt in $events) {
  $repo = [string]$evt.repo
  if (-not $repoCounts.ContainsKey($repo)) { $repoCounts[$repo] = 0 }
  $repoCounts[$repo] = [int]$repoCounts[$repo] + 1

  if ($evt.type -eq 'job_start' -and $evt.job) { [void]$openJobs.Add([string]$evt.job) }
  if ($evt.type -eq 'job_done' -and $evt.job) { [void]$openJobs.Remove([string]$evt.job) }

  if ($evt.ts) {
    try {
      $parsed = [DateTimeOffset]::Parse([string]$evt.ts)
      if ($null -eq $lastTs -or $parsed -gt $lastTs) { $lastTs = $parsed }
    } catch {}
  }
}

if (-not $repoCounts.ContainsKey('archonx-os')) {
  Add-Recommendation $recommendations 'No archonx-os events yet; run run-meeting-sync.ps1.'
}
if (-not $repoCounts.ContainsKey('openclaw')) {
  Add-Recommendation $recommendations 'No openclaw events yet; run run-meeting-sync.ps1.'
}

if ($openJobs.Count -gt 0) {
  if ($ApplyQuickFixes) {
    Set-Location $ArchonxPath
    foreach ($jobId in $openJobs) {
      powershell -ExecutionPolicy Bypass -File scripts/repo_meeting_link.ps1 job-done $jobId 'auto-closed by self-improve' -Status done -ChannelDir $ChannelDir | Out-Null
      [void]$actionsTaken.Add("Auto-closed open job: $jobId")
    }
    $openJobs.Clear()
  } else {
    Add-Recommendation $recommendations 'There are open jobs; close them with repo_meeting_link job-done.'
  }
}

if ($events.Count -gt 5000) {
  Add-Recommendation $recommendations 'Channel log is large; rotate meeting.jsonl to archive and keep tail.'
}

if ($lastTs) {
  $age = [DateTimeOffset]::UtcNow - $lastTs
  if ($age.TotalMinutes -gt $StaleMinutes) {
    Add-Recommendation $recommendations "Meeting channel is stale (${[math]::Round($age.TotalMinutes,1)} min). Run run-meeting-sync.ps1."
  }
} else {
  Add-Recommendation $recommendations 'No events found; initialize bridge with run-meeting-sync.ps1.'
}

$report = @{
  ok = ($recommendations.Count -eq 0)
  generatedAt = [DateTime]::UtcNow.ToString('o')
  channel = $meetingFile
  checks = $checks
  eventCount = $events.Count
  repoCounts = $repoCounts
  openJobs = @($openJobs | ForEach-Object { $_ } | Sort-Object)
  recommendations = @($recommendations)
  actionsTaken = @($actionsTaken)
}

$reportDir = Join-Path $ArchonxPath 'data\meeting-link'
New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
$reportPath = Join-Path $reportDir 'self-improve-report.json'
$report | ConvertTo-Json -Depth 10 | Set-Content -Path $reportPath -Encoding UTF8

$report | ConvertTo-Json -Depth 10
if (-not $report.ok -and -not $ApplyQuickFixes) { exit 1 }
exit 0
