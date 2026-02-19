$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$reportDir = Join-Path $root 'ops\reports'
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$workItemId = 'WI-SELFTEST-' + (Get-Date).ToUniversalTime().ToString('yyyyMMdd')

$loginBody = @{ principal = 'selftest'; principal_type = 'human'; duration_minutes = 60 } | ConvertTo-Json
$login = Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8090/v1/login/mock' -ContentType 'application/json' -Body $loginBody

$secretBody = @{ principal = 'selftest'; work_item_id = $workItemId; name = 'selftest-secret'; payload = @{ API_KEY = 'demo' } } | ConvertTo-Json -Depth 5
$secret = Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8090/v1/secrets/upload' -ContentType 'application/json' -Body $secretBody

$grantBody = @{ principal = 'selftest'; principal_type = 'human'; work_item_id = $workItemId; resource = 'github'; action = 'write'; duration_minutes = 15 } | ConvertTo-Json
$grant = Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8090/v1/grants/request' -ContentType 'application/json' -Body $grantBody

$approveBody = @{ grant_id = $grant.grant_id; approver = 'selftest-admin'; work_item_id = $workItemId } | ConvertTo-Json
$approve = Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8090/v1/grants/approve' -ContentType 'application/json' -Body $approveBody

$voiceBody = @{ caller = '+15550000001'; passphrase = 'archonx-passphrase'; pin = '1234'; action = 'status'; work_item_id = $workItemId } | ConvertTo-Json
$voice = Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8091/v1/voice/dev/simulate' -ContentType 'application/json' -Body $voiceBody
$evidence = Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:8090/v1/evidence/export'
$audit = Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:8090/v1/audit/export?format=jsonl'
$ts = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$outFile = Join-Path $reportDir ("access-kernel_selftest_$ts.json")
@{ generatedAt=(Get-Date).ToUniversalTime().ToString('o'); work_item_id=$workItemId; login=$login; secretUpload=$secret; grantRequest=$grant; grantApprove=$approve; voice=$voice; evidence=$evidence } | ConvertTo-Json -Depth 8 | Set-Content -Path $outFile -Encoding UTF8
$auditFile = Join-Path $reportDir ("access-kernel_audit_$ts.jsonl")
Set-Content -Path $auditFile -Value $audit.data -Encoding UTF8
Write-Host $outFile
