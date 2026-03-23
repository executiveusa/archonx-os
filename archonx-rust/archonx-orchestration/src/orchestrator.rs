/// Orchestrator Agent — central command for the 64-agent swarm.
/// Replaces: archonx/orchestration/orchestrator.py
///
/// Handles CREATE, ASSIGN, STATUS, PAUSE, RESUME, TERMINATE, LIST, DELEGATE.
use std::collections::HashMap;
use std::sync::{Arc, RwLock};

use archonx_core::{Agent, AgentRegistry, AgentStatus, Crew, Role, TaskPriority, TaskStatus, TaskType, build_all_agents};
use chrono::Utc;
use serde::{Deserialize, Serialize};
use tokio::sync::mpsc;
use tracing::{info, warn};

// ---------------------------------------------------------------------------
// Commands
// ---------------------------------------------------------------------------

/// Available orchestrator commands.
/// Replaces Python: class OrchestratorCommand(str, Enum)
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum OrchestratorCommand {
    Create,
    Assign,
    Status,
    Pause,
    Resume,
    Terminate,
    List,
    Delegate,
}

impl std::fmt::Display for OrchestratorCommand {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{:?}", self)
    }
}

impl std::str::FromStr for OrchestratorCommand {
    type Err = anyhow::Error;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_uppercase().as_str() {
            "CREATE" => Ok(Self::Create),
            "ASSIGN" => Ok(Self::Assign),
            "STATUS" => Ok(Self::Status),
            "PAUSE" => Ok(Self::Pause),
            "RESUME" => Ok(Self::Resume),
            "TERMINATE" => Ok(Self::Terminate),
            "LIST" => Ok(Self::List),
            "DELEGATE" => Ok(Self::Delegate),
            other => Err(anyhow::anyhow!("Unknown command: {}", other)),
        }
    }
}

// ---------------------------------------------------------------------------
// Task struct (minimal — enough for orchestrator routing)
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Task {
    pub id: String,
    pub title: String,
    pub description: String,
    pub task_type: TaskType,
    pub priority: TaskPriority,
    pub status: TaskStatus,
    pub assigned_agent: Option<String>,
    pub tags: Vec<String>,
    pub metadata: serde_json::Value,
    pub created_at_ms: i64,
    pub updated_at_ms: i64,
    pub result: Option<String>,
    pub error: Option<String>,
}

impl Task {
    pub fn new(
        title: impl Into<String>,
        task_type: TaskType,
        priority: TaskPriority,
    ) -> Self {
        let now = Utc::now().timestamp_millis();
        Self {
            id: format!("task-{}", uuid::Uuid::new_v4().to_string().replace('-', "")[..12].to_string()),
            title: title.into(),
            description: String::new(),
            task_type,
            priority,
            status: TaskStatus::Pending,
            assigned_agent: None,
            tags: Vec::new(),
            metadata: serde_json::Value::Object(serde_json::Map::new()),
            created_at_ms: now,
            updated_at_ms: now,
            result: None,
            error: None,
        }
    }

    pub fn to_dict(&self) -> serde_json::Value {
        serde_json::to_value(self).unwrap_or_default()
    }
}

// ---------------------------------------------------------------------------
// TaskManager
// ---------------------------------------------------------------------------

#[derive(Default)]
pub struct TaskManager {
    tasks: Arc<RwLock<HashMap<String, Task>>>,
    counter: Arc<RwLock<u64>>,
}

impl TaskManager {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn create_task(
        &self,
        title: &str,
        task_type: TaskType,
        priority: TaskPriority,
        assigned_agent: Option<String>,
        tags: Vec<String>,
        metadata: serde_json::Value,
    ) -> Task {
        let mut counter = self.counter.write().unwrap();
        *counter += 1;
        let now = Utc::now().timestamp_millis();
        let counter_val = *counter;
        let task = Task {
            id: format!("task-{:06}", counter_val),
            title: title.to_string(),
            description: String::new(),
            task_type,
            priority,
            status: TaskStatus::Pending,
            assigned_agent,
            tags,
            metadata,
            created_at_ms: now,
            updated_at_ms: now,
            result: None,
            error: None,
        };
        self.tasks
            .write()
            .unwrap()
            .insert(task.id.clone(), task.clone());
        task
    }

    pub fn get_task(&self, id: &str) -> Option<Task> {
        self.tasks.read().unwrap().get(id).cloned()
    }

