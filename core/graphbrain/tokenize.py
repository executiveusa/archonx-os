import re
from collections import Counter

STOPWORDS = {"the", "and", "for", "with", "from", "that", "this", "into", "are", "was", "were"}


def normalize_tokens(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z_][A-Za-z0-9_\-]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


def ngram_counter(texts: list[str]) -> Counter:
    c = Counter()
    for text in texts:
        tokens = normalize_tokens(text)
        c.update(tokens)
    return c
