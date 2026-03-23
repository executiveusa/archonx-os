/// GraphBrain Graph Builder — petgraph knowledge graph with co-occurrence edges.
/// Replaces: services/graphbrain/graph_builder.py
///
/// Python: sliding window co-occurrence, top 4000/6000 edges, Jaccard similarity.
/// Rust:   same algorithm, rayon parallel edge construction.
use std::collections::HashMap;

use petgraph::graph::{Graph, NodeIndex, UnGraph};
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use tracing::info;

use crate::repo_indexer::{RepoDocument, RepoIndex};

// ---------------------------------------------------------------------------
// Constants — exact match with Python source
// ---------------------------------------------------------------------------

const MAX_EDGES_PER_REPO: usize = 4_000;
const MAX_EDGES_GLOBAL: usize = 6_000;
const WINDOW_SIZE: usize = 5; // sliding window for co-occurrence

// ---------------------------------------------------------------------------
// Data types
// ---------------------------------------------------------------------------

/// A single edge in the knowledge graph.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KnowledgeEdge {
    pub source: String,
    pub target: String,
    pub weight: f64,
    pub repo: String,
}

/// Per-repo knowledge graph snapshot.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RepoGraph {
    pub slug: String,
    pub nodes: Vec<String>,
    pub edges: Vec<KnowledgeEdge>,
    pub node_count: usize,
    pub edge_count: usize,
}

/// Full multi-repo knowledge graph.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KnowledgeGraph {
    pub repo_graphs: Vec<RepoGraph>,
    pub global_nodes: Vec<String>,
    pub global_edges: Vec<KnowledgeEdge>,
    pub jaccard_rows: Vec<JaccardRow>,
}

/// One row of Jaccard similarity between two terms.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JaccardRow {
    pub term_a: String,
    pub term_b: String,
    pub similarity: f64,
}

// ---------------------------------------------------------------------------
// GraphBuilder
// ---------------------------------------------------------------------------

/// Builds a knowledge graph from indexed repositories.
/// Replaces Python: class GraphBuilder
pub struct GraphBuilder {
    max_edges_per_repo: usize,
    max_edges_global: usize,
    window_size: usize,
}

impl Default for GraphBuilder {
    fn default() -> Self {
        Self::new()
    }
}

impl GraphBuilder {
    pub fn new() -> Self {
        Self {
            max_edges_per_repo: MAX_EDGES_PER_REPO,
            max_edges_global: MAX_EDGES_GLOBAL,
            window_size: WINDOW_SIZE,
        }
    }

    // ------------------------------------------------------------------
    // Token extraction helpers
    // ------------------------------------------------------------------

    /// Tokenize a string into lowercase words (matches Python TOKEN_RE behavior).
    fn tokenize(text: &str) -> Vec<String> {
        // Simple word tokenizer — split on non-alphanumeric, filter short tokens
        text.split(|c: char| !c.is_alphanumeric() && c != '_' && c != '-')
            .filter(|s| s.len() >= 3)
            .map(|s| s.to_lowercase())
            .collect()
    }

    // ------------------------------------------------------------------
    // Co-occurrence edge building
    // ------------------------------------------------------------------

    /// Build co-occurrence edges from a list of tokens using sliding window.
    /// Replaces Python: sliding window loop in graph_builder.py
    ///
    /// For each pair (i, j) where j > i and j - i <= window_size:
    ///   weight = 1.0 / (j - i)
    fn build_cooccurrence_edges(
        tokens: &[String],
        slug: &str,
        max_edges: usize,
        window_size: usize,
    ) -> Vec<KnowledgeEdge> {
        // Count weights for each (source, target) pair
        let mut edge_weights: HashMap<(String, String), f64> = HashMap::new();

        for (i, term_a) in tokens.iter().enumerate() {
            let end = (i + window_size + 1).min(tokens.len());
            for (j, term_b) in tokens[i + 1..end].iter().enumerate() {
                if term_a == term_b {
                    continue;
                }
                // Canonical ordering to deduplicate (a,b) and (b,a)
                let (a, b) = if term_a < term_b {
                    (term_a.clone(), term_b.clone())
                } else {
                    (term_b.clone(), term_a.clone())
                };
                let weight = 1.0 / (j as f64 + 1.0);
                *edge_weights.entry((a, b)).or_insert(0.0) += weight;
            }
        }

        // Sort by weight descending, take top max_edges
        let mut edges: Vec<KnowledgeEdge> = edge_weights
            .into_iter()
            .map(|((source, target), weight)| KnowledgeEdge {
                source,
                target,
                weight,
                repo: slug.to_string(),
            })
            .collect();

        edges.sort_by(|a, b| b.weight.partial_cmp(&a.weight).unwrap_or(std::cmp::Ordering::Equal));
        edges.truncate(max_edges);
        edges
    }

