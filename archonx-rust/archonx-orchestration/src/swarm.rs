/// Agent Swarm Deployment System.
/// Replaces: archonx/orchestration/swarm.py
///
/// Wave-based parallel execution using tokio::task::JoinSet.
/// Replaces Python's asyncio.gather() with JoinSet for structured concurrency.
use std::time::Instant;

use archonx_core::{AgentRegistry, AgentStatus, Crew, Role};
use serde::{Deserialize, Serialize};
use tokio::task::JoinSet;
use tracing::{info, warn};

// ---------------------------------------------------------------------------
// SwarmAgent — lightweight view for swarm execution
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SwarmAgent {
    pub agent_id: String,
    pub crew: String,
    pub role: String,
    pub skills: Vec<String>,
    pub status: String,
    pub current_task: Option<String>,
}

// ---------------------------------------------------------------------------
// WaveResult
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WaveResult {
    pub wave_id: String,
    pub agents: Vec<String>,
    pub results: serde_json::Value,
    pub success: bool,
    pub duration_ms: u64,
    pub errors: Vec<String>,
}

// ---------------------------------------------------------------------------
// SwarmOrchestrator
// ---------------------------------------------------------------------------

/// Orchestrates the 64-agent swarm with wave-based execution.
///
/// Features:
/// - YOLO mode for autonomous execution (no human confirmation)
/// - Wave-based parallel execution (5 agents per wave by default)
/// - Crew coordination (White + Black)
/// - tokio::task::JoinSet for structured concurrency
/// Replaces Python: class SwarmOrchestrator with asyncio.gather()
pub struct SwarmOrchestrator {
    pub yolo: bool,
    pub wave_size: usize,
    pub max_waves: usize,
    agents: Vec<SwarmAgent>,
}

impl SwarmOrchestrator {
    pub fn new(yolo: bool, wave_size: usize, max_waves: usize) -> Self {
        let agents = Self::build_agents();
        info!(
            "Swarm orchestrator initialized with {} agents (YOLO: {})",
            agents.len(),
            yolo
        );
        Self {
            yolo,
            wave_size,
            max_waves,
            agents,
        }
    }

    /// Build the 64-agent roster for swarm execution.
    fn build_agents() -> Vec<SwarmAgent> {
        // White crew roles (32 agents, cycling through 5 roles)
        let white_roles: &[(&str, &[&str])] = &[
            ("queen", &["orchestration", "strategy", "decision_making"]),
            ("architect", &["design", "architecture", "planning"]),
            ("builder", &["implementation", "coding", "building"]),
            ("healer", &["debugging", "fixing", "optimization"]),
            ("mentor", &["documentation", "teaching", "explanation"]),
        ];

        let black_roles: &[(&str, &[&str])] = &[
            ("king", &["attack_coordination", "security_strategy"]),
            ("assassin", &["security_testing", "penetration", "vulnerability"]),
            ("saboteur", &["stress_testing", "chaos", "resilience"]),
            ("spy", &["reconnaissance", "research", "intelligence"]),
            ("nemesis", &["quality_assurance", "critique", "review"]),
        ];

        let mut agents = Vec::with_capacity(64);
        let mut agent_id = 0u32;

        for i in 0..32 {
            let (role, skills) = white_roles[i % white_roles.len()];
            agents.push(SwarmAgent {
                agent_id: format!("White-{}-{:02}", &role[..3], agent_id),
                crew: "white".into(),
                role: role.to_string(),
                skills: skills.iter().map(|s| s.to_string()).collect(),
                status: "idle".into(),
                current_task: None,
            });
            agent_id += 1;
        }

        for i in 0..32 {
            let (role, skills) = black_roles[i % black_roles.len()];
            agents.push(SwarmAgent {
                agent_id: format!("Black-{}-{:02}", &role[..3], agent_id),
                crew: "black".into(),
                role: role.to_string(),
                skills: skills.iter().map(|s| s.to_string()).collect(),
                status: "idle".into(),
                current_task: None,
            });
            agent_id += 1;
        }

        agents
    }

