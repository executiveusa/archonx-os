/// GraphBrain Runtime — Ralphy 7-phase loop.
/// Replaces: services/graphbrain/runtime.py
///
/// Python: GraphBrainRuntime with plan→implement→test→evaluate→patch→repeat→ship
/// Rust:   async orchestration with reqwest for report delivery, same 7 phases.
use std::path::PathBuf;
use std::time::Duration;

use reqwest::Client;
use serde::{Deserialize, Serialize};
use tracing::{error, info, warn};

use crate::analyzer::Analyzer;
use crate::graph_builder::GraphBuilder;
use crate::repo_indexer::{RepoIndexer, load_target_repos};
use crate::work_orders::{WorkOrder, generate_work_orders};

// ---------------------------------------------------------------------------
// Constants — exact match with Python source
// ---------------------------------------------------------------------------

/// Allowed endpoints for report delivery — matches Python ALLOWED_REPORT_ENDPOINTS.
static ALLOWED_REPORT_ENDPOINTS: &[&str] = &[
    "https://api.github.com",
    "https://api.anthropic.com",
    "https://api.openai.com",
    "https://hooks.slack.com",
];

const MAX_RETRIES: u32 = 3;
const RETRY_DELAY_SECS: u64 = 5;

// ---------------------------------------------------------------------------
// Run modes — matches Python --mode argument
// ---------------------------------------------------------------------------

/// Run mode: light for 15-minute cron, full for 8-hour cron.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum RunMode {
    Light,
    Full,
}

impl std::fmt::Display for RunMode {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            RunMode::Light => write!(f, "light"),
            RunMode::Full => write!(f, "full"),
        }
    }
}

impl std::str::FromStr for RunMode {
    type Err = String;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "light" => Ok(RunMode::Light),
            "full" => Ok(RunMode::Full),
            _ => Err(format!("Unknown mode: {}", s)),
        }
    }
}

// ---------------------------------------------------------------------------
// Report
// ---------------------------------------------------------------------------

/// The full GraphBrain report produced by one run.
/// Complies with ecosystem/contracts/graphbrain-report.schema.json.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GraphBrainReport {
    // Contract-required fields
    pub report_id: String,        // e.g. "graphbrain.graph_snapshot.v1.<ts>"
    pub generated_at: String,     // RFC3339 datetime
    pub repos_indexed: usize,
    pub graph: GraphSummary,
    pub recommendations: Vec<serde_json::Value>,
    // Existing fields
    pub mode: String,
    pub timestamp_ms: i64,
    pub docs_indexed: usize,
    pub work_orders: Vec<WorkOrder>,
    pub phases_completed: Vec<String>,
    pub metadata: serde_json::Value,
}

/// Nested graph summary for the contract schema.
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct GraphSummary {
    pub nodes: usize,
    pub edges: usize,
    pub clusters: usize,
    pub bridge_terms_top: Vec<serde_json::Value>,
}

// ---------------------------------------------------------------------------
// Phase results — internal to runtime
// ---------------------------------------------------------------------------

#[derive(Debug)]
struct PhaseResult {
    name: String,
    success: bool,
    details: String,
}

impl PhaseResult {
    fn ok(name: &str, details: &str) -> Self {
        Self { name: name.to_string(), success: true, details: details.to_string() }
    }
    fn fail(name: &str, details: &str) -> Self {
        Self { name: name.to_string(), success: false, details: details.to_string() }
    }
}

// ---------------------------------------------------------------------------
// GraphBrainRuntime
// ---------------------------------------------------------------------------

/// Main runtime for GraphBrain — the Ralphy 7-phase loop.
/// Replaces Python: class GraphBrainRuntime
pub struct GraphBrainRuntime {
    root: PathBuf,
    mode: RunMode,
    report_path: PathBuf,
    http: Client,
}

impl GraphBrainRuntime {
    pub fn new(root: PathBuf, mode: RunMode) -> Self {
        let report_path = root
            .join("data")
            .join("reports")
            .join("graphbrain_latest.json");
        Self {
            root,
            mode,
            report_path,
            http: Client::builder()
                .timeout(Duration::from_secs(30))
                .build()
                .expect("Failed to build HTTP client"),
        }
    }

    // ------------------------------------------------------------------
    // 7-phase Ralphy loop
    // ------------------------------------------------------------------

