/// GraphBrain Work Orders — generate actionable work items from analysis.
/// Replaces: services/graphbrain/work_orders.py
///
/// Python: generate_work_orders() producing wo-consolidate-N, wo-risk-N, wo-gap-N.
/// Rust:   exact ID format match, same priority logic.
use serde::{Deserialize, Serialize};
use tracing::info;

use crate::analyzer::{AnalysisReport, ConsolidationCandidate, KnowledgeGap, RiskFinding};

// ---------------------------------------------------------------------------
// Work order types — exact match with Python
// ---------------------------------------------------------------------------

/// Priority levels for work orders.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum WorkOrderPriority {
    Low,
    Medium,
    High,
    Critical,
}

impl std::fmt::Display for WorkOrderPriority {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            WorkOrderPriority::Low => write!(f, "low"),
            WorkOrderPriority::Medium => write!(f, "medium"),
            WorkOrderPriority::High => write!(f, "high"),
            WorkOrderPriority::Critical => write!(f, "critical"),
        }
    }
}

/// A single work order produced by analysis.
/// Replaces Python: dict with id/type/priority/title/description/metadata
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkOrder {
    pub id: String,
    pub kind: String,        // "consolidate" | "risk" | "gap"
    pub priority: WorkOrderPriority,
    pub title: String,
    pub description: String,
    pub metadata: serde_json::Value,
}

// ---------------------------------------------------------------------------
// Work order generation
// ---------------------------------------------------------------------------

/// Generate work orders from an analysis report.
/// Replaces Python: def generate_work_orders(report)
///
/// Returns work orders with IDs: wo-consolidate-N, wo-risk-N, wo-gap-N
pub fn generate_work_orders(report: &AnalysisReport) -> Vec<WorkOrder> {
    let mut orders: Vec<WorkOrder> = Vec::new();

    // Consolidation work orders
    for (i, candidate) in report.consolidation_candidates.iter().enumerate() {
        orders.push(consolidation_work_order(i + 1, candidate));
    }

    // Risk work orders
    for (i, finding) in report.risk_findings.iter().enumerate() {
        orders.push(risk_work_order(i + 1, finding));
    }

    // Gap work orders
    for (i, gap) in report.gaps.iter().enumerate() {
        orders.push(gap_work_order(i + 1, gap));
    }

    info!("Generated {} work orders", orders.len());
    orders
}

// ---------------------------------------------------------------------------
// Individual work order constructors — exact ID format
// ---------------------------------------------------------------------------

fn consolidation_work_order(n: usize, candidate: &ConsolidationCandidate) -> WorkOrder {
    let priority = if candidate.similarity >= 0.7 {
        WorkOrderPriority::High
    } else if candidate.similarity >= 0.5 {
        WorkOrderPriority::Medium
    } else {
        WorkOrderPriority::Low
    };

    WorkOrder {
        id: format!("wo-consolidate-{}", n),
        kind: "consolidate".into(),
        priority,
        title: format!(
            "Consolidate {} and {}",
            candidate.repo_a, candidate.repo_b
        ),
        description: format!(
            "Repos {} and {} share {:.0}% term overlap. Consider merging or extracting shared functionality.",
            candidate.repo_a,
            candidate.repo_b,
            candidate.similarity * 100.0
        ),
        metadata: serde_json::json!({
            "repo_a": candidate.repo_a,
            "repo_b": candidate.repo_b,
            "similarity": candidate.similarity,
        }),
    }
}

fn risk_work_order(n: usize, finding: &RiskFinding) -> WorkOrder {
    let priority = match finding.severity.as_str() {
        "high" | "critical" => WorkOrderPriority::Critical,
        "medium" => WorkOrderPriority::High,
        _ => WorkOrderPriority::Medium,
    };

    WorkOrder {
        id: format!("wo-risk-{}", n),
        kind: "risk".into(),
        priority,
        title: format!("Fix {} risk in {}", finding.kind, finding.location),
        description: finding.description.clone(),
        metadata: serde_json::json!({
            "kind": finding.kind,
            "location": finding.location,
            "severity": finding.severity,
        }),
    }
}

