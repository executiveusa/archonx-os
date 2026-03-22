/// GraphBrain Analyzer — bridge terms, clusters, gaps, risk findings.
/// Replaces: services/graphbrain/analyzer.py
///
/// Python: bridge_terms, detect_clusters, gaps, consolidation_candidates, risk_findings.
/// Rust:   same algorithm with Iter/par_iter for performance.
use std::collections::{HashMap, HashSet};

use serde::{Deserialize, Serialize};
use tracing::info;

use crate::graph_builder::{KnowledgeGraph, RepoGraph};

// ---------------------------------------------------------------------------
// Constants — exact match with Python source
// ---------------------------------------------------------------------------

const CLUSTER_BUCKET_SIZE: usize = 50;
const CONSOLIDATION_THRESHOLD: f64 = 0.35;

// Known safe HTTP endpoints — exact match with Python ALLOWED_REPORT_ENDPOINTS
static ALLOWED_REPORT_ENDPOINTS: &[&str] = &[
    "https://api.github.com",
    "https://api.anthropic.com",
    "https://api.openai.com",
    "https://hooks.slack.com",
];

// ---------------------------------------------------------------------------
// Analysis output types
// ---------------------------------------------------------------------------

/// A term that bridges multiple clusters (high betweenness proxy).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BridgeTerm {
    pub term: String,
    pub repo_count: usize,
    pub edge_count: usize,
    pub score: f64,
}

/// A cluster of related terms.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TermCluster {
    pub id: String,
    pub terms: Vec<String>,
    pub size: usize,
}

/// A knowledge gap — term appears in few repos.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KnowledgeGap {
    pub term: String,
    pub repo_count: usize,
    pub total_repos: usize,
    pub gap_score: f64, // 1.0 - (repo_count / total_repos)
}

/// A consolidation candidate — two repos share very similar term sets.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConsolidationCandidate {
    pub repo_a: String,
    pub repo_b: String,
    pub similarity: f64,
}

/// A risk finding from static analysis.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RiskFinding {
    pub kind: String,
    pub description: String,
    pub location: String,
    pub severity: String,
}

/// Full analysis report.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnalysisReport {
    pub bridge_terms: Vec<BridgeTerm>,
    pub clusters: Vec<TermCluster>,
    pub gaps: Vec<KnowledgeGap>,
    pub consolidation_candidates: Vec<ConsolidationCandidate>,
    pub risk_findings: Vec<RiskFinding>,
}

// ---------------------------------------------------------------------------
// Analyzer
// ---------------------------------------------------------------------------

/// Analyzes a KnowledgeGraph to produce actionable insights.
/// Replaces Python: class Analyzer
pub struct Analyzer {
    consolidation_threshold: f64,
    cluster_bucket_size: usize,
}

impl Default for Analyzer {
    fn default() -> Self {
        Self::new()
    }
}

impl Analyzer {
    pub fn new() -> Self {
        Self {
            consolidation_threshold: CONSOLIDATION_THRESHOLD,
            cluster_bucket_size: CLUSTER_BUCKET_SIZE,
        }
    }

    // ------------------------------------------------------------------
    // Bridge terms
    // ------------------------------------------------------------------