    pub fn assign_task(&self, task_id: &str, agent_id: &str) -> Option<Task> {
        let mut tasks = self.tasks.write().unwrap();
        if let Some(task) = tasks.get_mut(task_id) {
            task.assigned_agent = Some(agent_id.to_string());
            task.status = TaskStatus::Implementing;
            task.updated_at_ms = Utc::now().timestamp_millis();
            Some(task.clone())
        } else {
            None
        }
    }

    pub fn update_status(&self, task_id: &str, status: TaskStatus, result: Option<&str>, error: Option<&str>) -> Option<Task> {
        let mut tasks = self.tasks.write().unwrap();
        if let Some(task) = tasks.get_mut(task_id) {
            task.status = status;
            task.updated_at_ms = Utc::now().timestamp_millis();
            if let Some(r) = result { task.result = Some(r.to_string()); }
            if let Some(e) = error { task.error = Some(e.to_string()); }
            Some(task.clone())
        } else {
            None
        }
    }

    pub fn get_all_tasks(&self) -> Vec<Task> {
        self.tasks.read().unwrap().values().cloned().collect()
    }

    pub fn get_stats(&self) -> serde_json::Value {
        let tasks = self.tasks.read().unwrap();
        let total = tasks.len();
        let pending = tasks.values().filter(|t| t.status == TaskStatus::Pending).count();
        let active = tasks.values().filter(|t| t.status == TaskStatus::Implementing).count();
        let completed = tasks.values().filter(|t| t.status == TaskStatus::Completed).count();
        let failed = tasks.values().filter(|t| t.status == TaskStatus::Failed).count();
        serde_json::json!({
            "total": total,
            "pending": pending,
            "active": active,
            "completed": completed,
            "failed": failed,
        })
    }
}

// ---------------------------------------------------------------------------
// OrchestratorResult
// ---------------------------------------------------------------------------

/// Result from an orchestrator command.
/// Replaces Python: @dataclass class OrchestratorResult
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrchestratorResult {
    pub success: bool,
    pub command: String,
    pub message: String,
    pub data: serde_json::Value,
    pub timestamp_ms: i64,
}

impl OrchestratorResult {
    fn ok(command: OrchestratorCommand, message: impl Into<String>, data: serde_json::Value) -> Self {
        Self {
            success: true,
            command: command.to_string(),
            message: message.into(),
            data,
            timestamp_ms: Utc::now().timestamp_millis(),
        }
    }

    fn err(command: OrchestratorCommand, message: impl Into<String>) -> Self {
        Self {
            success: false,
            command: command.to_string(),
            message: message.into(),
            data: serde_json::Value::Null,
            timestamp_ms: Utc::now().timestamp_millis(),
        }
    }
}

// ---------------------------------------------------------------------------
// Orchestrator
// ---------------------------------------------------------------------------

/// Central command agent for the 64-agent swarm.
/// Replaces Python: class Orchestrator
pub struct Orchestrator {
    pub registry: Arc<AgentRegistry>,
    pub task_manager: Arc<TaskManager>,
    /// Optional mpsc channel sender for mail notifications.
    mail_tx: Option<mpsc::Sender<MailMessage>>,
    initialized: bool,
}

#[derive(Debug)]
pub struct MailMessage {
    pub sender: String,
    pub recipient: String,
    pub subject: String,
    pub payload: serde_json::Value,
}

impl Orchestrator {
    pub fn new(
        registry: Option<Arc<AgentRegistry>>,
        task_manager: Option<Arc<TaskManager>>,
        mail_tx: Option<mpsc::Sender<MailMessage>>,
    ) -> Self {
        Self {
            registry: registry.unwrap_or_else(|| Arc::new(AgentRegistry::new())),
            task_manager: task_manager.unwrap_or_else(|| Arc::new(TaskManager::new())),
            mail_tx,
            initialized: false,
        }
    }

    /// Initialize — populate registry if empty, activate all agents.
    pub async fn initialize(&mut self) -> anyhow::Result<()> {
        if self.initialized {
            return Ok(());
        }
        if self.registry.is_empty() {
            build_all_agents(&self.registry)?;
        }
        for arc in self.registry.all() {
            arc.write().unwrap().activate();
        }
        self.initialized = true;
        info!("Orchestrator ready with {} agents", self.registry.len());
        Ok(())
    }

    // ------------------------------------------------------------------
    // Command dispatch
    // ------------------------------------------------------------------

