param(
  [string]$ArchonxPath = 'C:\archonx-os-main',
  [string]$OpenClawPath = 'C:\Users\execu\clawdbot-Whatsapp-agent',
  [string]$ChannelDir = 'C:\archonx-os-main\data\meeting-link',
  [string]$ArchonxAuthor = 'archonx-sync',
  [string]$OpenClawAuthor = 'openclaw-sync',
  [string]$ArchonxMessage = 'ArchonX sync online',
  [string]$OpenClawMessage = 'OpenClaw sync online',
  [string]$JobId = '',
  [switch]$SkipCompletionCheck
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($JobId)) {
  $JobId = "sync-$([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds())"
}

function Assert-Tool([string]$name) {
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
    throw "Required command not found: $name"
  }
}

function Collect-JobResult([System.Management.Automation.Job]$job, [string]$name) {
  $output = Receive-Job -Job $job -Keep
  $state = (Get-Job -Id $job.Id).State
  return @{
    name = $name
    state = $state
    output = $output
    ok = ($state -eq 'Completed')
  }
}

Assert-Tool 'powershell'
Assert-Tool 'node'

if (!(Test-Path (Join-Path $ArchonxPath 'scripts\repo_meeting_link.ps1'))) {
  throw 'Missing ArchonX meeting script'
}
if (!(Test-Path (Join-Path $OpenClawPath 'scripts\repo-meeting-link.mjs'))) {
  throw 'Missing OpenClaw meeting script'
}

$startA = Start-Job -Name 'start-archonx' -ScriptBlock {
  param($ArchonxPath, $ChannelDir, $ArchonxMessage, $ArchonxAuthor, $JobId)
  Set-Location $ArchonxPath
  powershell -ExecutionPolicy Bypass -File scripts/repo_meeting_link.ps1 send $ArchonxMessage -Author $ArchonxAuthor -ChannelDir $ChannelDir | Out-String
  if ($LASTEXITCODE -ne 0) { throw 'archonx send failed' }
  powershell -ExecutionPolicy Bypass -File scripts/repo_meeting_link.ps1 job-start $JobId 'parallel sync started' -ChannelDir $ChannelDir | Out-String
  if ($LASTEXITCODE -ne 0) { throw 'archonx job-start failed' }
} -ArgumentList $ArchonxPath, $ChannelDir, $ArchonxMessage, $ArchonxAuthor, $JobId

$startB = Start-Job -Name 'start-openclaw' -ScriptBlock {
  param($OpenClawPath, $OpenClawMessage, $OpenClawAuthor, $JobId)
  Set-Location $OpenClawPath
  node scripts/repo-meeting-link.mjs send $OpenClawMessage --author $OpenClawAuthor | Out-String
  if ($LASTEXITCODE -ne 0) { throw 'openclaw send failed' }
  node scripts/repo-meeting-link.mjs job-start $JobId --detail 'parallel sync started' | Out-String
  if ($LASTEXITCODE -ne 0) { throw 'openclaw job-start failed' }
} -ArgumentList $OpenClawPath, $OpenClawMessage, $OpenClawAuthor, $JobId

Wait-Job -Job $startA, $startB | Out-Null
$startPhase = @{
  phase = 'start'
  archonx = Collect-JobResult -job $startA -name 'archonx'
  openclaw = Collect-JobResult -job $startB -name 'openclaw'
}
$startPhase.ok = [bool]$startPhase.archonx.ok -and [bool]$startPhase.openclaw.ok
Remove-Job -Job $startA, $startB -Force

if (-not $startPhase.ok) {
  $startPhase | ConvertTo-Json -Depth 10
  throw 'Start phase failed'
}

$doneA = Start-Job -Name 'done-archonx' -ScriptBlock {
  param($ArchonxPath, $ChannelDir, $JobId)
  Set-Location $ArchonxPath
  powershell -ExecutionPolicy Bypass -File scripts/repo_meeting_link.ps1 job-done $JobId 'parallel sync complete' -Status done -ChannelDir $ChannelDir | Out-String
  if ($LASTEXITCODE -ne 0) { throw 'archonx job-done failed' }
} -ArgumentList $ArchonxPath, $ChannelDir, $JobId

$doneB = Start-Job -Name 'done-openclaw' -ScriptBlock {
  param($OpenClawPath, $JobId)
  Set-Location $OpenClawPath
  node scripts/repo-meeting-link.mjs job-done $JobId --status done --detail 'parallel sync complete' | Out-String
  if ($LASTEXITCODE -ne 0) { throw 'openclaw job-done failed' }
} -ArgumentList $OpenClawPath, $JobId

Wait-Job -Job $doneA, $doneB | Out-Null
$donePhase = @{
  phase = 'done'
  archonx = Collect-JobResult -job $doneA -name 'archonx'
  openclaw = Collect-JobResult -job $doneB -name 'openclaw'
}
$donePhase.ok = [bool]$donePhase.archonx.ok -and [bool]$donePhase.openclaw.ok
Remove-Job -Job $doneA, $doneB -Force

if (-not $donePhase.ok) {
  $donePhase | ConvertTo-Json -Depth 10
  throw 'Done phase failed'
}

Set-Location $ArchonxPath
$statusRaw = powershell -ExecutionPolicy Bypass -File scripts/repo_meeting_link.ps1 status -ChannelDir $ChannelDir

$checkerExit = $null
$checkerRaw = $null
if (-not $SkipCompletionCheck) {
  $checkerRaw = powershell -ExecutionPolicy Bypass -File scripts/check_meeting_completion.ps1 -Channel (Join-Path $ChannelDir 'meeting.jsonl')
  $checkerExit = $LASTEXITCODE
}

$summary = @{
  ok = ($SkipCompletionCheck -or $checkerExit -eq 0)
  jobId = $JobId
  startPhase = $startPhase
  donePhase = $donePhase
  status = $(try { $statusRaw | ConvertFrom-Json } catch { $statusRaw })
  completionCheck = @{
    skipped = [bool]$SkipCompletionCheck
    exitCode = $checkerExit
    output = $(if ($checkerRaw) { try { $checkerRaw | ConvertFrom-Json } catch { $checkerRaw } } else { $null })
  }
}

$summary | ConvertTo-Json -Depth 12
if (-not $summary.ok) { exit 1 }
exit 0
