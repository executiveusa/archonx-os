/// AgentPersona trait — per-agent behavior hook.
///
/// Each agent type implements step() to define what it does when activated.
/// Replaces Python: individual agent class methods.
use std::collections::HashMap;

use serde::{Deserialize, Serialize};

/// Result of one agent step.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StepResult {
    pub agent_id: String,
    pub output: serde_json::Value,
    pub success: bool,
    pub metadata: HashMap<String, String>,
}

impl StepResult {
    pub fn ok(agent_id: &str, output: serde_json::Value) -> Self {
        Self {
            agent_id: agent_id.to_string(),
            output,
            success: true,
            metadata: HashMap::new(),
        }
    }

    pub fn fail(agent_id: &str, reason: &str) -> Self {
        Self {
            agent_id: agent_id.to_string(),
            output: serde_json::json!({ "error": reason }),
            success: false,
            metadata: HashMap::new(),
        }
    }
}

/// Core trait for agent persona behavior.
/// Each role (King, Queen, Rook, Bishop, Knight, Pawn) has a default impl.
#[async_trait::async_trait]
pub trait AgentPersona: Send + Sync {
    fn agent_id(&self) -> &str;

    /// Execute one step of agent logic for the given task.
    async fn step(&self, task: &str, context: &serde_json::Value) -> StepResult;
}

/// Default persona — used when no specialized logic is registered.
pub struct DefaultPersona {
    pub id: String,
    pub role: String,
}

#[async_trait::async_trait]
impl AgentPersona for DefaultPersona {
    fn agent_id(&self) -> &str {
        &self.id
    }

    async fn step(&self, task: &str, _context: &serde_json::Value) -> StepResult {
        StepResult::ok(
            &self.id,
            serde_json::json!({
                "role": self.role,
                "task": task,
                "result": "completed",
            }),
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn default_persona_step_succeeds() {
        let p = DefaultPersona {
            id: "test_agent".into(),
            role: "pawn".into(),
        };
        let result = p.step("analyze code", &serde_json::json!({})).await;
        assert!(result.success);
        assert_eq!(result.agent_id, "test_agent");
    }

    #[test]
    fn step_result_fail_has_error() {
        let r = StepResult::fail("agent1", "timeout");
        assert!(!r.success);
        assert_eq!(r.output["error"], "timeout");
    }
}