    // ------------------------------------------------------------------
    // Repo graph building
    // ------------------------------------------------------------------

    /// Build a knowledge graph for a single repo.
    /// Replaces Python: def build_repo_graph(self, repo_index)
    pub fn build_repo_graph(&self, repo_index: &RepoIndex) -> RepoGraph {
        let all_tokens: Vec<String> = repo_index
            .docs
            .iter()
            .flat_map(|doc| Self::tokenize(&doc.content))
            .collect();

        let edges = Self::build_cooccurrence_edges(&all_tokens, &repo_index.slug, self.max_edges_per_repo, self.window_size);

        let nodes: Vec<String> = {
            let mut seen = std::collections::HashSet::new();
            let mut nodes = Vec::new();
            for e in &edges {
                if seen.insert(e.source.clone()) {
                    nodes.push(e.source.clone());
                }
                if seen.insert(e.target.clone()) {
                    nodes.push(e.target.clone());
                }
            }
            nodes
        };

        let node_count = nodes.len();
        let edge_count = edges.len();

        RepoGraph {
            slug: repo_index.slug.clone(),
            nodes,
            edges,
            node_count,
            edge_count,
        }
    }

    // ------------------------------------------------------------------
    // Multi-repo global graph
    // ------------------------------------------------------------------

    /// Build global knowledge graph from all repos in parallel.
    /// Replaces Python: def build_global_graph(self, all_indexes)
    pub fn build_global_graph(&self, all_indexes: &[RepoIndex]) -> KnowledgeGraph {
        info!("Building knowledge graphs for {} repos (parallel)", all_indexes.len());

        // Build per-repo graphs in parallel with rayon
        let repo_graphs: Vec<RepoGraph> = all_indexes
            .par_iter()
            .map(|idx| self.build_repo_graph(idx))
            .collect();

        // Merge all tokens for global graph
        let all_tokens: Vec<String> = all_indexes
            .par_iter()
            .flat_map_iter(|idx| idx.docs.iter().flat_map(|doc| Self::tokenize(&doc.content)))
            .collect();

        let global_edges =
            Self::build_cooccurrence_edges(&all_tokens, "global", self.max_edges_global, self.window_size);

        let global_nodes: Vec<String> = {
            let mut seen = std::collections::HashSet::new();
            let mut nodes = Vec::new();
            for e in &global_edges {
                if seen.insert(e.source.clone()) {
                    nodes.push(e.source.clone());
                }
                if seen.insert(e.target.clone()) {
                    nodes.push(e.target.clone());
                }
            }
            nodes
        };

        // Compute Jaccard similarity rows for top-N term pairs
        let jaccard_rows = self.compute_jaccard(&repo_graphs);

        KnowledgeGraph {
            repo_graphs,
            global_nodes,
            global_edges,
            jaccard_rows,
        }
    }

    // ------------------------------------------------------------------
    // Jaccard similarity
    // ------------------------------------------------------------------

    /// Compute Jaccard similarity between repos based on shared terms.
    /// Replaces Python: def jaccard_similarity(self, set_a, set_b)
    ///
    /// For each pair of repo graphs, computes |intersection| / |union| of nodes.
    pub fn compute_jaccard(&self, repo_graphs: &[RepoGraph]) -> Vec<JaccardRow> {
        let mut rows: Vec<JaccardRow> = Vec::new();

        for i in 0..repo_graphs.len() {
            for j in (i + 1)..repo_graphs.len() {
                let a: std::collections::HashSet<&str> =
                    repo_graphs[i].nodes.iter().map(|s| s.as_str()).collect();
                let b: std::collections::HashSet<&str> =
                    repo_graphs[j].nodes.iter().map(|s| s.as_str()).collect();

                let intersection = a.intersection(&b).count();
                let union = a.union(&b).count();
                let similarity = if union == 0 {
                    0.0
                } else {
                    intersection as f64 / union as f64
                };

                // Only include non-trivial similarities
                if similarity > 0.0 {
                    rows.push(JaccardRow {
                        term_a: repo_graphs[i].slug.clone(),
                        term_b: repo_graphs[j].slug.clone(),
                        similarity,
                    });
                }
            }
        }

        // Sort by similarity descending
        rows.sort_by(|a, b| b.similarity.partial_cmp(&a.similarity).unwrap_or(std::cmp::Ordering::Equal));
        rows
    }

    // ------------------------------------------------------------------
    // petgraph conversion (for graph algorithms)
    // ------------------------------------------------------------------

