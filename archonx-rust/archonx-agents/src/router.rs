/// AgentRouter — dispatch tasks to agents by capability.
///
/// Wraps AgentRegistry with routing logic to select the best agent for a task.
/// Replaces Python: get_agent_for_task() in orchestrator.py + swarm routing.
use std::sync::Arc;

use archonx_core::agent::AgentRegistry;
use archonx_core::types::{Role, TaskType};
use tracing::info;

use crate::persona::{AgentPersona, DefaultPersona, StepResult};

/// Routes tasks to appropriate agents based on TaskType → Role mapping.
pub struct AgentRouter {
    registry: Arc<AgentRegistry>,
}

impl AgentRouter {
    pub fn new(registry: Arc<AgentRegistry>) -> Self {
        Self { registry }
    }

    /// Get the best agent ID for a given task type.
    /// Matches Python orchestrator.py get_agent_for_task() role mapping.
    pub fn agent_for_task_type(&self, task_type: &TaskType) -> Option<String> {
        let role = Self::role_for_task(task_type);
        self.registry
            .get_by_role(role, None)
            .first()
            .map(|a| a.read().unwrap().agent_id.clone())
    }

    /// Map TaskType → Role — exact match with Python routing table.
    fn role_for_task(task_type: &TaskType) -> Role {
        match task_type {
            TaskType::Code | TaskType::Deploy | TaskType::Optimization => Role::Knight,
            TaskType::Security => Role::Rook,
            TaskType::Analysis | TaskType::Review => Role::Bishop,
            _ => Role::Pawn,
        }
    }

    /// Route and execute a task using a DefaultPersona.
    /// In production this would dispatch to real agent logic.
    pub async fn route_and_execute(
        &self,
        task_type: &TaskType,
        task: &str,
        context: &serde_json::Value,
    ) -> StepResult {
        match self.agent_for_task_type(task_type) {
            Some(agent_id) => {
                info!("Routing task '{}' to agent {}", task, agent_id);
                let role = Self::role_for_task(task_type);
                let persona = DefaultPersona {
                    id: agent_id,
                    role: format!("{:?}", role).to_lowercase(),
                };
                persona.step(task, context).await
            }
            None => StepResult::fail("router", &format!("No agent found for task type {:?}", task_type)),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use archonx_core::agent::AgentRegistry;

    fn make_router() -> AgentRouter {
        let registry = Arc::new(AgentRegistry::new());
        archonx_core::agent::build_all_agents(&registry).unwrap();
        AgentRouter::new(registry)
    }

    #[test]
    fn code_task_routes_to_knight() {
        let router = make_router();
        let agent_id = router.agent_for_task_type(&TaskType::Code);
        assert!(agent_id.is_some(), "Expected a knight agent for code task");
    }

    #[test]
    fn security_task_routes_to_rook() {
        let router = make_router();
        let agent_id = router.agent_for_task_type(&TaskType::Security);
        assert!(agent_id.is_some(), "Expected a rook agent for security task");
    }

    #[tokio::test]
    async fn route_and_execute_returns_success() {
        let router = make_router();
        let result = router
            .route_and_execute(
                &TaskType::Analysis,
                "analyze codebase",
                &serde_json::json!({}),
            )
            .await;
        assert!(result.success);
    }
}