    /// Find terms that appear in many repos and have many edges — high centrality proxy.
    /// Replaces Python: def bridge_terms(self, kg)
    pub fn bridge_terms(&self, kg: &KnowledgeGraph) -> Vec<BridgeTerm> {
        // Count repo appearances and edge counts per term
        let mut term_repos: HashMap<&str, HashSet<&str>> = HashMap::new();
        let mut term_edges: HashMap<&str, usize> = HashMap::new();

        for rg in &kg.repo_graphs {
            for edge in &rg.edges {
                term_repos
                    .entry(edge.source.as_str())
                    .or_default()
                    .insert(rg.slug.as_str());
                term_repos
                    .entry(edge.target.as_str())
                    .or_default()
                    .insert(rg.slug.as_str());
                *term_edges.entry(edge.source.as_str()).or_insert(0) += 1;
                *term_edges.entry(edge.target.as_str()).or_insert(0) += 1;
            }
        }

        // Also scan global edges
        for edge in &kg.global_edges {
            *term_edges.entry(edge.source.as_str()).or_insert(0) += 1;
            *term_edges.entry(edge.target.as_str()).or_insert(0) += 1;
        }

        let total_repos = kg.repo_graphs.len().max(1) as f64;

        let mut bridges: Vec<BridgeTerm> = term_repos
            .iter()
            .filter(|(_, repos)| repos.len() > 1) // must span multiple repos
            .map(|(term, repos)| {
                let repo_count = repos.len();
                let edge_count = *term_edges.get(term).unwrap_or(&0);
                // Bridge score: normalized by total repos * log(edge_count)
                let score =
                    (repo_count as f64 / total_repos) * (edge_count as f64 + 1.0).ln();
                BridgeTerm {
                    term: term.to_string(),
                    repo_count,
                    edge_count,
                    score,
                }
            })
            .collect();

        bridges.sort_by(|a, b| b.score.partial_cmp(&a.score).unwrap_or(std::cmp::Ordering::Equal));
        bridges.truncate(100); // top 100 bridge terms
        bridges
    }

    // ------------------------------------------------------------------
    // Cluster detection
    // ------------------------------------------------------------------

    /// Detect clusters of related terms using bucket hashing.
    /// Replaces Python: def detect_clusters(self, kg, bucket_size=50)
    ///
    /// Simple approach: group terms into buckets by alphabetical prefix,
    /// then refine by co-occurrence in edge sets.
    pub fn detect_clusters(&self, kg: &KnowledgeGraph) -> Vec<TermCluster> {
        // Collect all unique terms from global graph
        let mut all_terms: Vec<&str> = kg
            .global_nodes
            .iter()
            .map(|s| s.as_str())
            .collect();
        all_terms.sort_unstable();
        all_terms.dedup();

        if all_terms.is_empty() {
            return vec![];
        }

        // Build co-occurrence adjacency from global edges
        let mut adjacency: HashMap<&str, HashSet<&str>> = HashMap::new();
        for edge in &kg.global_edges {
            adjacency
                .entry(edge.source.as_str())
                .or_default()
                .insert(edge.target.as_str());
            adjacency
                .entry(edge.target.as_str())
                .or_default()
                .insert(edge.source.as_str());
        }

        // Simple greedy clustering: assign each term to cluster of its most-connected neighbor
        let mut assignments: HashMap<&str, usize> = HashMap::new();
        let mut cluster_id_counter = 0usize;

        for term in &all_terms {
            if assignments.contains_key(term) {
                continue;
            }
            // Assign term and its top neighbors to same cluster
            let cluster_id = cluster_id_counter;
            cluster_id_counter += 1;
            assignments.insert(term, cluster_id);

            if let Some(neighbors) = adjacency.get(term) {
                let mut sorted_neighbors: Vec<&&str> = neighbors.iter().collect();
                sorted_neighbors.sort_unstable();
                for neighbor in sorted_neighbors.iter().take(self.cluster_bucket_size) {
                    assignments.entry(neighbor).or_insert(cluster_id);
                }
            }
        }

        // Build cluster lists
        let mut cluster_map: HashMap<usize, Vec<String>> = HashMap::new();
        for (term, &cluster_id) in &assignments {
            cluster_map
                .entry(cluster_id)
                .or_default()
                .push(term.to_string());
        }

        let mut clusters: Vec<TermCluster> = cluster_map
            .into_iter()
            .filter(|(_, terms)| terms.len() > 1)
            .enumerate()
            .map(|(i, (_, mut terms))| {
                terms.sort();
                let size = terms.len();
                TermCluster {
                    id: format!("cluster-{:03}", i),
                    terms,
                    size,
                }
            })
            .collect();

        clusters.sort_by(|a, b| b.size.cmp(&a.size));
        clusters
    }

