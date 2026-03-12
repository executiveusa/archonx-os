"""Routing engine — Maps repos + tasks to agent dispatch plans."""

from typing import List, Optional
from datetime import datetime, timezone

from archonx.repos.models import (
    Repo,
    DomainType,
    RepoPlacement,
    DispatchPlan,
    DispatchPlanAgent,
    DispatchPlanWorker,
    DispatchPlanIntegration,
)
from archonx.repos.registry import RepoRegistry
from archonx.orchestration.workers import build_default_worker_registry


class Router:
    """Routes repos + tasks to agent dispatch plans."""

    def __init__(self, registry: RepoRegistry):
        """Initialize router.

        Args:
            registry: RepoRegistry instance
        """
        self.registry = registry
        self.worker_registry = build_default_worker_registry()

    def route(
        self, repo_ids: List[int], task_name: str, task_intent: Optional[str] = None
    ) -> DispatchPlan:
        """Generate a dispatch plan for given repos and task.

        Args:
            repo_ids: List of repository IDs to route
            task_name: Name of the task to execute

        Returns:
            DispatchPlan with preflight steps, recommended agents, and metadata

        Raises:
            ValueError: If repo_ids is empty or invalid
        """
        if not repo_ids:
            raise ValueError("repo_ids cannot be empty")

        # Fetch all repo metadata
        repos_metadata = []
        team_ids = set()

        for repo_id in repo_ids:
            repo = self.registry.get_repo(repo_id)
            if not repo:
                raise ValueError(f"Repo ID {repo_id} not found in registry")

            repos_metadata.append(repo.to_dict())
            team_ids.add(repo.team_id)

        if len(team_ids) > 1:
            team_id = "multi_team"
            team_display = f"Multi-team ({', '.join(sorted(team_ids))})"
        else:
            team_id = list(team_ids)[0]
            team = self.registry.get_team(team_id)
            team_display = team.display if team else team_id

        # Determine recommended agents based on domain types
        domain_types = {repo["domain_type_id"] for repo in repos_metadata}
        recommended_agents = self._recommend_agents(domain_types)

        # Build preflight steps
        preflight_steps = self._build_preflight_steps()

        # Build dispatch plan
        now = datetime.now(timezone.utc).isoformat()
        plan = DispatchPlan(
            timestamp=now,
            repo_ids=repo_ids,
            task_name=task_name,
            task_intent=self._resolve_task_intent(repos_metadata, task_intent),
            team_id=team_id,
            repos_metadata=repos_metadata,
            preflight_steps=preflight_steps,
            recommended_agents=recommended_agents,
            recommended_workers=self._recommend_workers(
                repos_metadata, self._resolve_task_intent(repos_metadata, task_intent)
            ),
            required_integrations=self._required_integrations(
                repos_metadata, self._resolve_task_intent(repos_metadata, task_intent)
            ),
            notes=f"Task: {task_name} | Team: {team_display} | Repos: {len(repo_ids)} | Domains: {', '.join(sorted(domain_types))}",
        )

        return plan

    def _recommend_agents(self, domain_types: set) -> List[DispatchPlanAgent]:
        """Recommend agents based on domain types.

        Mapping:
        - saas: {design, backend, qa, sec, prd}
        - tool: {backend, sec, prd}
        - agent: {agent_ops, sec, prd}
        - template/content: {prd}
        - unknown: {recon, prd} + classification_required flag
        """
        agent_set = set()

        for domain_type in domain_types:
            if domain_type == DomainType.SAAS.value:
                agent_set.update(["design_agent", "backend_agent", "qa_agent", "sec_agent", "prd_agent"])
            elif domain_type == DomainType.TOOL.value:
                agent_set.update(["backend_agent", "sec_agent", "prd_agent"])
            elif domain_type == DomainType.AGENT.value:
                agent_set.update(["agent_ops_agent", "sec_agent", "prd_agent"])
            elif domain_type in (DomainType.TEMPLATE.value, DomainType.CONTENT.value):
                agent_set.add("prd_agent")
            elif domain_type == DomainType.UNKNOWN.value:
                agent_set.update(["recon_agent", "prd_agent"])

        # Define agent profiles
        agent_profiles = {
            "design_agent": {
                "role": "frontend_audit",
                "tools": ["playwright", "puppeteer", "lighthouse", "a11y"],
            },
            "backend_agent": {
                "role": "backend_audit",
                "tools": ["sast", "dependency_audit", "api_contract", "migration_check"],
            },
            "qa_agent": {
                "role": "e2e_validation",
                "tools": ["playwright", "test_runner"],
            },
            "sec_agent": {
                "role": "security_review",
                "tools": ["secret_scan", "sast", "dependency_audit"],
            },
            "prd_agent": {
                "role": "prd_writer",
                "tools": ["repo_intel", "issue_summarizer"],
            },
            "agent_ops_agent": {
                "role": "agent_orchestration",
                "tools": ["mcp", "github_api", "agent_dispatch"],
            },
            "recon_agent": {
                "role": "classification_and_recon",
                "tools": ["playwright", "puppeteer", "repo_intel", "classifier"],
            },
        }

        agents = [
            DispatchPlanAgent(
                id=agent_id,
                role=profile["role"],
                tools=profile["tools"],
            )
            for agent_id, profile in agent_profiles.items()
            if agent_id in agent_set
        ]

        # Sort for deterministic ordering
        agents.sort(key=lambda a: a.id)

        return agents

    def _resolve_task_intent(
        self, repos_metadata: List[dict], task_intent: Optional[str]
    ) -> str:
        """Resolve task intent from explicit input or repo placement/domain hints."""
        if task_intent:
            return task_intent

        placements = {repo.get("placement", RepoPlacement.UNKNOWN.value) for repo in repos_metadata}
        domains = {repo["domain_type_id"] for repo in repos_metadata}

        if RepoPlacement.FRONTEND_LAYER.value in placements:
            return "frontend_change"
        if RepoPlacement.WORKER_SERVICE.value in placements:
            return "worker_integration"
        if RepoPlacement.PLUGIN.value in placements:
            return "plugin_integration"
        if RepoPlacement.SIDECAR.value in placements:
            return "desktop_action"
        if DomainType.AGENT.value in domains:
            return "multi_agent"
        if DomainType.SAAS.value in domains or DomainType.TOOL.value in domains:
            return "code_change"
        return "repo_analysis"

    def _recommend_workers(
        self, repos_metadata: List[dict], task_intent: str
    ) -> List[DispatchPlanWorker]:
        """Recommend workers based on intent and placement metadata."""
        worker_ids = {
            worker.worker_id
            for worker in self.worker_registry.find_by_intent(task_intent)
        }

        placements = {repo.get("placement", RepoPlacement.UNKNOWN.value) for repo in repos_metadata}
        domains = {repo["domain_type_id"] for repo in repos_metadata}

        if RepoPlacement.WORKER_SERVICE.value in placements:
            worker_ids.add("agency_agents")
        if RepoPlacement.FRONTEND_LAYER.value in placements:
            worker_ids.add("goose")
        if DomainType.AGENT.value in domains:
            worker_ids.add("agency_agents")
        if task_intent in {"code_change", "repo_analysis", "worker_integration"}:
            worker_ids.add("darya_openhands")
        if task_intent == "desktop_action":
            worker_ids.add("darya_openhands")

        workers = []
        for worker_id in sorted(worker_ids):
            capability = self.worker_registry.get(worker_id)
            if not capability:
                continue
            workers.append(
                DispatchPlanWorker(
                    id=capability.worker_id,
                    role=capability.kind.value,
                    intents=capability.intents,
                    tools=capability.tools,
                    dependencies=capability.dependencies,
                )
            )
        return workers

    def _required_integrations(
        self, repos_metadata: List[dict], task_intent: str
    ) -> List[DispatchPlanIntegration]:
        """Return required control-path integrations for a dispatch plan."""
        integrations = {
            "mcp2cli": DispatchPlanIntegration(
                id="mcp2cli",
                role="invocation_gateway",
                required=True,
                rationale="Mandatory token-efficient tool invocation layer.",
            ),
            "DesktopCommanderMCP": DispatchPlanIntegration(
                id="DesktopCommanderMCP",
                role="control_tower",
                required=task_intent in {
                    "desktop_action",
                    "code_change",
                    "worker_integration",
                    "repo_analysis",
                },
                rationale="Primary machine-control gateway for local execution.",
            ),
        }

        placements = {repo.get("placement", RepoPlacement.UNKNOWN.value) for repo in repos_metadata}
        if RepoPlacement.MEMORY_LAYER.value in placements:
            integrations["Notion"] = DispatchPlanIntegration(
                id="Notion",
                role="memory_layer",
                required=True,
                rationale="Canonical memory backend for memory-layer repos.",
            )
        if RepoPlacement.FRONTEND_LAYER.value in placements:
            integrations["Cloudflare Tunnel"] = DispatchPlanIntegration(
                id="Cloudflare Tunnel",
                role="edge_access",
                required=False,
                rationale="Edge publishing path for frontend and product layers.",
            )

        ordered = [integrations[key] for key in sorted(integrations.keys())]
        return [integration for integration in ordered if integration.required]

    def _build_preflight_steps(self) -> List[str]:
        """Build required preflight verification steps.

        These steps MUST complete before any code execution or git operations.
        """
        return [
            "archonx mcp connect --profile default",
            "archonx mcp verify --require tools:playwright,puppeteer,git,github,vault",
            "archonx tokensaver enable --mode global --persist --compression smart --dedupe prompts --minify context",
            "archonx tokens baseline start --scope session",
        ]
