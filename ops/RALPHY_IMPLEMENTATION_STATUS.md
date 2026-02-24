# Ralphy-Inspired Control-Plane Implementation Status

## Completed in this pass

1. Added 7-phase GraphBrain loop runtime:
- plan
- implement
- test
- evaluate
- patch
- repeat
- ship

File: `services/graphbrain/runtime.py`

2. Added loop CLI controls:
- `--loop`
- `--max-iterations`
- `--max-retries`
- `--retry-delay`
- `--fail-on-high-risk`

File: `archonx/cli.py`

3. Added loop-mode test coverage.

File: `tests/test_graphbrain_loop.py`

4. Added root Docker packaging for control-plane API runtime.

Files:
- `Dockerfile`
- `.dockerignore`

5. Added Vercel fleet inventory sync utility (API-based).

File: `scripts/vercel_fleet_sync.py`
Outputs:
- `data/vercel/projects.json`
- `data/vercel/repo_map.json`

6. Added bootstrap script for required CLIs on Windows.

File: `scripts/bootstrap_dev_cli.ps1`

## Example commands

```powershell
# Run graphbrain loop in light mode
python -m archonx.cli graphbrain run --mode light --loop --max-iterations 3

# Build Docker image
docker build -t archonx:latest .

# Run ArchonX API in container
docker run --rm -p 8080:8080 archonx:latest

# Install CLIs if missing
powershell -ExecutionPolicy Bypass -File scripts/bootstrap_dev_cli.ps1 -InstallNode -InstallGitHubCli -InstallVercel

# Sync Vercel project inventory
$env:VERCEL_TOKEN = "<token>"
python scripts/vercel_fleet_sync.py
```

## Security note

Do not store raw secrets in repo files. Use environment variables or managed secret backends. Rotate any token that was shared in plaintext.
