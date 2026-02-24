"""Bead: bead.graphbrain.runtime.v1 | Ralphy: PLAN->IMPLEMENT->TEST->EVALUATE->PATCH->REPEAT."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from time import sleep
from typing import Any

from services.graphbrain.analyzer import Analyzer
from services.graphbrain.graph_builder import GraphBuilder
from services.graphbrain.repo_indexer import RepoIndexer, load_target_repos
from services.graphbrain.work_orders import generate_work_orders

ALLOWED_REPORT_ENDPOINTS = {
    "https://api.github.com/",
    "https://github.com/",
    "https://hooks.slack.com/",
}


class GraphBrainRuntime:
    def __init__(self, root: Path):
        self.root = root
        self.repos = load_target_repos(root)

    def run(self, mode: str = "full") -> dict:
        return self._build_payload(mode=mode)

    def run_loop(
        self,
        mode: str = "full",
        max_iterations: int = 3,
        max_retries: int = 2,
        retry_delay: int = 2,
        fail_on_high_risk: bool = False,
    ) -> dict:
        """Run a guarded multi-phase loop inspired by the Ralphy execution model.

        Phases:
        1. plan
        2. implement
        3. test
        4. evaluate
        5. patch
        6. repeat
        7. ship
        """
        if max_iterations < 1:
            max_iterations = 1
        if max_retries < 0:
            max_retries = 0
        if retry_delay < 0:
            retry_delay = 0

        phase_history: list[dict[str, Any]] = []
        last_payload: dict[str, Any] | None = None

        for iteration in range(1, max_iterations + 1):
            retries = 0
            while True:
                try:
                    payload = self._build_payload(mode=mode)

                    # 1) plan
                    plan_phase = {
                        "name": "plan",
                        "ok": True,
                        "repo_count": len(payload["repo_graphs"]),
                        "work_order_count": len(payload["work_orders"]),
                    }

                    # 2) implement (prepare action-ready work orders)
                    payload["work_orders"] = self._annotate_work_orders(payload["work_orders"])
                    implement_phase = {
                        "name": "implement",
                        "ok": True,
                        "execution_ready": len(payload["work_orders"]),
                    }

                    # 3) test (validate payload integrity)
                    test_report = self._run_quality_tests(payload)
                    test_phase = {"name": "test", **test_report}

                    # 4) evaluate
                    evaluation = self._evaluate(payload, test_report)
                    evaluate_phase = {"name": "evaluate", **evaluation}

                    # 5) patch (append remediation work orders)
                    patch_orders = self._build_patch_orders(payload, test_report, evaluation)
                    if patch_orders:
                        payload["work_orders"].extend(patch_orders)
                    patch_phase = {
                        "name": "patch",
                        "ok": True,
                        "patch_orders_added": len(patch_orders),
                    }

                    # 6) repeat decision
                    should_repeat = self._should_repeat(payload, test_report, evaluation, iteration, max_iterations)
                    repeat_phase = {
                        "name": "repeat",
                        "ok": True,
                        "should_repeat": should_repeat,
                    }

                    # 7) ship snapshot metadata for downstream CI/CD jobs
                    ship_manifest = self._build_ship_manifest(payload, iteration)
                    payload["ship_manifest"] = ship_manifest
                    ship_phase = {"name": "ship", "ok": True, "manifest_id": ship_manifest["id"]}

                    phase_history.append(
                        {
                            "iteration": iteration,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "phases": [
                                plan_phase,
                                implement_phase,
                                test_phase,
                                evaluate_phase,
                                patch_phase,
                                repeat_phase,
                                ship_phase,
                            ],
                        }
                    )

                    payload["loop"] = {
                        "mode": mode,
                        "model": "ralphy-inspired",
                        "max_iterations": max_iterations,
                        "iterations_completed": iteration,
                        "phase_history": phase_history,
                        "status": "ok" if test_report["ok"] else "degraded",
                    }

                    if fail_on_high_risk and evaluation["high_risk_count"] > 0:
                        payload["loop"]["status"] = "failed"
                        payload["loop"]["failure_reason"] = "high_risk_findings_present"
                        return payload

                    last_payload = payload
                    if not should_repeat:
                        return payload
                    break
                except Exception as exc:  # pragma: no cover - defensive runtime protection
                    retries += 1
                    if retries > max_retries:
                        if last_payload is None:
                            return {
                                "global_graph": {"nodes": [], "edges": [], "repo_count": 0},
                                "repo_graphs": [],
                                "similarity": [],
                                "consolidation_candidates": [],
                                "risk_findings": [],
                                "work_orders": [],
                                "repo_status": {"available": 0, "unavailable": 0},
                                "dashboard_registry": {"repos": []},
                                "dashboard_status": {"repos": []},
                                "loop": {
                                    "mode": mode,
                                    "model": "ralphy-inspired",
                                    "max_iterations": max_iterations,
                                    "iterations_completed": iteration,
                                    "phase_history": phase_history,
                                    "status": "failed",
                                    "failure_reason": str(exc),
                                },
                            }

                        last_payload["loop"] = {
                            "mode": mode,
                            "model": "ralphy-inspired",
                            "max_iterations": max_iterations,
                            "iterations_completed": iteration,
                            "phase_history": phase_history,
                            "status": "failed",
                            "failure_reason": str(exc),
                        }
                        return last_payload

                    sleep(retry_delay)

        if last_payload is None:
            last_payload = self._build_payload(mode=mode)
        return last_payload

    def _build_payload(self, mode: str = "full") -> dict:
        active_repos = self.repos if mode == "full" else ["executiveusa/archonx-os"]
        indexer = RepoIndexer(self.root, active_repos)
        indexes = indexer.index_all()

        builder = GraphBuilder()
        repo_graphs = [builder.build_repo_graph(index) for index in indexes]
        global_graph = builder.build_global_graph(repo_graphs)
        similarity_rows = builder.similarity(indexes)

        analyzer = Analyzer()
        bridge_terms = analyzer.bridge_terms(global_graph["edges"])
        clusters = analyzer.detect_clusters(global_graph["nodes"])
        gaps = analyzer.gaps(repo_graphs)
        consolidation = analyzer.consolidation_candidates(similarity_rows)
        risks = analyzer.risk_findings(indexes, ALLOWED_REPORT_ENDPOINTS)
        status = analyzer.repo_status(indexes)

        work_orders = generate_work_orders(consolidation, risks, gaps)
        return {
            "global_graph": {**global_graph, "bridge_terms": bridge_terms, "clusters": clusters},
            "repo_graphs": repo_graphs,
            "similarity": similarity_rows,
            "consolidation_candidates": consolidation,
            "risk_findings": risks,
            "work_orders": work_orders,
            "repo_status": status,
            "dashboard_registry": {
                "repos": [
                    {"slug": index.slug, "tags": ["graphbrain"], "owner": "executiveusa"}
                    for index in indexes
                ]
            },
            "dashboard_status": {
                "repos": [
                    {
                        "slug": index.slug,
                        "status": index.status,
                        "doc_count": len(index.docs),
                        "term_count": len(index.terms),
                    }
                    for index in indexes
                ]
            },
        }

    def _annotate_work_orders(self, work_orders: list[dict]) -> list[dict]:
        enriched: list[dict] = []
        for order in work_orders:
            order_type = str(order.get("type", "execution"))
            priority = "medium"
            if order.get("id", "").startswith("wo-risk"):
                priority = "high"
            elif order.get("id", "").startswith("wo-gap"):
                priority = "high"
            elif order_type == "reasoning":
                priority = "low"

            enriched.append(
                {
                    **order,
                    "priority": priority,
                    "phase": "implement",
                    "runner": "graphbrain-agent",
                }
            )
        return enriched

    def _run_quality_tests(self, payload: dict) -> dict[str, Any]:
        checks: list[dict[str, Any]] = []

        required_keys = [
            "global_graph",
            "repo_graphs",
            "similarity",
            "consolidation_candidates",
            "risk_findings",
            "work_orders",
            "repo_status",
            "dashboard_registry",
            "dashboard_status",
        ]
        for key in required_keys:
            checks.append({"check": f"payload_key:{key}", "ok": key in payload})

        checks.append(
            {
                "check": "repo_graph_count_matches_status",
                "ok": len(payload.get("repo_graphs", [])) >= payload.get("repo_status", {}).get("available", 0),
            }
        )

        checks.append(
            {
                "check": "dashboard_status_matches_repo_graphs",
                "ok": len(payload.get("dashboard_status", {}).get("repos", [])) == len(payload.get("repo_graphs", [])),
            }
        )

        failed = [check for check in checks if not check["ok"]]
        return {"ok": len(failed) == 0, "checks": checks, "failed_count": len(failed)}

    def _evaluate(self, payload: dict, test_report: dict[str, Any]) -> dict[str, Any]:
        high_risk = [r for r in payload.get("risk_findings", []) if r.get("severity") == "high"]
        medium_risk = [r for r in payload.get("risk_findings", []) if r.get("severity") == "medium"]
        gaps = [g for g in payload.get("work_orders", []) if str(g.get("id", "")).startswith("wo-gap")]
        degraded = (not test_report.get("ok", False)) or bool(high_risk)

        return {
            "ok": not degraded,
            "high_risk_count": len(high_risk),
            "medium_risk_count": len(medium_risk),
            "gap_work_order_count": len(gaps),
            "status": "degraded" if degraded else "healthy",
        }

    def _build_patch_orders(
        self,
        payload: dict,
        test_report: dict[str, Any],
        evaluation: dict[str, Any],
    ) -> list[dict[str, Any]]:
        patch_orders: list[dict[str, Any]] = []
        if not test_report.get("ok", False):
            patch_orders.append(
                {
                    "id": "wo-patch-payload-integrity",
                    "assignee": "Devika",
                    "type": "execution",
                    "priority": "high",
                    "phase": "patch",
                    "summary": "Repair graphbrain payload integrity checks before next iteration.",
                    "source": {
                        "failed_checks": [
                            check for check in test_report.get("checks", []) if not check.get("ok", False)
                        ]
                    },
                }
            )

        if evaluation.get("high_risk_count", 0) > 0:
            patch_orders.append(
                {
                    "id": "wo-patch-high-risk",
                    "assignee": "Devika",
                    "type": "execution",
                    "priority": "critical",
                    "phase": "patch",
                    "summary": "Mitigate high-severity risk findings before autonomous promotion.",
                    "source": {
                        "high_risk_findings": [
                            risk for risk in payload.get("risk_findings", []) if risk.get("severity") == "high"
                        ]
                    },
                }
            )

        return patch_orders

    def _should_repeat(
        self,
        payload: dict,
        test_report: dict[str, Any],
        evaluation: dict[str, Any],
        iteration: int,
        max_iterations: int,
    ) -> bool:
        if iteration >= max_iterations:
            return False
        if not test_report.get("ok", False):
            return True
        if evaluation.get("high_risk_count", 0) > 0:
            return True
        if len(payload.get("work_orders", [])) == 0:
            return False
        return False

    def _build_ship_manifest(self, payload: dict, iteration: int) -> dict[str, Any]:
        manifest_id = f"ship-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{iteration}"
        return {
            "id": manifest_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "iteration": iteration,
            "repo_status": payload.get("repo_status", {}),
            "work_order_count": len(payload.get("work_orders", [])),
            "risk_count": len(payload.get("risk_findings", [])),
        }
