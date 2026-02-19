from collections import Counter
from math import sqrt


def cosine_similarity(a: Counter, b: Counter) -> float:
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
    mag_a = sqrt(sum(v * v for v in a.values()))
    mag_b = sqrt(sum(v * v for v in b.values()))
    if not mag_a or not mag_b:
        return 0.0
    return dot / (mag_a * mag_b)


def jaccard(a: set[str], b: set[str]) -> float:
    if not (a or b):
        return 0.0
    return len(a & b) / len(a | b)


def recommendation_confidence(cosine_tfidf: float, jaccard_dependencies: float, api_overlap: float, cluster_overlap: float, bridge_alignment: float) -> float:
    score = (
        0.45 * cosine_tfidf
        + 0.20 * jaccard_dependencies
        + 0.15 * api_overlap
        + 0.10 * cluster_overlap
        + 0.10 * bridge_alignment
    )
    return max(0.0, min(1.0, round(score, 4)))
