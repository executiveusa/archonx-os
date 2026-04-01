/// Flywheel Engine — self-reinforcing improvement loop.
/// Replaces: archonx/core/flywheel.py
///
/// Every task execution can surface improvements. Those improvements become
/// new tasks, which surface more improvements. This is the compounding mechanism.
///
/// Cycle:
///   execute_task → improvements_found → flywheel.ingest() →
///   prioritized_backlog() → generate_micro_tasks() → execute_task() → ...
use std::sync::{Arc, Mutex};

use chrono::Utc;
use serde::{Deserialize, Serialize};
use tracing::info;

use crate::types::ImprovementPriority;

// ---------------------------------------------------------------------------
// Improvement struct
// ---------------------------------------------------------------------------

/// A single discoverable improvement from task execution.
/// Replaces Python: @dataclass class Improvement
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Improvement {
    pub id: String,
    pub source_skill: String,
    pub source_task_id: String,
    pub description: String,
    pub priority: ImprovementPriority,
    pub category: String,
    pub suggested_action: String,
    pub estimated_effort: EffortLevel,
    pub created_at_ms: i64, // replaces Python time.time()
    pub status: ImprovementStatus,
    pub metadata: serde_json::Value,
}

/// Effort level for an improvement.
/// Replaces Python string: "small" | "medium" | "large"
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
#[serde(rename_all = "lowercase")]
pub enum EffortLevel {
    #[default]
    Small,
    Medium,
    Large,
}

impl EffortLevel {
    /// Weight for impact × inverse-effort scoring.
    pub fn inverse_weight(self) -> u32 {
        match self {
            EffortLevel::Small => 3,
            EffortLevel::Medium => 2,
            EffortLevel::Large => 1,
        }
    }
}

impl std::str::FromStr for EffortLevel {
    type Err = anyhow::Error;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "small" => Ok(EffortLevel::Small),
            "medium" => Ok(EffortLevel::Medium),
            "large" => Ok(EffortLevel::Large),
            other => Err(anyhow::anyhow!("Unknown effort level: {}", other)),
        }
    }
}

/// Lifecycle status of an improvement.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
#[serde(rename_all = "snake_case")]
pub enum ImprovementStatus {
    #[default]
    Pending,
    InProgress,
    Completed,
    Skipped,
}

// ---------------------------------------------------------------------------
// FlywheelStats
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FlywheelStats {
    pub total_ingested: u64,
    pub backlog_pending: usize,
    pub backlog_in_progress: usize,
    pub completed: usize,
    pub cycles_run: u64,
    pub compound_ratio: f64,
}

// ---------------------------------------------------------------------------
// FlywheelEngine
// ---------------------------------------------------------------------------

/// Manages the improvement backlog and drives the self-build loop.
///
/// Thread-safe: uses Arc<Mutex<Vec<Improvement>>> for backlog.
/// Replaces Python: class FlywheelEngine
pub struct FlywheelEngine {
    backlog: Arc<Mutex<Vec<Improvement>>>,
    completed: Arc<Mutex<Vec<Improvement>>>,
    counter: Arc<Mutex<u64>>,
    cycle_count: Arc<Mutex<u64>>,
}

impl Default for FlywheelEngine {
    fn default() -> Self {
        Self::new()
    }
}

impl FlywheelEngine {
    pub fn new() -> Self {
        Self {
            backlog: Arc::new(Mutex::new(Vec::new())),
            completed: Arc::new(Mutex::new(Vec::new())),
            counter: Arc::new(Mutex::new(0)),
            cycle_count: Arc::new(Mutex::new(0)),
        }
    }

    // ------------------------------------------------------------------
    // Ingest improvements
    // ------------------------------------------------------------------

