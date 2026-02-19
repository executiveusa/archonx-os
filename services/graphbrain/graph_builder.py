from __future__ import annotations

from collections import defaultdict
from itertools import combinations

from services.graphbrain.repo_indexer import RepoIndex


class GraphBuilder:
    def build_repo_graph(self, index: RepoIndex) -> dict:
        counts: dict[tuple[str, str], float] = defaultdict(float)
        window = 5
        terms = index.terms
        for i, left in enumerate(terms):
            for j in range(i + 1, min(i + window, len(terms))):
                right = terms[j]
                if left == right:
                    continue
                edge = tuple(sorted((left, right)))
                counts[edge] += 1 / (j - i)

        edges = [
            {"a": a, "b": b, "weight": round(weight, 4)}
            for (a, b), weight in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:4000]
        ]
        nodes = sorted({edge["a"] for edge in edges} | {edge["b"] for edge in edges})
        return {"repo": index.slug, "status": index.status, "nodes": nodes, "edges": edges}

    def build_global_graph(self, repo_graphs: list[dict]) -> dict:
        merged: dict[tuple[str, str], float] = defaultdict(float)
        for repo_graph in repo_graphs:
            for edge in repo_graph["edges"]:
                merged[(edge["a"], edge["b"])] += edge["weight"]

        edges = [
            {"a": a, "b": b, "weight": round(weight, 4)}
            for (a, b), weight in sorted(merged.items(), key=lambda item: item[1], reverse=True)[:6000]
        ]
        nodes = sorted({edge["a"] for edge in edges} | {edge["b"] for edge in edges})
        return {"nodes": nodes, "edges": edges, "repo_count": len(repo_graphs)}

    def similarity(self, indexes: list[RepoIndex]) -> list[dict]:
        rows: list[dict] = []
        for left, right in combinations(indexes, 2):
            lterms = set(left.terms)
            rterms = set(right.terms)
            if not (lterms or rterms):
                score = 0.0
            else:
                score = len(lterms & rterms) / len(lterms | rterms)
            rows.append(
                {
                    "left": left.slug,
                    "right": right.slug,
                    "jaccard": round(score, 4),
                    "shared_terms": sorted(list(lterms & rterms))[:25],
                }
            )
        return sorted(rows, key=lambda row: row["jaccard"], reverse=True)