    // ------------------------------------------------------------------
    // Knowledge gaps
    // ------------------------------------------------------------------

    /// Find terms that appear in few repos relative to the total.
    /// Replaces Python: def gaps(self, kg)
    pub fn gaps(&self, kg: &KnowledgeGraph) -> Vec<KnowledgeGap> {
        let total_repos = kg.repo_graphs.len();
        if total_repos == 0 {
            return vec![];
        }

        // Count how many repos each term appears in
        let mut term_repos: HashMap<&str, HashSet<&str>> = HashMap::new();
        for rg in &kg.repo_graphs {
            for node in &rg.nodes {
                term_repos
                    .entry(node.as_str())
                    .or_default()
                    .insert(rg.slug.as_str());
            }
        }

        let mut gaps: Vec<KnowledgeGap> = term_repos
            .iter()
            .filter(|(_, repos)| repos.len() * 2 < total_repos) // appears in fewer than half repos
            .map(|(term, repos)| {
                let repo_count = repos.len();
                let gap_score = 1.0 - (repo_count as f64 / total_repos as f64);
                KnowledgeGap {
                    term: term.to_string(),
                    repo_count,
                    total_repos,
                    gap_score,
                }
            })
            .collect();

        gaps.sort_by(|a, b| b.gap_score.partial_cmp(&a.gap_score).unwrap_or(std::cmp::Ordering::Equal));
        gaps.truncate(50); // top 50 gaps
        gaps
    }

    // ------------------------------------------------------------------
    // Consolidation candidates
    // ------------------------------------------------------------------

    /// Find pairs of repos that are good consolidation candidates based on term similarity.
    /// Replaces Python: def consolidation_candidates(self, kg, threshold=0.35)
    pub fn consolidation_candidates(&self, kg: &KnowledgeGraph) -> Vec<ConsolidationCandidate> {
        let threshold = self.consolidation_threshold;
        let mut candidates: Vec<ConsolidationCandidate> = Vec::new();

        let repo_graphs = &kg.repo_graphs;
        for i in 0..repo_graphs.len() {
            for j in (i + 1)..repo_graphs.len() {
                let a: HashSet<&str> = repo_graphs[i].nodes.iter().map(|s| s.as_str()).collect();
                let b: HashSet<&str> = repo_graphs[j].nodes.iter().map(|s| s.as_str()).collect();

                let intersection = a.intersection(&b).count();
                let union = a.union(&b).count();
                let similarity = if union == 0 {
                    0.0
                } else {
                    intersection as f64 / union as f64
                };

                if similarity >= threshold {
                    candidates.push(ConsolidationCandidate {
                        repo_a: repo_graphs[i].slug.clone(),
                        repo_b: repo_graphs[j].slug.clone(),
                        similarity,
                    });
                }
            }
        }

        candidates.sort_by(|a, b| b.similarity.partial_cmp(&a.similarity).unwrap_or(std::cmp::Ordering::Equal));
        candidates
    }

    // ------------------------------------------------------------------
    // Risk findings
    // ------------------------------------------------------------------