    /// Execute the full 7-phase run. Returns the final report.
    /// Replaces Python: async def run(self)
    pub async fn run(&self) -> GraphBrainReport {
        info!("GraphBrain runtime starting (mode={})", self.mode);

        let mut phases: Vec<PhaseResult> = Vec::new();
        let start_ms = chrono::Utc::now().timestamp_millis();

        // Phase 1: Plan — load target repos
        let repos = self.phase_plan(&mut phases);

        // Phase 2: Implement — index repos
        let (repo_indexes, total_docs) = self.phase_implement(&repos, &mut phases).await;

        // Phase 3: Test — validate indexes
        self.phase_test(&repo_indexes, &mut phases);

        // Phase 4: Evaluate — build knowledge graph
        let kg = self.phase_evaluate(&repo_indexes, &mut phases);

        // Phase 5: Patch — analyze and generate work orders
        let work_orders = self.phase_patch(&kg, &repo_indexes, &mut phases);

        // Phase 6: Repeat — build report and save to disk
        let now_dt = chrono::Utc::now();
        let bridge_terms_top: Vec<serde_json::Value> = kg.jaccard_rows.iter().take(5).map(|r| serde_json::json!({
            "term": format!("{} <-> {}", r.term_a, r.term_b),
            "betweenness": r.similarity,
        })).collect();

        let mut report = GraphBrainReport {
            report_id: format!("graphbrain.graph_snapshot.v1.{}", start_ms),
            generated_at: now_dt.to_rfc3339(),
            mode: self.mode.to_string(),
            timestamp_ms: start_ms,
            repos_indexed: repo_indexes.len(),
            docs_indexed: total_docs,
            graph: GraphSummary {
                nodes: kg.global_nodes.len(),
                edges: kg.global_edges.len(),
                clusters: kg.repo_graphs.len(),
                bridge_terms_top,
            },
            recommendations: work_orders.iter()
                .map(|w| serde_json::to_value(w).unwrap_or_default())
                .collect(),
            work_orders,
            // phases_completed set below — after phase_repeat and phase_ship execute
            phases_completed: vec![],
            metadata: serde_json::json!({
                "duration_ms": chrono::Utc::now().timestamp_millis() - start_ms,
                "mode": self.mode.to_string(),
            }),
        };

        self.phase_repeat(&report, &mut phases);

        // Phase 7: Ship — deliver report
        self.phase_ship(&report, &mut phases).await;

        // Record all completed phases (including repeat + ship) now that they have run
        report.phases_completed = phases
            .iter()
            .filter(|p| p.success)
            .map(|p| p.name.clone())
            .collect();

        info!(
            "GraphBrain complete: {} repos, {} docs, {} work orders",
            report.repos_indexed, report.docs_indexed, report.work_orders.len()
        );

        report
    }

    // ------------------------------------------------------------------
    // Phase 1: Plan
    // ------------------------------------------------------------------

    fn phase_plan(&self, phases: &mut Vec<PhaseResult>) -> Vec<String> {
        info!("Phase 1: Plan — loading target repos");
        let repos = load_target_repos(&self.root);
        // In light mode, only index first 5 repos for speed
        let repos = if self.mode == RunMode::Light {
            repos.into_iter().take(5).collect()
        } else {
            repos
        };
        phases.push(PhaseResult::ok("plan", &format!("Loaded {} repos", repos.len())));
        repos
    }

    // ------------------------------------------------------------------
    // Phase 2: Implement
    // ------------------------------------------------------------------

    async fn phase_implement(
        &self,
        repos: &[String],
        phases: &mut Vec<PhaseResult>,
    ) -> (Vec<crate::repo_indexer::RepoIndex>, usize) {
        info!("Phase 2: Implement — indexing {} repos", repos.len());
        let indexer = RepoIndexer::new(self.root.clone(), repos.to_vec());
        // index_all is CPU/IO-bound (git clone + file scan) — use spawn_blocking to avoid
        // blocking the tokio executor thread.
        let indexes = tokio::task::spawn_blocking(move || indexer.index_all())
            .await
            .unwrap_or_else(|e| {
                warn!("index_all panicked: {}", e);
                vec![]
            });
        let available = indexes.iter().filter(|i| i.status == "available").count();
        let total_docs: usize = indexes.iter().map(|i| i.docs.len()).sum();
        phases.push(PhaseResult::ok(
            "implement",
            &format!("{}/{} repos available, {} docs", available, indexes.len(), total_docs),
        ));
        (indexes, total_docs)
    }