    // ------------------------------------------------------------------
    // Public deploy interface
    // ------------------------------------------------------------------

    /// Deploy the agent swarm for a task using wave-based JoinSet execution.
    /// Replaces Python: async def deploy_swarm(self, task, yolo, crews, skills_filter)
    pub async fn deploy_swarm(
        &mut self,
        task: &str,
        yolo: Option<bool>,
        crews: Option<Vec<String>>,
        skills_filter: Option<Vec<String>>,
    ) -> serde_json::Value {
        let yolo_mode = yolo.unwrap_or(self.yolo);
        info!("Deploying swarm for task: {}", task);

        let filtered = self.filter_agents(crews.as_deref(), skills_filter.as_deref());
        if filtered.is_empty() {
            return serde_json::json!({ "error": "No agents match the filter criteria" });
        }

        let waves = self.create_waves(&filtered);
        let mut wave_results: Vec<WaveResult> = Vec::new();

        for (wave_idx, wave_agents) in waves.iter().enumerate() {
            let wave_id = format!("wave_{:02}", wave_idx + 1);
            let result = self
                .execute_wave(&wave_id, wave_agents, task, yolo_mode)
                .await;
            info!("Wave {} complete: success={}", wave_id, result.success);
            wave_results.push(result);
        }

        let overall_success = wave_results.iter().all(|r| r.success);
        let session_id = format!("session-{}", uuid::Uuid::new_v4());

        serde_json::json!({
            "task": task,
            "yolo_mode": yolo_mode,
            "total_agents": filtered.len(),
            "total_waves": wave_results.len(),
            "wave_results": wave_results,
            "success": overall_success,
            "session_id": session_id,
        })
    }

    // ------------------------------------------------------------------
    // Wave execution — JoinSet for structured concurrency
    // ------------------------------------------------------------------

    async fn execute_wave(
        &mut self,
        wave_id: &str,
        agents: &[SwarmAgent],
        task: &str,
        yolo: bool,
    ) -> WaveResult {
        let start = Instant::now();

        // Mark agents active
        for agent in agents {
            if let Some(a) = self.agents.iter_mut().find(|a| a.agent_id == agent.agent_id) {
                a.status = "active".into();
                a.current_task = Some(task.to_string());
            }
        }

        // Execute agents in parallel with JoinSet
        // Replaces Python: asyncio.gather(*tasks, return_exceptions=True)
        let mut join_set: JoinSet<(String, Result<serde_json::Value, String>)> = JoinSet::new();

        for agent in agents.iter().cloned() {
            let task_str = task.to_string();
            let yolo_flag = yolo;
            join_set.spawn(async move {
                let result = Self::run_agent_logic(&agent, &task_str, yolo_flag).await;
                (agent.agent_id.clone(), result)
            });
        }

        let mut agent_results = serde_json::Map::new();
        let mut errors: Vec<String> = Vec::new();

        while let Some(joined) = join_set.join_next().await {
            match joined {
                Ok((agent_id, Ok(result))) => {
                    agent_results.insert(agent_id, result);
                }
                Ok((agent_id, Err(e))) => {
                    let err_msg = format!("{}: {}", agent_id, e);
                    errors.push(err_msg.clone());
                    agent_results.insert(
                        agent_id,
                        serde_json::json!({ "error": e }),
                    );
                }
                Err(join_err) => {
                    warn!("JoinSet error: {}", join_err);
                }
            }
        }

        // Mark agents completed
        for agent in agents {
            if let Some(a) = self.agents.iter_mut().find(|a| a.agent_id == agent.agent_id) {
                a.status = "completed".into();
                a.current_task = None;
            }
        }

        let duration_ms = start.elapsed().as_millis() as u64;

        WaveResult {
            wave_id: wave_id.to_string(),
            agents: agents.iter().map(|a| a.agent_id.clone()).collect(),
            results: serde_json::Value::Object(agent_results),
            success: errors.is_empty(),
            duration_ms,
            errors,
        }
    }