    pub async fn execute_command(
        &self,
        command: OrchestratorCommand,
        params: serde_json::Value,
    ) -> OrchestratorResult {
        match command {
            OrchestratorCommand::Create => self.handle_create(params).await,
            OrchestratorCommand::Assign => self.handle_assign(params).await,
            OrchestratorCommand::Status => self.handle_status(params).await,
            OrchestratorCommand::Pause => self.handle_pause(params).await,
            OrchestratorCommand::Resume => self.handle_resume(params).await,
            OrchestratorCommand::Terminate => self.handle_terminate(params).await,
            OrchestratorCommand::List => self.handle_list(params).await,
            OrchestratorCommand::Delegate => self.handle_delegate(params).await,
        }
    }

    // ------------------------------------------------------------------
    // CREATE
    // ------------------------------------------------------------------

    async fn handle_create(&self, params: serde_json::Value) -> OrchestratorResult {
        let title = match params.get("title").and_then(|v| v.as_str()) {
            Some(t) => t.to_string(),
            None => return OrchestratorResult::err(OrchestratorCommand::Create, "Missing 'title'"),
        };

        let task_type: TaskType = params
            .get("task_type")
            .and_then(|v| v.as_str())
            .and_then(|s| {
                serde_json::from_value(serde_json::Value::String(s.to_string())).ok()
            })
            .unwrap_or_default();

        let priority: TaskPriority = params
            .get("priority")
            .and_then(|v| v.as_str())
            .and_then(|s| {
                serde_json::from_value(serde_json::Value::String(s.to_string())).ok()
            })
            .unwrap_or_default();

        let assigned_agent = params
            .get("assigned_agent")
            .and_then(|v| v.as_str())
            .map(String::from);

        let tags: Vec<String> = params
            .get("tags")
            .and_then(|v| v.as_array())
            .map(|arr| {
                arr.iter()
                    .filter_map(|v| v.as_str().map(String::from))
                    .collect()
            })
            .unwrap_or_default();

        let metadata = params
            .get("metadata")
            .cloned()
            .unwrap_or(serde_json::Value::Object(serde_json::Map::new()));

        let task = self.task_manager.create_task(
            &title,
            task_type,
            priority,
            assigned_agent.clone(),
            tags,
            metadata,
        );

        // Notify via mail if agent assigned
        if let (Some(agent_id), Some(tx)) = (&assigned_agent, &self.mail_tx) {
            let _ = tx
                .send(MailMessage {
                    sender: "orchestrator".into(),
                    recipient: agent_id.clone(),
                    subject: format!("New Task: {}", title),
                    payload: serde_json::json!({"task_id": task.id, "command": "CREATE"}),
                })
                .await;
        }

        info!("Created task {}: {}", task.id, title);
        OrchestratorResult::ok(
            OrchestratorCommand::Create,
            format!("Task {} created", task.id),
            serde_json::json!({
                "task_id": task.id,
                "task": task.to_dict(),
            }),
        )
    }

    // ------------------------------------------------------------------
    // ASSIGN
    // ------------------------------------------------------------------

    async fn handle_assign(&self, params: serde_json::Value) -> OrchestratorResult {
        let task_id = match params.get("task_id").and_then(|v| v.as_str()) {
            Some(t) => t.to_string(),
            None => return OrchestratorResult::err(OrchestratorCommand::Assign, "Missing 'task_id'"),
        };
        let agent_id = match params.get("agent_id").and_then(|v| v.as_str()) {
            Some(a) => a.to_string(),
            None => return OrchestratorResult::err(OrchestratorCommand::Assign, "Missing 'agent_id'"),
        };

        let agent_arc = match self.registry.get(&agent_id) {
            Some(a) => a,
            None => return OrchestratorResult::err(OrchestratorCommand::Assign, format!("Agent not found: {}", agent_id)),
        };

        if agent_arc.read().unwrap().status == AgentStatus::Busy {
            return OrchestratorResult::err(OrchestratorCommand::Assign, format!("Agent {} is busy", agent_id));
        }

        let task = match self.task_manager.assign_task(&task_id, &agent_id) {
            Some(t) => t,
            None => return OrchestratorResult::err(OrchestratorCommand::Assign, format!("Task not found: {}", task_id)),
        };

        if let Some(tx) = &self.mail_tx {
            let _ = tx
                .send(MailMessage {
                    sender: "orchestrator".into(),
                    recipient: agent_id.clone(),
                    subject: format!("Assigned: {}", task.title),
                    payload: serde_json::json!({"task_id": task_id, "command": "ASSIGN"}),
                })
                .await;
        }

        info!("Assigned task {} to {}", task_id, agent_id);
        OrchestratorResult::ok(
            OrchestratorCommand::Assign,
            format!("Task {} assigned to {}", task_id, agent_id),
            serde_json::json!({ "task_id": task_id, "agent_id": agent_id }),
        )
    }

