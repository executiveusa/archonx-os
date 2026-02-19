from collections import defaultdict
from itertools import combinations


def build_cooccurrence_graph(tokens: list[str], window: int = 4) -> dict[tuple[str, str], float]:
    edges: dict[tuple[str, str], float] = defaultdict(float)
    for i, left in enumerate(tokens):
        right_limit = min(i + window, len(tokens))
        for j in range(i + 1, right_limit):
            right = tokens[j]
            if left == right:
                continue
            a, b = sorted((left, right))
            distance = j - i
            edges[(a, b)] += 1 / distance
    return dict(edges)


def graph_nodes(edges: dict[tuple[str, str], float]) -> set[str]:
    out = set()
    for left, right in edges.keys():
        out.add(left)
        out.add(right)
    return out
