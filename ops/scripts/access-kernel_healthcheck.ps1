$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$reportDir = Join-Path $root 'ops\reports'
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$ts = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$outFile = Join-Path $reportDir ("access-kernel_health_$ts.json")
$health = Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:8090/v1/health'
$voice = Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:8091/v1/health'
$payload = [ordered]@{ generatedAt = (Get-Date).ToUniversalTime().ToString('o'); accessKernel = $health; voiceGateway = $voice }
$payload | ConvertTo-Json -Depth 8 | Set-Content -Path $outFile -Encoding UTF8
Write-Host $outFile
