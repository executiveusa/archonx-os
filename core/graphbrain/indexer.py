from pathlib import Path

TEXT_GLOBS = ["README*", "docs/**/*", "src/**/*", "app/**/*", "server/**/*", ".github/workflows/*", "openapi.*", "swagger.*", "specs/**/*"]
MANIFESTS = ["package.json", "pnpm-lock.yaml", "requirements.txt", "pyproject.toml", "go.mod", "openclaw.plugin.json"]


class GraphBrainIndexer:
    def __init__(self, root: Path):
        self.root = root

    def discover_files(self) -> list[Path]:
        files: list[Path] = []
        for pattern in TEXT_GLOBS + MANIFESTS:
            files.extend(self.root.glob(pattern))
        return [p for p in files if p.is_file()]

    def build_corpus(self, limit_chars: int = 20000) -> list[str]:
        corpus = []
        for file in self.discover_files():
            try:
                corpus.append(file.read_text(errors="ignore")[:limit_chars])
            except OSError:
                continue
        return corpus
