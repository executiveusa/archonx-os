from __future__ import annotations

from dataclasses import dataclass

from .analyze import naive_clusters, top_bridge_terms
from .graph_builder import build_cooccurrence_graph, graph_nodes
from .similarity import recommendation_confidence
from .tokenize import normalize_tokens


@dataclass
class GraphBrainPipeline:
    bead_id: str = "bead.graphbrain.bootstrap.v1"
    window: int = 4

    def run(self, corpus: list[str]) -> dict:
        tokens: list[str] = []
        for text in corpus:
            tokens.extend(normalize_tokens(text))
        edges = build_cooccurrence_graph(tokens, window=self.window)
        bridges = top_bridge_terms(edges, limit=10)
        clusters = naive_clusters(tokens)
        return {
            "bead_id": self.bead_id,
            "graph": {
                "nodes": len(graph_nodes(edges)),
                "edges": len(edges),
                "clusters": len(clusters),
                "bridge_terms_top": bridges,
            },
            "confidence_example": recommendation_confidence(0.8, 0.6, 0.5, 0.4, 0.7),
        }
