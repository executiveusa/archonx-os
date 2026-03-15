from collections import Counter, defaultdict


def weighted_degree(edges: dict[tuple[str, str], float]) -> dict[str, float]:
    degree = defaultdict(float)
    for (left, right), weight in edges.items():
        degree[left] += weight
        degree[right] += weight
    return dict(degree)


def top_bridge_terms(edges: dict[tuple[str, str], float], limit: int = 10) -> list[dict]:
    # Approximate bridge ranking with weighted degree in environments without networkx/igraph.
    degree = weighted_degree(edges)
    ranked = sorted(degree.items(), key=lambda item: item[1], reverse=True)[:limit]
    return [{"term": term, "betweenness": score} for term, score in ranked]


def naive_clusters(tokens: list[str], bucket_size: int = 100) -> list[list[str]]:
    counts = Counter(tokens)
    sorted_terms = [term for term, _ in counts.most_common()]
    return [sorted_terms[i:i + bucket_size] for i in range(0, len(sorted_terms), bucket_size)]
