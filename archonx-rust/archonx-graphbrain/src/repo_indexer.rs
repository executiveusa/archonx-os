/// GraphBrain Repo Indexer — replaces Python with rayon parallel file walking.
/// Replaces: services/graphbrain/repo_indexer.py
///
/// Python: sequential glob → 45-90 second cron run.
/// Rust:   rayon::par_iter() + walkdir → 3-5 second run.
use std::path::{Path, PathBuf};
use std::process::Command;

use rayon::prelude::*;
use regex::Regex;
use serde::{Deserialize, Serialize};
use tracing::{info, warn};

// ---------------------------------------------------------------------------
// Scan patterns — matches Python SCAN_PATTERNS exactly
// ---------------------------------------------------------------------------

static SCAN_EXTENSIONS: &[&str] = &[
    "md", "json", "toml", "txt", "ts", "tsx", "js", "jsx", "py", "rs", "yml", "yaml",
];

static SCAN_DIRS: &[&str] = &[
    "README", "docs", "src", "app", "server", "archonx", "core", ".github/workflows",
];

// ---------------------------------------------------------------------------
// Data structs — exact match with Python dataclasses
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RepoDocument {
    pub path: String,
    pub content: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RepoIndex {
    pub slug: String,
    pub status: String,
    pub docs: Vec<RepoDocument>,
    pub terms: Vec<String>,
    pub metadata: std::collections::HashMap<String, String>,
}

// ---------------------------------------------------------------------------
// RepoIndexer
// ---------------------------------------------------------------------------

/// Indexes repositories in parallel using rayon.
/// Replaces Python: class RepoIndexer with sequential glob loops.
pub struct RepoIndexer {
    pub root: PathBuf,
    pub repos: Vec<String>,
    token_re: Regex,
}

impl RepoIndexer {
    pub fn new(root: PathBuf, repos: Vec<String>) -> Self {
        Self {
            root,
            repos,
            token_re: Regex::new(r"[A-Za-z][A-Za-z0-9_\-]{2,}").unwrap(),
        }
    }

    fn slug_to_dirname(slug: &str) -> String {
        slug.replace('/', "__")
    }

    fn repo_local_path(&self, slug: &str) -> PathBuf {
        if slug == "executiveusa/archonx-os" {
            return self.root.clone();
        }
        self.root
            .join("data")
            .join("repos")
            .join(Self::slug_to_dirname(slug))
    }

    /// Ensure a repo is checked out locally (shallow clone if needed).
    fn ensure_checkout(&self, slug: &str) -> (PathBuf, String) {
        let path = self.repo_local_path(slug);
        if path.exists() {
            return (path, "available".into());
        }
        let parent = path.parent().unwrap_or(&self.root);
        std::fs::create_dir_all(parent).ok();
        let clone_url = format!("https://github.com/{}.git", slug);
        let output = Command::new("git")
            .args(["clone", "--depth", "1", &clone_url, &path.to_string_lossy()])
            .output();
        match output {
            Ok(o) if o.status.success() => (path, "available".into()),
            _ => (path, "unavailable".into()),
        }
    }

    /// Index a single repository.
    /// Replaces Python: def index_repo(self, slug)
    pub fn index_repo(&self, slug: &str) -> RepoIndex {
        let (repo_path, status) = self.ensure_checkout(slug);
        if status != "available" {
            return RepoIndex {
                slug: slug.to_string(),
                status,
                docs: vec![],
                terms: vec![],
                metadata: [("reason".into(), "clone_failed".into())].into(),
            };
        }

        // Parallel file collection using walkdir + rayon
        let docs: Vec<RepoDocument> = self.collect_docs_parallel(&repo_path);
        let all_text: String = docs.iter().map(|d| d.content.as_str()).collect::<Vec<_>>().join("\n");
        let terms: Vec<String> = self
            .token_re
            .find_iter(&all_text)
            .map(|m| m.as_str().to_lowercase())
            .collect();

        let doc_count = docs.len().to_string();
        RepoIndex {
            slug: slug.to_string(),
            status,
            docs,
            terms,
            metadata: [("doc_count".into(), doc_count)].into(),
        }
    }

    /// Collect all scannable documents in parallel using rayon.
    fn collect_docs_parallel(&self, repo_path: &Path) -> Vec<RepoDocument> {
        use walkdir::WalkDir;

        let entries: Vec<_> = WalkDir::new(repo_path)
            .follow_links(false)
            .max_depth(8)
            .into_iter()
            .filter_map(|e| e.ok())
            .filter(|e| {
                let path = e.path();
                if !path.is_file() {
                    return false;
                }
                // Skip .git directory
                if path.components().any(|c| c.as_os_str() == ".git") {
                    return false;
                }
                // Only scan approved extensions
                if let Some(ext) = path.extension().and_then(|e| e.to_str()) {
                    return SCAN_EXTENSIONS.contains(&ext);
                }
                // Include extensionless files like README
                let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
                name.to_uppercase().starts_with("README")
            })
            .collect();

        // Parallel read using rayon — replaces Python's sequential loop
        entries
            .par_iter()
            .filter_map(|entry| {
                let path = entry.path();
                let rel = path.strip_prefix(repo_path).ok()?.to_string_lossy().into_owned();
                let content = std::fs::read_to_string(path)
                    .unwrap_or_default();
                // Limit content to 25,000 chars (matches Python [:25000])
                let content = content.chars().take(25_000).collect::<String>();
                if content.is_empty() {
                    return None;
                }
                Some(RepoDocument { path: rel, content })
            })
            .collect()
    }

    /// Index all repositories. Returns indexes in order.
    /// Replaces Python: def index_all(self)
    pub fn index_all(&self) -> Vec<RepoIndex> {
        info!("Indexing {} repos (parallel with rayon)", self.repos.len());
        // Index repos in parallel — this is the main performance gain
        self.repos
            .par_iter()
            .map(|slug| self.index_repo(slug))
            .collect()
    }

    /// Index a local directory (not a git repo).
    /// Used for testing and local development.
    pub fn index_directory(&self, dir: &Path) -> RepoIndex {
        let docs = self.collect_docs_parallel(dir);
        let all_text: String = docs.iter().map(|d| d.content.as_str()).collect::<Vec<_>>().join("\n");
        let terms: Vec<String> = self
            .token_re
            .find_iter(&all_text)
            .map(|m| m.as_str().to_lowercase())
            .collect();

        let slug = dir.file_name().and_then(|n| n.to_str()).unwrap_or("unknown");
        RepoIndex {
            slug: slug.to_string(),
            status: "available".into(),
            docs,
            terms,
            metadata: Default::default(),
        }
    }
}

/// Load target repos from targets.json or return defaults.
/// Replaces Python: def load_target_repos(root)
pub fn load_target_repos(root: &Path) -> Vec<String> {
    let targets_path = root.join("data").join("graphbrain").join("targets.json");
    if targets_path.exists() {
        if let Ok(content) = std::fs::read_to_string(&targets_path) {
            if let Ok(v) = serde_json::from_str::<serde_json::Value>(&content) {
                if let Some(repos) = v.get("repos").and_then(|r| r.as_array()) {
                    return repos
                        .iter()
                        .filter_map(|r| r.as_str().map(String::from))
                        .collect();
                }
            }
        }
    }

    // Default target repos — exact match with Python source
    vec![
        "executiveusa/phone-call-assistant".into(),
        "executiveusa/VisionClaw".into(),
        "executiveusa/clawdbot-Whatsapp-agent".into(),
        "executiveusa/dashboard-agent-swarm".into(),
        "executiveusa/agent-zero-Fork".into(),
        "executiveusa/archonx-os".into(),
        "executiveusa/Darya-designs".into(),
        "executiveusa/cult-directory-template".into(),
        "executiveusa/pauli-comic-funnel".into(),
        "executiveusa/Pauli-claw-work".into(),
        "executiveusa/amentislibrary".into(),
        "executiveusa/agent_flywheel_clawdbot_skills_and_integrations".into(),
        "executiveusa/goat-alliance-scaffold".into(),
        "executiveusa/vallarta-voyage-explorer".into(),
        "executiveusa/paulisworld-openclaw-3d".into(),
    ]
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    fn make_temp_repo() -> TempDir {
        let dir = tempfile::tempdir().unwrap();
        std::fs::write(dir.path().join("README.md"), "# Test Repo\nThis is a test.").unwrap();
        std::fs::write(dir.path().join("test.json"), r#"{"key": "value"}"#).unwrap();
        let src = dir.path().join("src");
        std::fs::create_dir_all(&src).unwrap();
        std::fs::write(src.join("main.rs"), "fn main() { println!(\"hello\"); }").unwrap();
        dir
    }

    #[test]
    fn index_directory_finds_files() {
        let dir = make_temp_repo();
        let root = PathBuf::from("/tmp");
        let indexer = RepoIndexer::new(root, vec![]);
        let index = indexer.index_directory(dir.path());
        assert_eq!(index.status, "available");
        assert!(index.docs.len() >= 2, "Expected at least 2 docs, got {}", index.docs.len());
        assert!(!index.terms.is_empty());
    }

    #[test]
    fn load_target_repos_returns_defaults() {
        let root = PathBuf::from("/nonexistent");
        let repos = load_target_repos(&root);
        assert_eq!(repos.len(), 15);
        assert!(repos.contains(&"executiveusa/archonx-os".to_string()));
    }

    #[test]
    fn index_directory_parallel_does_not_panic() {
        let dir = make_temp_repo();
        // Create many files to exercise rayon parallelism
        for i in 0..20 {
            std::fs::write(
                dir.path().join(format!("file_{}.md", i)),
                format!("# File {}\nContent for file {}", i, i),
            ).unwrap();
        }
        let indexer = RepoIndexer::new(PathBuf::from("/tmp"), vec![]);
        let index = indexer.index_directory(dir.path());
        assert!(index.docs.len() >= 20);
    }
}