    /// Add discovered improvements to the backlog. Returns count ingested.
    /// Replaces Python: def ingest(self, improvements, source_skill, task_id)
    pub fn ingest(
        &self,
        improvements: &[serde_json::Value],
        source_skill: &str,
        task_id: &str,
    ) -> usize {
        let mut backlog = self.backlog.lock().unwrap();
        let mut counter = self.counter.lock().unwrap();
        let mut added = 0;

        for raw in improvements {
            *counter += 1;
            let priority: ImprovementPriority = raw
                .get("priority")
                .and_then(|v| v.as_str())
                .and_then(|s| s.parse().ok())
                .unwrap_or_default();

            let effort: EffortLevel = raw
                .get("effort")
                .and_then(|v| v.as_str())
                .and_then(|s| s.parse().ok())
                .unwrap_or_default();

            let imp = Improvement {
                id: format!("imp-{:05}", *counter),
                source_skill: source_skill.to_string(),
                source_task_id: task_id.to_string(),
                description: raw
                    .get("description")
                    .and_then(|v| v.as_str())
                    .unwrap_or("")
                    .to_string(),
                priority,
                category: raw
                    .get("category")
                    .and_then(|v| v.as_str())
                    .unwrap_or("general")
                    .to_string(),
                suggested_action: raw
                    .get("suggested_action")
                    .and_then(|v| v.as_str())
                    .unwrap_or("")
                    .to_string(),
                estimated_effort: effort,
                created_at_ms: Utc::now().timestamp_millis(),
                status: ImprovementStatus::Pending,
                metadata: raw
                    .get("metadata")
                    .cloned()
                    .unwrap_or(serde_json::Value::Null),
            };

            info!(
                "Flywheel ingested: {} [{}] — {}",
                imp.id,
                imp.priority,
                imp.description
            );
            backlog.push(imp);
            added += 1;
        }
        added
    }

    // ------------------------------------------------------------------
    // Prioritize and generate micro-tasks
    // ------------------------------------------------------------------

    /// Return backlog sorted by impact score (priority_weight × inverse_effort_weight).
    /// Replaces Python: def prioritized_backlog(self)
    pub fn prioritized_backlog(&self) -> Vec<Improvement> {
        let backlog = self.backlog.lock().unwrap();
        let mut pending: Vec<Improvement> = backlog
            .iter()
            .filter(|i| i.status == ImprovementStatus::Pending)
            .cloned()
            .collect();

        pending.sort_by(|a, b| {
            let score_a = a.priority.weight() * a.estimated_effort.inverse_weight();
            let score_b = b.priority.weight() * b.estimated_effort.inverse_weight();
            score_b.cmp(&score_a) // descending
        });
        pending
    }

    /// Pop top-N improvements, set them in_progress, and convert to micro-tasks.
    /// These re-enter execute_task() to close the loop.
    /// Replaces Python: def generate_micro_tasks(self, limit=5)
    pub fn generate_micro_tasks(&self, limit: usize) -> Vec<serde_json::Value> {
        let top = self.prioritized_backlog();
        let top = &top[..top.len().min(limit)];

        let mut backlog = self.backlog.lock().unwrap();
        let mut cycle_count = self.cycle_count.lock().unwrap();
        let pending_count = backlog
            .iter()
            .filter(|i| i.status == ImprovementStatus::Pending)
            .count();

        let mut tasks = Vec::new();
        for selected in top {
            // Mark in_progress in the backlog
            if let Some(imp) = backlog.iter_mut().find(|i| i.id == selected.id) {
                imp.status = ImprovementStatus::InProgress;
            }

            tasks.push(serde_json::json!({
                "type": selected.category,
                "description": selected.description,
                "crew": "both",
                "flywheel_improvement_id": selected.id,
                "suggested_action": selected.suggested_action,
                "metadata": {
                    "source": selected.source_skill,
                    "priority": selected.priority.to_string()
                }
            }));
        }

        *cycle_count += 1;
        info!(
            "Flywheel cycle {}: generated {} micro-tasks from {} pending",
            cycle_count,
            tasks.len(),
            pending_count
        );
        tasks
    }

    /// Mark an improvement as done and move it to the completed list.
    /// Replaces Python: def mark_completed(self, improvement_id)
    pub fn mark_completed(&self, improvement_id: &str) {
        let mut backlog = self.backlog.lock().unwrap();
        let mut completed = self.completed.lock().unwrap();

        if let Some(pos) = backlog.iter().position(|i| i.id == improvement_id) {
            let mut imp = backlog.remove(pos);
            imp.status = ImprovementStatus::Completed;
            info!("Flywheel: completed {}", improvement_id);
            completed.push(imp);
        }
    }

    // ------------------------------------------------------------------
    // Metrics
    // ------------------------------------------------------------------