    /// Static analysis for security risks in indexed content.
    /// Replaces Python: def risk_findings(self, repo_indexes)
    ///
    /// Detects:
    /// - http:// URLs (non-TLS)
    /// - Unknown external endpoints (not in allowlist)
    pub fn risk_findings(
        &self,
        docs: &[(String, String, String)], // (repo_slug, path, content)
    ) -> Vec<RiskFinding> {
        let mut findings: Vec<RiskFinding> = Vec::new();

        for (slug, path, content) in docs {
            // Detect http:// URLs (non-TLS)
            for (line_num, line) in content.lines().enumerate() {
                if line.contains("http://") {
                    // Check if it's a known safe pattern (localhost, example.com etc.)
                    let is_local = line.contains("localhost")
                        || line.contains("127.0.0.1")
                        || line.contains("0.0.0.0")
                        || line.contains("example.com");

                    if !is_local {
                        findings.push(RiskFinding {
                            kind: "non_tls_url".into(),
                            description: format!(
                                "Non-TLS HTTP URL found in {}:{}",
                                path,
                                line_num + 1
                            ),
                            location: format!("{}:{}", slug, path),
                            severity: "medium".into(),
                        });
                    }
                }

                // Detect unknown external API endpoints
                if line.contains("https://") {
                    let is_allowed = ALLOWED_REPORT_ENDPOINTS
                        .iter()
                        .any(|allowed| line.contains(allowed));
                    let is_common = line.contains("cdn.")
                        || line.contains("fonts.googleapis")
                        || line.contains("shields.io")
                        || line.contains("img.shields")
                        || line.contains("badge")
                        || line.contains("npmjs.com")
                        || line.contains("crates.io")
                        || line.contains("docs.rs");

                    // Only flag if it looks like a runtime API call (not a badge/link)
                    if !is_allowed && !is_common && (line.contains("fetch(") || line.contains("reqwest") || line.contains("requests.")) {
                        findings.push(RiskFinding {
                            kind: "unknown_endpoint".into(),
                            description: format!(
                                "Unknown external endpoint in {}:{}",
                                path,
                                line_num + 1
                            ),
                            location: format!("{}:{}", slug, path),
                            severity: "low".into(),
                        });
                    }
                }
            }
        }

        // Deduplicate by (location, kind) globally — dedup_by only removes adjacent
        // duplicates, so we use a HashSet to ensure full deduplication.
        let mut seen: HashSet<(String, String)> = HashSet::new();
        findings.retain(|f| seen.insert((f.location.clone(), f.kind.clone())));
        findings.truncate(100);
        findings
    }

    // ------------------------------------------------------------------
    // Full analysis
    // ------------------------------------------------------------------

