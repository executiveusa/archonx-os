param(
  [switch]$DryRun,
  [switch]$ReportOnly
)

$args = @()
if ($DryRun) { $args += "--dry-run" }
if ($ReportOnly) { $args += "--report-only" }

Push-Location (Join-Path $PSScriptRoot "..\..")
py -3 ops\runner\main.py @args
Pop-Location
