"""Bead: bead.graphbrain.runtime.v1 | Ralphy: PLAN->IMPLEMENT->TEST->EVALUATE->PATCH->REPEAT."""

from __future__ import annotations

from pathlib import Path

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
