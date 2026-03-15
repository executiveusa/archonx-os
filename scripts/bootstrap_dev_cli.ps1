param(
  [switch]$InstallVercel,
  [switch]$InstallGitHubCli,
  [switch]$InstallNode,
  [switch]$InstallPython
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Test-Cmd([string]$name) {
  return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

function Require-Winget() {
  if (-not (Test-Cmd 'winget')) {
    throw 'winget is required for this bootstrap script on Windows.'
  }
}

$actions = @()

if ($InstallNode -and -not (Test-Cmd 'node')) {
  Require-Winget
  winget install OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements
  $actions += 'Installed Node.js LTS'
}

if ($InstallPython -and -not (Test-Cmd 'python')) {
  Require-Winget
  winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
  $actions += 'Installed Python 3.11'
}

if ($InstallGitHubCli -and -not (Test-Cmd 'gh')) {
  Require-Winget
  winget install GitHub.cli --silent --accept-package-agreements --accept-source-agreements
  $actions += 'Installed GitHub CLI'
}

if ($InstallVercel -and -not (Test-Cmd 'vercel')) {
  if (-not (Test-Cmd 'npm')) {
    throw 'npm is required to install the Vercel CLI. Install Node.js first.'
  }
  npm install -g vercel
  $actions += 'Installed Vercel CLI'
}

$result = @{
  ok = $true
  vercel = (Test-Cmd 'vercel')
  gh = (Test-Cmd 'gh')
  node = (Test-Cmd 'node')
  python = (Test-Cmd 'python')
  actions = $actions
}

$result | ConvertTo-Json -Depth 4