    async fn run_agent_logic(
        agent: &SwarmAgent,
        task: &str,
        yolo: bool,
    ) -> Result<serde_json::Value, String> {
        // In production this invokes real agent execution.
        // Simulation: short async yield to allow concurrency.
        tokio::task::yield_now().await;

        Ok(serde_json::json!({
            "agent_id": agent.agent_id,
            "crew": agent.crew,
            "role": agent.role,
            "task": task,
            "status": "completed",
            "yolo_mode": yolo,
        }))
    }

    // ------------------------------------------------------------------
    // Filtering helpers
    // ------------------------------------------------------------------

    fn filter_agents(
        &self,
        crews: Option<&[String]>,
        skills: Option<&[String]>,
    ) -> Vec<SwarmAgent> {
        self.agents
            .iter()
            .filter(|a| {
                let crew_ok = crews.map_or(true, |c| c.contains(&a.crew));
                let skills_ok = skills.map_or(true, |s| {
                    s.iter().any(|sk| a.skills.contains(sk))
                });
                crew_ok && skills_ok
            })
            .cloned()
            .collect()
    }

    fn create_waves<'a>(&self, agents: &'a [SwarmAgent]) -> Vec<&'a [SwarmAgent]> {
        agents
            .chunks(self.wave_size)
            .take(self.max_waves)
            .collect()
    }

    // ------------------------------------------------------------------
    // Stats
    // ------------------------------------------------------------------

    pub fn get_swarm_stats(&self) -> serde_json::Value {
        let idle = self.agents.iter().filter(|a| a.status == "idle").count();
        let active = self.agents.iter().filter(|a| a.status == "active").count();
        let completed = self.agents.iter().filter(|a| a.status == "completed").count();
        serde_json::json!({
            "total_agents": self.agents.len(),
            "yolo_mode": self.yolo,
            "wave_size": self.wave_size,
            "max_waves": self.max_waves,
            "by_crew": {
                "white": self.agents.iter().filter(|a| a.crew == "white").count(),
                "black": self.agents.iter().filter(|a| a.crew == "black").count(),
            },
            "by_status": { "idle": idle, "active": active, "completed": completed }
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn make_swarm() -> SwarmOrchestrator {
        SwarmOrchestrator::new(false, 5, 13)
    }

    #[test]
    fn swarm_builds_64_agents() {
        let s = make_swarm();
        assert_eq!(s.agents.len(), 64);
    }

    #[test]
    fn filter_by_crew() {
        let s = make_swarm();
        let white = s.filter_agents(Some(&["white".to_string()]), None);
        assert_eq!(white.len(), 32);
    }

    #[test]
    fn create_waves_limits_to_max() {
        let s = make_swarm();
        let agents = s.filter_agents(None, None);
        let waves = s.create_waves(&agents);
        assert!(waves.len() <= 13);
    }

    #[tokio::test]
    async fn deploy_swarm_returns_results() {
        let mut s = SwarmOrchestrator::new(true, 5, 1); // 1 wave for speed
        let result = s
            .deploy_swarm("Upgrade repository", Some(true), None, None)
            .await;
        assert!(result["success"].as_bool().unwrap_or(false));
        assert_eq!(result["total_waves"].as_u64().unwrap(), 1);
    }

    #[tokio::test]
    async fn deploy_with_crew_filter() {
        let mut s = SwarmOrchestrator::new(false, 5, 1);
        let result = s
            .deploy_swarm(
                "Security audit",
                None,
                Some(vec!["black".to_string()]),
                None,
            )
            .await;
        assert_eq!(result["total_agents"].as_u64().unwrap(), 32);
    }
}
