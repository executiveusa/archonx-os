# Meeting Tools

Cross-repo meeting bridge toolkit for `archonx-os` + `openclaw`.

## Scripts

- `scripts/repo_meeting_link.ps1`: low-level event writer/reader for chat + job status.
- `scripts/check_meeting_completion.ps1`: validates both repos present and no open jobs.
- `scripts/run-meeting-sync.ps1`: one-command parallel sync run across both repos.
- `scripts/meeting-self-improve.ps1`: self-review + optional quick fixes.

## Quick Start

Run one parallel sync across both repos:

```powershell
Set-Location "C:\archonx-os-main"
powershell -ExecutionPolicy Bypass -File scripts/run-meeting-sync.ps1
```

Review and improve tooling health:

```powershell
Set-Location "C:\archonx-os-main"
powershell -ExecutionPolicy Bypass -File scripts/meeting-self-improve.ps1
```

Apply quick fixes (create missing channel dir, auto-close open jobs):

```powershell
Set-Location "C:\archonx-os-main"
powershell -ExecutionPolicy Bypass -File scripts/meeting-self-improve.ps1 -ApplyQuickFixes
```

## Outputs

- Shared channel log: `data/meeting-link/meeting.jsonl`
- Self-improvement report: `data/meeting-link/self-improve-report.json`
