# Access Kernel Security Notes

Threat model highlights:

- Credential sprawl from `.env` and hardcoded keys
- Untracked privileged actions by agents
- Voice spoofing and brute-force call attempts
- Policy drift over time

Safe defaults:

- Deny by default ABAC policy
- `work_item_id` mandatory for privileged actions
- Secrets encrypted at rest and never returned in raw form
- Voice authentication uses allowlist + passphrase + PIN
- Biometric speaker verification is optional and disabled by default
- Audit JSONL append-only export path
- Evidence pack includes policy hash + config snapshot + audit window

Hardening next steps:

- Replace dev master key fallback with KMS/HSM only
- Add signed/tamper-evident audit chain
- Add SIEM export sink (OTLP/Splunk)
- Add SCIM and stronger RBAC
