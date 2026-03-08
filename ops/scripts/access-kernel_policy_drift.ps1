$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$reportDir = Join-Path $root 'ops\reports'
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$policyFile = Join-Path $root 'services\access-kernel\config\policy.json'
$baseline = Join-Path $reportDir 'policy.hash'
$current = (Get-FileHash -Algorithm SHA256 -Path $policyFile).Hash.ToLower()
if (-not (Test-Path $baseline)) { Set-Content -Path $baseline -Value $current -Encoding UTF8 }
$baseHash = (Get-Content -Path $baseline -Raw).Trim()
$status = if ($baseHash -eq $current) { 'ok' } else { 'drift_detected' }
$ts = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$outFile = Join-Path $reportDir ("policy_drift_$ts.json")
@{ generatedAt=(Get-Date).ToUniversalTime().ToString('o'); status=$status; baseline=$baseHash; current=$current } | ConvertTo-Json -Depth 5 | Set-Content -Path $outFile -Encoding UTF8
Write-Host $outFile