    /// Convert a RepoGraph to a petgraph UnGraph for algorithmic analysis.
    pub fn to_petgraph(repo_graph: &RepoGraph) -> (UnGraph<String, f64>, HashMap<String, NodeIndex>) {
        let mut g: UnGraph<String, f64> = Graph::new_undirected();
        let mut node_map: HashMap<String, NodeIndex> = HashMap::new();

        for node in &repo_graph.nodes {
            let idx = g.add_node(node.clone());
            node_map.insert(node.clone(), idx);
        }

        for edge in &repo_graph.edges {
            if let (Some(&src), Some(&dst)) = (node_map.get(&edge.source), node_map.get(&edge.target)) {
                g.add_edge(src, dst, edge.weight);
            }
        }

        (g, node_map)
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use crate::repo_indexer::RepoDocument;

    fn make_index(slug: &str, content: &str) -> RepoIndex {
        RepoIndex {
            slug: slug.to_string(),
            status: "available".into(),
            docs: vec![RepoDocument {
                path: "README.md".into(),
                content: content.to_string(),
            }],
            terms: vec![],
            metadata: Default::default(),
        }
    }

    #[test]
    fn tokenize_basic() {
        let tokens = GraphBuilder::tokenize("Hello world foo bar");
        assert!(tokens.contains(&"hello".to_string()));
        assert!(tokens.contains(&"world".to_string()));
        // "foo" and "bar" length < 3 skipped? No, they're exactly 3
        assert!(tokens.contains(&"foo".to_string()));
    }

    #[test]
    fn build_repo_graph_has_edges() {
        let builder = GraphBuilder::new();
        let content = "rust async tokio rayon serde tokio rayon serde rust tokio";
        let idx = make_index("test/repo", content);
        let graph = builder.build_repo_graph(&idx);
        assert!(!graph.edges.is_empty());
        assert!(!graph.nodes.is_empty());
    }

    #[test]
    fn edges_respect_max_limit() {
        let builder = GraphBuilder::new();
        // Generate a large content with many unique pairs
        let words: Vec<String> = (0..200).map(|i| format!("word{:03}", i)).collect();
        let content = words.join(" ");
        let idx = make_index("test/big", &content);
        let graph = builder.build_repo_graph(&idx);
        assert!(
            graph.edge_count <= MAX_EDGES_PER_REPO,
            "edge_count {} exceeds max {}",
            graph.edge_count,
            MAX_EDGES_PER_REPO
        );
    }

    #[test]
    fn build_global_graph_merges_repos() {
        let builder = GraphBuilder::new();
        let idx1 = make_index("repo/a", "rust async tokio rayon parallel");
        let idx2 = make_index("repo/b", "rust python async performance speed");
        let kg = builder.build_global_graph(&[idx1, idx2]);
        assert_eq!(kg.repo_graphs.len(), 2);
        assert!(!kg.global_edges.is_empty());
        assert!(!kg.global_nodes.is_empty());
    }

    #[test]
    fn jaccard_similarity_computed() {
        let builder = GraphBuilder::new();
        let idx1 = make_index("repo/a", "rust async tokio rayon parallel serde uuid chrono");
        let idx2 = make_index("repo/b", "rust python async performance speed serde json");
        let kg = builder.build_global_graph(&[idx1, idx2]);
        // Should have at least one Jaccard row since repos share terms
        assert!(!kg.jaccard_rows.is_empty());
        let row = &kg.jaccard_rows[0];
        assert!(row.similarity > 0.0 && row.similarity <= 1.0);
    }

    #[test]
    fn to_petgraph_converts_correctly() {
        let builder = GraphBuilder::new();
        let idx = make_index("test/repo", "rust async tokio rayon serde tokio rayon rust");
        let repo_graph = builder.build_repo_graph(&idx);
        let (g, node_map) = GraphBuilder::to_petgraph(&repo_graph);
        assert_eq!(g.node_count(), node_map.len());
        assert!(g.edge_count() > 0);
    }

    #[test]
    fn cooccurrence_weight_decreases_with_distance() {
        // Tokens: a _ _ _ b (distance 4) and a _ b (distance 2)
        // Weights should be higher for closer pairs
        let tokens: Vec<String> = vec![
            "alpha".into(), "mid1".into(), "beta".into(), // alpha-beta distance 2 -> 0.5
            "alpha".into(), "mid2".into(), "mid3".into(), "mid4".into(), "gamma".into(), // alpha-gamma distance 5 -> 0.2
        ];
        let edges = GraphBuilder::build_cooccurrence_edges(&tokens, "test", 1000, WINDOW_SIZE);
        let ab = edges.iter().find(|e| {
            (e.source == "alpha" && e.target == "beta")
                || (e.source == "beta" && e.target == "alpha")
        });
        let ag = edges.iter().find(|e| {
            (e.source == "alpha" && e.target == "gamma")
                || (e.source == "gamma" && e.target == "alpha")
        });
        if let (Some(ab), Some(ag)) = (ab, ag) {
            assert!(ab.weight > ag.weight, "closer pair should have higher weight");
        }
    }
}