fn gap_work_order(n: usize, gap: &KnowledgeGap) -> WorkOrder {
    let priority = if gap.gap_score >= 0.8 {
        WorkOrderPriority::Medium
    } else {
        WorkOrderPriority::Low
    };

    WorkOrder {
        id: format!("wo-gap-{}", n),
        kind: "gap".into(),
        priority,
        title: format!("Fill knowledge gap: {}", gap.term),
        description: format!(
            "Term '{}' only appears in {}/{} repos ({:.0}% gap). Consider adding documentation or implementation.",
            gap.term,
            gap.repo_count,
            gap.total_repos,
            gap.gap_score * 100.0
        ),
        metadata: serde_json::json!({
            "term": gap.term,
            "repo_count": gap.repo_count,
            "total_repos": gap.total_repos,
            "gap_score": gap.gap_score,
        }),
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use crate::analyzer::{AnalysisReport, BridgeTerm, TermCluster};

    fn empty_report() -> AnalysisReport {
        AnalysisReport {
            bridge_terms: vec![],
            clusters: vec![],
            gaps: vec![],
            consolidation_candidates: vec![],
            risk_findings: vec![],
        }
    }

    #[test]
    fn empty_report_produces_no_orders() {
        let report = empty_report();
        let orders = generate_work_orders(&report);
        assert!(orders.is_empty());
    }

    #[test]
    fn consolidation_ids_are_sequential() {
        let mut report = empty_report();
        report.consolidation_candidates = vec![
            ConsolidationCandidate {
                repo_a: "repo/a".into(),
                repo_b: "repo/b".into(),
                similarity: 0.8,
            },
            ConsolidationCandidate {
                repo_a: "repo/c".into(),
                repo_b: "repo/d".into(),
                similarity: 0.5,
            },
        ];
        let orders = generate_work_orders(&report);
        assert_eq!(orders[0].id, "wo-consolidate-1");
        assert_eq!(orders[1].id, "wo-consolidate-2");
    }

    #[test]
    fn risk_ids_are_sequential() {
        let mut report = empty_report();
        report.risk_findings = vec![
            RiskFinding {
                kind: "non_tls_url".into(),
                description: "http found".into(),
                location: "repo/a:src/main.rs".into(),
                severity: "medium".into(),
            },
        ];
        let orders = generate_work_orders(&report);
        assert_eq!(orders[0].id, "wo-risk-1");
        assert_eq!(orders[0].kind, "risk");
    }

    #[test]
    fn gap_ids_are_sequential() {
        let mut report = empty_report();
        report.gaps = vec![
            KnowledgeGap {
                term: "obscure_term".into(),
                repo_count: 1,
                total_repos: 10,
                gap_score: 0.9,
            },
        ];
        let orders = generate_work_orders(&report);
        assert_eq!(orders[0].id, "wo-gap-1");
        assert_eq!(orders[0].kind, "gap");
    }

    #[test]
    fn high_similarity_consolidation_is_high_priority() {
        let candidate = ConsolidationCandidate {
            repo_a: "a".into(),
            repo_b: "b".into(),
            similarity: 0.75,
        };
        let order = consolidation_work_order(1, &candidate);
        assert_eq!(order.priority, WorkOrderPriority::High);
    }

    #[test]
    fn medium_severity_risk_is_high_priority() {
        let finding = RiskFinding {
            kind: "non_tls_url".into(),
            description: "test".into(),
            location: "test".into(),
            severity: "medium".into(),
        };
        let order = risk_work_order(1, &finding);
        assert_eq!(order.priority, WorkOrderPriority::High);
    }

    #[test]
    fn mixed_report_produces_ordered_ids() {
        let mut report = empty_report();
        report.consolidation_candidates = vec![
            ConsolidationCandidate { repo_a: "a".into(), repo_b: "b".into(), similarity: 0.6 },
        ];
        report.risk_findings = vec![
            RiskFinding { kind: "non_tls_url".into(), description: "x".into(), location: "y".into(), severity: "low".into() },
        ];
        report.gaps = vec![
            KnowledgeGap { term: "foo".into(), repo_count: 1, total_repos: 5, gap_score: 0.8 },
        ];
        let orders = generate_work_orders(&report);
        assert_eq!(orders.len(), 3);
        assert_eq!(orders[0].id, "wo-consolidate-1");
        assert_eq!(orders[1].id, "wo-risk-1");
        assert_eq!(orders[2].id, "wo-gap-1");
    }
}
