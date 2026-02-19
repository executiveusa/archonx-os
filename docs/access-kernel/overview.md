# Access Kernel Overview

Access Kernel is Archon-X's one-shot login + secrets broker + audited access subsystem.

Goal:
Log in once, then receive short-lived, auditable access to tools and resources without distributing raw long-lived secrets.

## Core services

- `services/access-kernel`: policy + grants + encrypted secrets + audit/evidence
- `services/voice-gateway`: Twilio-compatible call-in control with passphrase + PIN
- `cli/archonxctl`: operator CLI for login, grants, secrets upload, audit export, doctor

## Security defaults

- Deny by default policy
- Work item required for privileged operations (`work_item_id`)
- No raw secret value returned by APIs/UI
- Voice biometric plugin model exists but is OFF by default

## Text Diagram

User/Agent -> archonxctl/dashboard/voice -> Access Kernel API

Access Kernel -> policy evaluation -> grant decision -> audit JSONL

Access Kernel -> encrypted secret store -> ephemeral handle previews

Voice Gateway -> allowlist + passphrase/PIN + rate limits -> action router -> Access Kernel