    /// Get flywheel statistics.
    /// Replaces Python: @property def stats(self)
    pub fn stats(&self) -> FlywheelStats {
        let backlog = self.backlog.lock().unwrap();
        let completed = self.completed.lock().unwrap();
        let counter = *self.counter.lock().unwrap();
        let cycle_count = *self.cycle_count.lock().unwrap();

        let pending = backlog
            .iter()
            .filter(|i| i.status == ImprovementStatus::Pending)
            .count();
        let in_progress = backlog
            .iter()
            .filter(|i| i.status == ImprovementStatus::InProgress)
            .count();

        FlywheelStats {
            total_ingested: counter,
            backlog_pending: pending,
            backlog_in_progress: in_progress,
            completed: completed.len(),
            cycles_run: cycle_count,
            compound_ratio: if counter > 0 {
                completed.len() as f64 / counter as f64
            } else {
                0.0
            },
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn make_improvement(priority: &str, effort: &str, description: &str) -> serde_json::Value {
        json!({
            "priority": priority,
            "effort": effort,
            "description": description,
            "category": "general",
            "suggested_action": "do the thing",
        })
    }

    #[test]
    fn ingest_adds_to_backlog() {
        let fw = FlywheelEngine::new();
        let improvements = vec![
            make_improvement("high", "small", "Fix memory leak"),
            make_improvement("medium", "large", "Refactor module"),
        ];
        let count = fw.ingest(&improvements, "test_skill", "task-001");
        assert_eq!(count, 2);
        assert_eq!(fw.stats().backlog_pending, 2);
    }

    #[test]
    fn prioritized_backlog_orders_by_impact_score() {
        let fw = FlywheelEngine::new();
        let improvements = vec![
            make_improvement("low", "large", "Low priority"),    // weight 1×1 = 1
            make_improvement("critical", "small", "Critical!"),  // weight 4×3 = 12
            make_improvement("medium", "medium", "Medium item"), // weight 2×2 = 4
        ];
        fw.ingest(&improvements, "s", "t");
        let backlog = fw.prioritized_backlog();
        assert_eq!(backlog[0].description, "Critical!");
        assert_eq!(backlog[2].description, "Low priority");
    }

    #[test]
    fn generate_micro_tasks_marks_in_progress() {
        let fw = FlywheelEngine::new();
        let improvements = vec![
            make_improvement("high", "small", "Task A"),
            make_improvement("medium", "small", "Task B"),
            make_improvement("low", "small", "Task C"),
        ];
        fw.ingest(&improvements, "s", "t");
        let tasks = fw.generate_micro_tasks(2);
        assert_eq!(tasks.len(), 2);
        assert_eq!(fw.stats().backlog_in_progress, 2);
        assert_eq!(fw.stats().backlog_pending, 1);
    }

    #[test]
    fn mark_completed_moves_to_completed() {
        let fw = FlywheelEngine::new();
        fw.ingest(&[make_improvement("high", "small", "Fix it")], "s", "t");
        let tasks = fw.generate_micro_tasks(1);
        let id = tasks[0]["flywheel_improvement_id"]
            .as_str()
            .unwrap()
            .to_string();
        fw.mark_completed(&id);
        let stats = fw.stats();
        assert_eq!(stats.completed, 1);
        assert_eq!(stats.backlog_pending, 0);
        assert_eq!(stats.backlog_in_progress, 0);
    }

    #[test]
    fn stats_compound_ratio() {
        let fw = FlywheelEngine::new();
        fw.ingest(
            &[
                make_improvement("high", "small", "A"),
                make_improvement("high", "small", "B"),
            ],
            "s",
            "t",
        );
        let tasks = fw.generate_micro_tasks(2);
        let id = tasks[0]["flywheel_improvement_id"]
            .as_str()
            .unwrap()
            .to_string();
        fw.mark_completed(&id);
        let stats = fw.stats();
        assert!((stats.compound_ratio - 0.5).abs() < 0.001);
    }

    #[test]
    fn cycles_count_increments() {
        let fw = FlywheelEngine::new();
        fw.ingest(&[make_improvement("medium", "small", "x")], "s", "t");
        fw.generate_micro_tasks(1);
        fw.generate_micro_tasks(1);
        assert_eq!(fw.stats().cycles_run, 2);
    }
}