    // ------------------------------------------------------------------
    // STATUS
    // ------------------------------------------------------------------

    async fn handle_status(&self, params: serde_json::Value) -> OrchestratorResult {
        let task_id = params.get("task_id").and_then(|v| v.as_str());
        let agent_id = params.get("agent_id").and_then(|v| v.as_str());
        let mut data = serde_json::Map::new();

        if let Some(tid) = task_id {
            match self.task_manager.get_task(tid) {
                None => return OrchestratorResult::err(OrchestratorCommand::Status, format!("Task not found: {}", tid)),
                Some(t) => { data.insert("task".into(), t.to_dict()); }
            }
        }

        if let Some(aid) = agent_id {
            match self.registry.get(aid) {
                None => return OrchestratorResult::err(OrchestratorCommand::Status, format!("Agent not found: {}", aid)),
                Some(arc) => {
                    let a = arc.read().unwrap();
                    data.insert("agent".into(), serde_json::json!({
                        "agent_id": a.agent_id,
                        "name": a.name,
                        "status": a.status.to_string(),
                        "health": a.health,
                        "tasks_completed": a.tasks_completed,
                        "score": a.score,
                    }));
                }
            }
        }

        if task_id.is_none() && agent_id.is_none() {
            data.insert("agents".into(), serde_json::json!({
                "total": self.registry.len(),
                "by_status": self.agent_status_counts(),
                "by_crew": {
                    "white": self.registry.get_by_crew(Crew::White).len(),
                    "black": self.registry.get_by_crew(Crew::Black).len(),
                }
            }));
            data.insert("tasks".into(), self.task_manager.get_stats());
        }

        OrchestratorResult::ok(
            OrchestratorCommand::Status,
            "Status retrieved",
            serde_json::Value::Object(data),
        )
    }

    // ------------------------------------------------------------------
    // PAUSE
    // ------------------------------------------------------------------

    async fn handle_pause(&self, params: serde_json::Value) -> OrchestratorResult {
        let task_id = match params.get("task_id").and_then(|v| v.as_str()) {
            Some(t) => t,
            None => return OrchestratorResult::err(OrchestratorCommand::Pause, "Missing 'task_id'"),
        };
        let reason = params.get("reason").and_then(|v| v.as_str());
        match self.task_manager.update_status(task_id, TaskStatus::Paused, reason, None) {
            None => OrchestratorResult::err(OrchestratorCommand::Pause, format!("Task not found: {}", task_id)),
            Some(t) => {
                if let Some(tx) = &self.mail_tx {
                    if let Some(aid) = &t.assigned_agent {
                        let _ = tx.send(MailMessage {
                            sender: "orchestrator".into(),
                            recipient: aid.clone(),
                            subject: format!("Task Paused: {}", t.title),
                            payload: serde_json::json!({"task_id": task_id, "reason": reason, "command": "PAUSE"}),
                        }).await;
                    }
                }
                info!("Paused task {}", task_id);
                OrchestratorResult::ok(OrchestratorCommand::Pause, format!("Task {} paused", task_id), serde_json::json!({"task_id": task_id, "reason": reason}))
            }
        }
    }

    // ------------------------------------------------------------------
    // RESUME
    // ------------------------------------------------------------------

    async fn handle_resume(&self, params: serde_json::Value) -> OrchestratorResult {
        let task_id = match params.get("task_id").and_then(|v| v.as_str()) {
            Some(t) => t,
            None => return OrchestratorResult::err(OrchestratorCommand::Resume, "Missing 'task_id'"),
        };
        match self.task_manager.get_task(task_id) {
            None => OrchestratorResult::err(OrchestratorCommand::Resume, format!("Task not found: {}", task_id)),
            Some(t) if t.status != TaskStatus::Paused => OrchestratorResult::err(
                OrchestratorCommand::Resume,
                format!("Task {} is not paused (status: {})", task_id, t.status),
            ),
            Some(_) => {
                let updated = self.task_manager.update_status(task_id, TaskStatus::Implementing, None, None);
                if let (Some(t), Some(tx)) = (updated, &self.mail_tx) {
                    if let Some(aid) = &t.assigned_agent {
                        let _ = tx.send(MailMessage {
                            sender: "orchestrator".into(),
                            recipient: aid.clone(),
                            subject: format!("Task Resumed: {}", t.title),
                            payload: serde_json::json!({"task_id": task_id, "command": "RESUME"}),
                        }).await;
                    }
                }
                info!("Resumed task {}", task_id);
                OrchestratorResult::ok(OrchestratorCommand::Resume, format!("Task {} resumed", task_id), serde_json::json!({"task_id": task_id}))
            }
        }
    }

