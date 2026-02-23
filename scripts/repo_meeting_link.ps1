param(
  [Parameter(Position=0, Mandatory=$true)] [ValidateSet('send','job-start','job-done','tail','status')] [string]$Command,
  [Parameter(Position=1)] [string]$Arg1,
  [Parameter(Position=2)] [string]$Arg2,
  [string]$Author = 'system',
  [string]$Status = 'done',
  [string]$Detail = '',
  [string]$Repo = 'archonx-os',
  [string]$ChannelDir = 'C:\archonx-os-main\data\meeting-link',
  [int]$Limit = 20
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function New-Id([string]$prefix) {
  $rand = -join ((48..57 + 97..122) | Get-Random -Count 8 | ForEach-Object {[char]$_})
  return "${prefix}_$([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds().ToString('x'))_$rand"
}

function Write-Event([hashtable]$evt, [string]$dir) {
  New-Item -ItemType Directory -Path $dir -Force | Out-Null
  $path = Join-Path $dir 'meeting.jsonl'
  $line = ($evt | ConvertTo-Json -Compress)
  Add-Content -Path $path -Value $line -Encoding UTF8
  return $path
}

function Read-Events([string]$dir) {
  $path = Join-Path $dir 'meeting.jsonl'
  if (!(Test-Path $path)) { return @() }
  $rows = @()
  foreach ($line in Get-Content -Path $path -Encoding UTF8) {
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    try { $rows += ($line | ConvertFrom-Json) } catch {}
  }
  return $rows
}

switch ($Command) {
  'send' {
    if ([string]::IsNullOrWhiteSpace($Arg1)) { throw 'send requires message text as Arg1' }
    $evt = @{
      id = (New-Id 'evt')
      ts = [DateTime]::UtcNow.ToString('o')
      type = 'chat'
      repo = $Repo
      author = $Author
      text = $Arg1
    }
    $channel = Write-Event -evt $evt -dir $ChannelDir
    @{ ok = $true; channel = $channel; event = $evt } | ConvertTo-Json -Depth 8
  }
  'job-start' {
    if ([string]::IsNullOrWhiteSpace($Arg1)) { throw 'job-start requires job id as Arg1' }
    $evt = @{
      id = (New-Id 'job')
      ts = [DateTime]::UtcNow.ToString('o')
      type = 'job_start'
      repo = $Repo
      job = $Arg1
      detail = $(if ($Arg2) { $Arg2 } else { $Detail })
    }
    $channel = Write-Event -evt $evt -dir $ChannelDir
    @{ ok = $true; channel = $channel; event = $evt } | ConvertTo-Json -Depth 8
  }
  'job-done' {
    if ([string]::IsNullOrWhiteSpace($Arg1)) { throw 'job-done requires job id as Arg1' }
    $evt = @{
      id = (New-Id 'job')
      ts = [DateTime]::UtcNow.ToString('o')
      type = 'job_done'
      repo = $Repo
      job = $Arg1
      status = $Status
      detail = $(if ($Arg2) { $Arg2 } else { $Detail })
    }
    $channel = Write-Event -evt $evt -dir $ChannelDir
    @{ ok = $true; channel = $channel; event = $evt } | ConvertTo-Json -Depth 8
  }
  'tail' {
    $events = Read-Events -dir $ChannelDir
    $slice = $events | Select-Object -Last $Limit
    foreach ($e in $slice) { $e | ConvertTo-Json -Compress }
  }
  'status' {
    $events = Read-Events -dir $ChannelDir
    $repos = @{}
    $open = New-Object 'System.Collections.Generic.HashSet[string]'
    $lastChat = @{}
    foreach ($e in $events) {
      $repoName = [string]$e.repo
      if (-not $repos.ContainsKey($repoName)) { $repos[$repoName] = 0 }
      $repos[$repoName] = [int]$repos[$repoName] + 1

      if ($e.type -eq 'job_start' -and $e.job) { [void]$open.Add([string]$e.job) }
      if ($e.type -eq 'job_done' -and $e.job) { [void]$open.Remove([string]$e.job) }
      if ($e.type -eq 'chat') { $lastChat[$repoName] = [string]$e.text }
    }

    @{
      ok = $true
      events = $events.Count
      repos = $repos
      openJobs = @($open | ForEach-Object { $_ } | Sort-Object)
      lastChat = $lastChat
      channel = (Join-Path $ChannelDir 'meeting.jsonl')
    } | ConvertTo-Json -Depth 8
  }
}
