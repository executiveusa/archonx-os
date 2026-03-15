from pathlib import Path


def extract(path: Path) -> str:
    return path.read_text(errors="ignore")
