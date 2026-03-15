# Future Upgrade TODO: HTTP-served Toolbox

Current mode is **git-pull** for simplicity.

When scaling to enterprise deployments, upgrade toolbox delivery to HTTP service (kernel/YAPP-backed) with:
- versioned and signed toolbox snapshots,
- audit logging for toolbox fetches,
- cache validation and contract hash pinning,
- rollout controls by environment.