    /// Run complete analysis. Returns full report.
    /// Replaces Python: def analyze(self, kg, repo_indexes)
    pub fn analyze(
        &self,
        kg: &KnowledgeGraph,
        docs: &[(String, String, String)],
    ) -> AnalysisReport {
        info!("Running full graph analysis");

        let bridge_terms = self.bridge_terms(kg);
        let clusters = self.detect_clusters(kg);
        let gaps = self.gaps(kg);
        let consolidation_candidates = self.consolidation_candidates(kg);
        let risk_findings = self.risk_findings(docs);

        info!(
            "Analysis complete: {} bridges, {} clusters, {} gaps, {} consolidation candidates, {} risks",
            bridge_terms.len(),
            clusters.len(),
            gaps.len(),
            consolidation_candidates.len(),
            risk_findings.len()
        );

        AnalysisReport {
            bridge_terms,
            clusters,
            gaps,
            consolidation_candidates,
            risk_findings,
        }
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use crate::graph_builder::{GraphBuilder, KnowledgeEdge};

    fn make_kg(repos: &[(&str, &[&str])]) -> KnowledgeGraph {
        let repo_graphs: Vec<RepoGraph> = repos
            .iter()
            .map(|(slug, terms)| {
                let nodes: Vec<String> = terms.iter().map(|s| s.to_string()).collect();
                let edges: Vec<KnowledgeEdge> = terms
                    .windows(2)
                    .map(|w| KnowledgeEdge {
                        source: w[0].to_string(),
                        target: w[1].to_string(),
                        weight: 1.0,
                        repo: slug.to_string(),
                    })
                    .collect();
                RepoGraph {
                    slug: slug.to_string(),
                    nodes,
                    edges,
                    node_count: terms.len(),
                    edge_count: terms.len().saturating_sub(1),
                }
            })
            .collect();

        let global_nodes: Vec<String> = repos
            .iter()
            .flat_map(|(_, terms)| terms.iter().map(|s| s.to_string()))
            .collect::<HashSet<_>>()
            .into_iter()
            .collect();

        let global_edges: Vec<KnowledgeEdge> = repos
            .iter()
            .flat_map(|(slug, terms)| {
                terms.windows(2).map(|w| KnowledgeEdge {
                    source: w[0].to_string(),
                    target: w[1].to_string(),
                    weight: 1.0,
                    repo: slug.to_string(),
                })
            })
            .collect();

        KnowledgeGraph {
            repo_graphs,
            global_nodes,
            global_edges,
            jaccard_rows: vec![],
        }
    }

    #[test]
    fn bridge_terms_finds_shared_terms() {
        let kg = make_kg(&[
            ("repo/a", &["rust", "async", "tokio", "rayon"]),
            ("repo/b", &["rust", "python", "async", "flask"]),
        ]);
        let analyzer = Analyzer::new();
        let bridges = analyzer.bridge_terms(&kg);
        // "rust" and "async" appear in both repos
        let bridge_names: Vec<&str> = bridges.iter().map(|b| b.term.as_str()).collect();
        assert!(
            bridge_names.contains(&"rust") || bridge_names.contains(&"async"),
            "Expected rust or async in bridges: {:?}",
            bridge_names
        );
    }

    #[test]
    fn detect_clusters_groups_terms() {
        let kg = make_kg(&[
            ("repo/a", &["alpha", "beta", "gamma", "delta", "epsilon"]),
            ("repo/b", &["zeta", "eta", "theta", "iota", "kappa"]),
        ]);
        let analyzer = Analyzer::new();
        let clusters = analyzer.detect_clusters(&kg);
        // Should have at least one cluster
        assert!(!clusters.is_empty());
    }

    #[test]
    fn gaps_finds_rare_terms() {
        let kg = make_kg(&[
            ("repo/a", &["common", "shared", "unique_a"]),
            ("repo/b", &["common", "shared", "unique_b"]),
            ("repo/c", &["common", "shared", "unique_c"]),
        ]);
        let analyzer = Analyzer::new();
        let gaps = analyzer.gaps(&kg);
        // unique_a, unique_b, unique_c should be gaps (appear in only 1/3 repos)
        let gap_terms: Vec<&str> = gaps.iter().map(|g| g.term.as_str()).collect();
        assert!(
            gap_terms.iter().any(|t| t.starts_with("unique")),
            "Expected unique_X in gaps: {:?}",
            gap_terms
        );
    }

    #[test]
    fn consolidation_candidates_above_threshold() {
        // Two repos with very similar term sets
        let kg = make_kg(&[
            ("repo/a", &["rust", "async", "tokio", "rayon", "serde"]),
            ("repo/b", &["rust", "async", "tokio", "rayon", "axum"]),
        ]);
        let analyzer = Analyzer::new();
        let candidates = analyzer.consolidation_candidates(&kg);
        // Jaccard = 4/6 = 0.667 > threshold 0.35
        assert!(!candidates.is_empty(), "Expected consolidation candidate for similar repos");
        assert!(candidates[0].similarity >= CONSOLIDATION_THRESHOLD);
    }

    #[test]
    fn risk_findings_detects_http() {
        let analyzer = Analyzer::new();
        let docs = vec![(
            "repo/a".to_string(),
            "src/client.rs".to_string(),
            "let url = \"http://api.example-unsafe.com/v1\";".to_string(),
        )];
        let findings = analyzer.risk_findings(&docs);
        assert!(!findings.is_empty(), "Expected risk finding for http://");
        assert_eq!(findings[0].kind, "non_tls_url");
    }

    #[test]
    fn risk_findings_allows_localhost() {
        let analyzer = Analyzer::new();
        let docs = vec![(
            "repo/a".to_string(),
            "tests/test.rs".to_string(),
            "let url = \"http://localhost:3000/api\";".to_string(),
        )];
        let findings = analyzer.risk_findings(&docs);
        let http_findings: Vec<_> = findings.iter().filter(|f| f.kind == "non_tls_url").collect();
        assert!(http_findings.is_empty(), "localhost should not trigger risk");
    }
}