    // ------------------------------------------------------------------
    // Phase 3: Test
    // ------------------------------------------------------------------

    fn phase_test(
        &self,
        indexes: &[crate::repo_indexer::RepoIndex],
        phases: &mut Vec<PhaseResult>,
    ) {
        info!("Phase 3: Test — validating indexes");
        let available = indexes.iter().filter(|i| i.status == "available").count();
        if available == 0 {
            warn!("Phase 3: No repos available — graph will be empty");
            phases.push(PhaseResult::fail("test", "No repos available"));
        } else {
            phases.push(PhaseResult::ok("test", &format!("{} repos passed validation", available)));
        }
    }

    // ------------------------------------------------------------------
    // Phase 4: Evaluate
    // ------------------------------------------------------------------

    fn phase_evaluate(
        &self,
        indexes: &[crate::repo_indexer::RepoIndex],
        phases: &mut Vec<PhaseResult>,
    ) -> crate::graph_builder::KnowledgeGraph {
        info!("Phase 4: Evaluate — building knowledge graph");
        let available: Vec<_> = indexes
            .iter()
            .filter(|i| i.status == "available")
            .cloned()
            .collect();
        let builder = GraphBuilder::new();
        let kg = builder.build_global_graph(&available);
        phases.push(PhaseResult::ok(
            "evaluate",
            &format!(
                "Graph: {} nodes, {} edges, {} repo graphs",
                kg.global_nodes.len(),
                kg.global_edges.len(),
                kg.repo_graphs.len()
            ),
        ));
        kg
    }

    // ------------------------------------------------------------------
    // Phase 5: Patch
    // ------------------------------------------------------------------

    fn phase_patch(
        &self,
        kg: &crate::graph_builder::KnowledgeGraph,
        indexes: &[crate::repo_indexer::RepoIndex],
        phases: &mut Vec<PhaseResult>,
    ) -> Vec<WorkOrder> {
        info!("Phase 5: Patch — analyzing graph and generating work orders");
        let analyzer = Analyzer::new();

        // Build flat doc list for risk analysis
        let docs: Vec<(String, String, String)> = indexes
            .iter()
            .filter(|i| i.status == "available")
            .flat_map(|i| {
                i.docs.iter().map(|d| (i.slug.clone(), d.path.clone(), d.content.clone()))
            })
            .collect();

        let report = analyzer.analyze(kg, &docs);
        let orders = generate_work_orders(&report);
        phases.push(PhaseResult::ok("patch", &format!("{} work orders generated", orders.len())));
        orders
    }

    // ------------------------------------------------------------------
    // Phase 6: Repeat (save to disk)
    // ------------------------------------------------------------------

    fn phase_repeat(&self, report: &GraphBrainReport, phases: &mut Vec<PhaseResult>) {
        info!("Phase 6: Repeat — saving report");

        let json = match serde_json::to_string_pretty(report) {
            Ok(j) => j,
            Err(e) => {
                error!("Could not serialize report: {}", e);
                phases.push(PhaseResult::fail("repeat", &e.to_string()));
                return;
            }
        };

        // Write timestamped snapshot to ops/reports/graphbrain/ (GRAPH_SNAPSHOT contract)
        let snapshot_dir = self.root.join("ops").join("reports").join("graphbrain");
        if std::fs::create_dir_all(&snapshot_dir).is_ok() {
            let ts = chrono::Utc::now().format("%Y%m%dT%H%M%SZ");
            let snapshot_path = snapshot_dir.join(format!("GRAPH_SNAPSHOT_{}.json", ts));
            if let Err(e) = std::fs::write(&snapshot_path, &json) {
                warn!("Could not write snapshot: {}", e);
            } else {
                info!("Snapshot written to {}", snapshot_path.display());
            }
        }

        // Write latest path (backwards-compatibility for consumers of graphbrain_latest.json)
        if let Some(parent) = self.report_path.parent() {
            if let Err(e) = std::fs::create_dir_all(parent) {
                warn!("Could not create report directory: {}", e);
                phases.push(PhaseResult::fail("repeat", &e.to_string()));
                return;
            }
        }
        match std::fs::write(&self.report_path, &json) {
            Ok(_) => {
                phases.push(PhaseResult::ok(
                    "repeat",
                    &format!("Saved to {}", self.report_path.display()),
                ));
            }
            Err(e) => {
                warn!("Could not write report: {}", e);
                phases.push(PhaseResult::fail("repeat", &e.to_string()));
            }
        }
    }

