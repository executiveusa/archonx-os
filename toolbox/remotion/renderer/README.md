# ArchonX Remotion Renderer (stub)

This folder is the integration point for `archonx-remotion-renderer`.

Required endpoints:
- `POST /v1/render`
- `GET /v1/render/{job_id}`
- `GET /v1/health`

Security requirements:
- require grant + work item ID,
- emit audit event for request and completion,
- support `ARCHONX_KERNEL_PROVIDER=mock` for local development.
