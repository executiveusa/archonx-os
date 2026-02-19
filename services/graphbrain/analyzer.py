from __future__ import annotations

from collections import Counter, defaultdict


class Analyzer:
    def bridge_terms(self, edges: list[dict], limit: int = 20) -> list[dict]:
        degree: dict[str, float] = defaultdict(float)
        for edge in edges:
            degree[edge["a"]] += edge["weight"]
            degree[edge["b"]] += edge["weight"]
        return [
            {"term": term, "score": round(score, 4)}
            for term, score in sorted(degree.items(), key=lambda item: item[1], reverse=True)[:limit]
        ]

    def detect_clusters(self, nodes: list[str], bucket_size: int = 50) -> list[list[str]]:
        sorted_nodes = sorted(nodes)
        return [sorted_nodes[i : i + bucket_size] for i in range(0, len(sorted_nodes), bucket_size)]

    def gaps(self, repo_graphs: list[dict]) -> list[dict]:
        findings = []
        for graph in repo_graphs:
            if graph["status"] != "available":
                findings.append({"repo": graph["repo"], "severity": "high", "gap": "repository_unavailable"})
                continue
            if not graph["nodes"]:
                findings.append({"repo": graph["repo"], "severity": "medium", "gap": "no_indexable_content"})
        return findings

    def consolidation_candidates(self, similarity_rows: list[dict], threshold: float = 0.35) -> list[dict]:
        return [
            {
                "type": "consider_consolidation",
                "left": row["left"],
                "right": row["right"],
                "score": row["jaccard"],
            }
            for row in similarity_rows
            if row["jaccard"] >= threshold
        ]

    def risk_findings(self, indexes: list, allowed_endpoints: set[str]) -> list[dict]:
        findings: list[dict] = []
        for index in indexes:
            if index.status != "available":
                continue
            text = "\n".join(doc.content for doc in index.docs)
            if "http://" in text:
                findings.append({"repo": index.slug, "severity": "medium", "risk": "insecure_http_reference"})
            endpoints = [token for token in text.split() if token.startswith("https://")]
            for endpoint in endpoints[:150]:
                base = endpoint.strip().rstrip("/\",').)")
                if not any(base.startswith(allow) for allow in allowed_endpoints):
                    findings.append({"repo": index.slug, "severity": "low", "risk": "endpoint_not_allowlisted", "endpoint": base})
                    break
        return findings

    def repo_status(self, indexes: list) -> dict:
        counts = Counter(index.status for index in indexes)
        return {"available": counts.get("available", 0), "unavailable": counts.get("unavailable", 0)}