    // ------------------------------------------------------------------
    // TERMINATE
    // ------------------------------------------------------------------

    async fn handle_terminate(&self, params: serde_json::Value) -> OrchestratorResult {
        let task_id = match params.get("task_id").and_then(|v| v.as_str()) {
            Some(t) => t,
            None => return OrchestratorResult::err(OrchestratorCommand::Terminate, "Missing 'task_id'"),
        };
        let reason = params.get("reason").and_then(|v| v.as_str()).unwrap_or("Terminated by orchestrator");
        match self.task_manager.update_status(task_id, TaskStatus::Failed, None, Some(reason)) {
            None => OrchestratorResult::err(OrchestratorCommand::Terminate, format!("Task not found: {}", task_id)),
            Some(t) => {
                if let (Some(aid), Some(tx)) = (&t.assigned_agent, &self.mail_tx) {
                    let _ = tx.send(MailMessage {
                        sender: "orchestrator".into(),
                        recipient: aid.clone(),
                        subject: format!("Task Terminated: {}", t.title),
                        payload: serde_json::json!({"task_id": task_id, "reason": reason, "command": "TERMINATE"}),
                    }).await;
                }
                info!("Terminated task {}", task_id);
                OrchestratorResult::ok(OrchestratorCommand::Terminate, format!("Task {} terminated", task_id), serde_json::json!({"task_id": task_id, "reason": reason}))
            }
        }
    }

    // ------------------------------------------------------------------
    // LIST
    // ------------------------------------------------------------------

    async fn handle_list(&self, params: serde_json::Value) -> OrchestratorResult {
        let limit = params.get("limit").and_then(|v| v.as_u64()).unwrap_or(50) as usize;
        let status_filter = params.get("status").and_then(|v| v.as_str());

        let tasks: Vec<serde_json::Value> = self
            .task_manager
            .get_all_tasks()
            .into_iter()
            .filter(|t| {
                status_filter.map_or(true, |s| t.status.to_string() == s)
            })
            .take(limit)
            .map(|t| t.to_dict())
            .collect();

        OrchestratorResult::ok(
            OrchestratorCommand::List,
            format!("Found {} tasks", tasks.len()),
            serde_json::json!({ "tasks": tasks, "count": tasks.len() }),
        )
    }

    // ------------------------------------------------------------------
    // DELEGATE
    // ------------------------------------------------------------------

    async fn handle_delegate(&self, params: serde_json::Value) -> OrchestratorResult {
        let task_id = match params.get("task_id").and_then(|v| v.as_str()) {
            Some(t) => t,
            None => return OrchestratorResult::err(OrchestratorCommand::Delegate, "Missing 'task_id'"),
        };
        let crew = params.get("crew").and_then(|v| v.as_str()).unwrap_or("white");
        let queen_id = if crew.to_lowercase() == "white" {
            "synthia_queen_white"
        } else {
            "shadow_queen_black"
        };

        match self.registry.get(queen_id) {
            None => OrchestratorResult::err(OrchestratorCommand::Delegate, format!("Queen not found: {}", queen_id)),
            Some(_) => {
                match self.task_manager.assign_task(task_id, queen_id) {
                    None => OrchestratorResult::err(OrchestratorCommand::Delegate, format!("Task not found: {}", task_id)),
                    Some(t) => {
                        if let Some(tx) = &self.mail_tx {
                            let _ = tx.send(MailMessage {
                                sender: "orchestrator".into(),
                                recipient: queen_id.to_string(),
                                subject: format!("Delegated: {}", t.title),
                                payload: serde_json::json!({"task_id": task_id, "command": "DELEGATE", "crew": crew}),
                            }).await;
                        }
                        info!("Delegated task {} to {}", task_id, queen_id);
                        OrchestratorResult::ok(OrchestratorCommand::Delegate, format!("Task {} delegated to {}", task_id, queen_id), serde_json::json!({"task_id": task_id, "queen_id": queen_id, "crew": crew}))
                    }
                }
            }
        }
    }