    // ------------------------------------------------------------------
    // Phase 7: Ship (deliver via HTTP if configured)
    // ------------------------------------------------------------------

    async fn phase_ship(&self, report: &GraphBrainReport, phases: &mut Vec<PhaseResult>) {
        info!("Phase 7: Ship — checking for delivery endpoint");

        // Check for GRAPHBRAIN_REPORT_URL env var
        let endpoint = match std::env::var("GRAPHBRAIN_REPORT_URL") {
            Ok(url) => url,
            Err(_) => {
                info!("No GRAPHBRAIN_REPORT_URL set — skipping delivery");
                phases.push(PhaseResult::ok("ship", "No endpoint configured"));
                return;
            }
        };

        // Validate endpoint is in allowlist
        let is_allowed = ALLOWED_REPORT_ENDPOINTS
            .iter()
            .any(|allowed| endpoint.starts_with(allowed));

        if !is_allowed {
            warn!("GRAPHBRAIN_REPORT_URL '{}' not in allowlist — skipping", endpoint);
            phases.push(PhaseResult::fail("ship", "Endpoint not in allowlist"));
            return;
        }

        // Deliver with retries
        let mut last_error = String::new();
        for attempt in 0..MAX_RETRIES {
            if attempt > 0 {
                tokio::time::sleep(Duration::from_secs(RETRY_DELAY_SECS * (attempt as u64))).await;
            }
            match self.http.post(&endpoint).json(report).send().await {
                Ok(resp) if resp.status().is_success() => {
                    phases.push(PhaseResult::ok("ship", &format!("Delivered to {}", endpoint)));
                    return;
                }
                Ok(resp) => {
                    last_error = format!("HTTP {}", resp.status());
                    warn!("Delivery attempt {} failed: {}", attempt + 1, last_error);
                }
                Err(e) => {
                    last_error = e.to_string();
                    warn!("Delivery attempt {} error: {}", attempt + 1, last_error);
                }
            }
        }
        phases.push(PhaseResult::fail("ship", &last_error));
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn run_mode_from_str() {
        assert_eq!("light".parse::<RunMode>().unwrap(), RunMode::Light);
        assert_eq!("full".parse::<RunMode>().unwrap(), RunMode::Full);
        assert!("invalid".parse::<RunMode>().is_err());
    }

    #[test]
    fn run_mode_display() {
        assert_eq!(RunMode::Light.to_string(), "light");
        assert_eq!(RunMode::Full.to_string(), "full");
    }

    #[tokio::test]
    async fn runtime_light_mode_runs_on_temp_dir() {
        let dir = tempfile::tempdir().unwrap();
        // Write a simple README so indexer has something to index
        std::fs::write(dir.path().join("README.md"), "# Test\nrust async tokio rayon serde").unwrap();

        let runtime = GraphBrainRuntime::new(dir.path().to_path_buf(), RunMode::Light);
        let report = runtime.run().await;

        // With no cloneable repos (no git), indexer returns unavailable for all
        // but runtime should still produce a valid (possibly empty) report
        assert_eq!(report.mode, "light");
        assert!(report.timestamp_ms > 0);
        assert!(report.phases_completed.contains(&"plan".to_string()));
    }

    #[test]
    fn graphbrain_report_serializes() {
        let report = GraphBrainReport {
            report_id: "graphbrain.graph_snapshot.v1.0".into(),
            generated_at: "2023-01-01T00:00:00Z".into(),
            mode: "light".into(),
            timestamp_ms: 1_700_000_000_000,
            repos_indexed: 5,
            docs_indexed: 100,
            graph: GraphSummary {
                nodes: 500,
                edges: 1000,
                clusters: 3,
                bridge_terms_top: vec![],
            },
            recommendations: vec![],
            work_orders: vec![],
            phases_completed: vec!["plan".into(), "implement".into()],
            metadata: serde_json::json!({"duration_ms": 3000}),
        };
        let json = serde_json::to_string(&report).unwrap();
        assert!(json.contains("\"mode\":\"light\""));
        assert!(json.contains("\"repos_indexed\":5"));
        assert!(json.contains("\"report_id\""));
    }
}
