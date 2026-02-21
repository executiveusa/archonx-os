# ARCHONX:SYNTHIA — Security Threat Model

**Version:** 0.1.0 — MVP  
**Status:** DRAFT (P0)  
**Date:** 2026-02-21  

---

## 1. Security Principles

1. **Least Privilege** — every component gets minimum required access
2. **Default Deny** — network, tools, and actions are blocked unless explicitly allowed
3. **Ephemeral Compute** — Orgo computers and sandbox containers are disposable
4. **Human-in-the-Loop** — irreversible actions require explicit approval
5. **Audit Everything** — every tool call logged with redacted I/O
6. **Secrets Isolation** — secrets live only in env vars, never in code/logs/UI

## 2. Threat Matrix

| ID | Threat | Likelihood | Impact | Mitigation |
|----|--------|-----------|--------|------------|
| T1 | Agent exfiltrates secrets via tool output | Medium | Critical | Secrets only in env vars; structured redaction in ToolResult; no shell access by default |
| T2 | Agent makes unauthorized purchases/payments | Medium | Critical | Approval gate on all payment actions; `APPROVAL_REQUIRED_ACTIONS` enforced in PolicyEngine |
| T3 | Agent sends unauthorized external communications | Medium | High | Approval gate on email/message/calendar actions |
| T4 | Code-runner escapes sandbox | Low | Critical | Non-root user; read-only FS; no Docker socket mount; no `--privileged`; resource limits |
| T5 | Agent loops indefinitely, consuming resources | Medium | Medium | Budget enforcement: max_steps, max_tool_calls, max_runtime; kill switch in UI |
| T6 | Prompt injection via user voice input | Medium | Medium | Input sanitization; XML escaping in TwiML; tool allowlisting prevents arbitrary execution |
| T7 | Orgo computer accesses sensitive sites | Medium | High | Egress domain allowlist; Orgo computers destroyed after job (TTL) |
| T8 | SSRF from server to internal services | Low | High | Egress proxy with domain allowlist; no raw IP access |
| T9 | Secrets leaked in logs | Medium | Critical | structlog with redaction; never log env var values; `[REDACTED]` in ToolResult |
| T10 | Unauthorized access to Control Tower | Medium | High | Auth required (post-MVP: SSO/OAuth); CORS locked to known origins |
| T11 | Supply chain / dependency compromise | Low | High | Pinned dependencies; minimal base images; no unnecessary packages |
| T12 | Data at rest exposure | Low | Medium | Notion handles encryption; local volumes ephemeral; no PII in code-runner |

## 3. Security Controls — Implementation Status

| Control | Status | Location |
|---------|--------|----------|
| Tool allowlisting | ✅ Implemented (stub) | `packages/core/policy.py` |
| Approval-required actions list | ✅ Implemented (stub) | `packages/core/policy.py` |
| Egress domain allowlist | ✅ Defined | `packages/core/policy.py` + `.env.example` |
| Budget enforcement | ✅ Implemented (stub) | `packages/core/agent_runtime.py` |
| Non-root code-runner | ✅ Implemented | `infra/code-runner/Dockerfile` |
| Read-only FS (code-runner) | ✅ Implemented | `infra/docker-compose.yml` |
| Resource limits (code-runner) | ✅ Implemented | `infra/docker-compose.yml` |
| No Docker socket mount | ✅ By omission | `infra/docker-compose.yml` |
| XML escape in TwiML | ✅ Implemented | `apps/server/app/routes/voice.py` |
| Path traversal protection | ✅ Implemented | `infra/code-runner/runner_api.py` |
| CORS policy | ✅ Implemented | `apps/server/app/main.py` |
| Secrets in env only | ✅ By design | `.env.example` + `.gitignore` |
| Structured logging | ✅ Implemented | `apps/server/app/main.py` (structlog) |
| Auth on Control Tower | 🔲 Post-MVP | — |
| SSO / OAuth | 🔲 Post-MVP | — |
| Egress proxy container | 🔲 Post-MVP | `infra/proxy/` |
| Secret rotation automation | 🔲 Post-MVP | — |
| Rate limiting on API | 🔲 Post-MVP | — |

## 4. Secrets Handling Rules

1. All secrets stored in `.env` file (gitignored)
2. `.env.example` provides template with empty values
3. Code reads secrets via `pydantic-settings` (env vars only)
4. Logs must never contain secret values
5. If a secret is missing at startup, fail loudly — do not fall back to defaults
6. API keys are scoped and short-lived where possible
7. builder/CI never outputs secret values

## 5. Post-MVP Hardening Checklist

- [ ] Add OAuth2 / SSO to Control Tower
- [ ] Implement egress proxy container with allowlist enforcement
- [ ] Add rate limiting to all API endpoints
- [ ] Implement secret rotation automation
- [ ] Add CSP headers to UI
- [ ] Run OWASP ZAP scan against server
- [ ] Add audit log export (SIEM-compatible)
- [ ] Implement network policies for K8s deployment
- [ ] Add mTLS between internal services
- [ ] Penetration test the Orgo integration flow