    // ------------------------------------------------------------------
    // Helpers
    // ------------------------------------------------------------------

    fn agent_status_counts(&self) -> serde_json::Value {
        let mut counts: HashMap<String, usize> = HashMap::new();
        for arc in self.registry.all() {
            let status = arc.read().unwrap().status.to_string();
            *counts.entry(status).or_insert(0) += 1;
        }
        serde_json::to_value(counts).unwrap_or_default()
    }

    /// Find the best available agent for a given task type.
    /// Replaces Python: def get_agent_for_task(self, task_type, crew=Crew.WHITE)
    pub fn get_agent_for_task(&self, task_type: TaskType, crew: Crew) -> Option<Arc<RwLock<Agent>>> {
        let preferred_role = match task_type {
            TaskType::Code | TaskType::Deploy | TaskType::Optimization => Role::Knight,
            TaskType::Security => Role::Rook,
            TaskType::Analysis | TaskType::Review => Role::Bishop,
            _ => Role::Pawn,
        };

        // Get available agents with preferred role
        let mut candidates: Vec<_> = self
            .registry
            .get_by_role(preferred_role, Some(crew))
            .into_iter()
            .filter(|arc| arc.read().unwrap().status == AgentStatus::Active)
            .collect();

        if candidates.is_empty() {
            // Fallback to any active agent in the crew
            candidates = self
                .registry
                .get_by_crew(crew)
                .into_iter()
                .filter(|arc| arc.read().unwrap().status == AgentStatus::Active)
                .collect();
        }

        // Pick agent with lowest task count
        candidates.into_iter().min_by_key(|arc| arc.read().unwrap().tasks_completed)
    }
}

/// Singleton via tokio::sync::OnceCell.
static ORCHESTRATOR: tokio::sync::OnceCell<tokio::sync::Mutex<Orchestrator>> =
    tokio::sync::OnceCell::const_new();

pub async fn get_orchestrator() -> &'static tokio::sync::Mutex<Orchestrator> {
    ORCHESTRATOR
        .get_or_init(|| async {
            let mut o = Orchestrator::new(None, None, None);
            o.initialize().await.expect("Orchestrator init failed");
            tokio::sync::Mutex::new(o)
        })
        .await
}

#[cfg(test)]
mod tests {
    use super::*;

    async fn make_orch() -> Orchestrator {
        let mut o = Orchestrator::new(None, None, None);
        o.initialize().await.unwrap();
        o
    }

    #[tokio::test]
    async fn create_command_succeeds() {
        let o = make_orch().await;
        let r = o.execute_command(
            OrchestratorCommand::Create,
            serde_json::json!({ "title": "Test task", "task_type": "code" }),
        ).await;
        assert!(r.success);
        assert!(r.data["task_id"].as_str().is_some());
    }

    #[tokio::test]
    async fn assign_command_to_valid_agent() {
        let o = make_orch().await;
        let create = o.execute_command(
            OrchestratorCommand::Create,
            serde_json::json!({ "title": "Assign me" }),
        ).await;
        let task_id = create.data["task_id"].as_str().unwrap().to_string();
        let r = o.execute_command(
            OrchestratorCommand::Assign,
            serde_json::json!({ "task_id": task_id, "agent_id": "probe_pawn_white_g" }),
        ).await;
        assert!(r.success, "Assign failed: {}", r.message);
    }

    #[tokio::test]
    async fn assign_to_unknown_agent_fails() {
        let o = make_orch().await;
        let create = o.execute_command(
            OrchestratorCommand::Create,
            serde_json::json!({ "title": "Test" }),
        ).await;
        let task_id = create.data["task_id"].as_str().unwrap().to_string();
        let r = o.execute_command(
            OrchestratorCommand::Assign,
            serde_json::json!({ "task_id": task_id, "agent_id": "nonexistent" }),
        ).await;
        assert!(!r.success);
    }

    #[tokio::test]
    async fn status_command_returns_totals() {
        let o = make_orch().await;
        let r = o.execute_command(OrchestratorCommand::Status, serde_json::json!({})).await;
        assert!(r.success);
        assert_eq!(r.data["agents"]["total"].as_u64().unwrap(), 64);
    }

    #[tokio::test]
    async fn get_agent_for_task_routing() {
        let o = make_orch().await;
        let a = o.get_agent_for_task(TaskType::Code, Crew::White);
        assert!(a.is_some());
        assert_eq!(a.unwrap().read().unwrap().crew, Crew::White);
    }
}
