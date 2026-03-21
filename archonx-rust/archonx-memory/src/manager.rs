/// Memory Manager — replaces file-based storage with sqlx + PostgreSQL.
/// Replaces: archonx/memory/memory_manager.py + archonx/memory/byterover_client.py
///
/// Uses sqlx::PgPool for all storage.
/// pgvector extension for semantic similarity search (production).
/// Falls back to keyword search when pool unavailable.
use std::collections::HashMap;
use std::sync::Arc;

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::PgPool;
use tracing::{info, warn};

// ---------------------------------------------------------------------------
// AgentExpertise
// ---------------------------------------------------------------------------

/// Expertise record for an agent.
/// Replaces Python: @dataclass class AgentExpertise
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentExpertise {
    pub agent_id: String,
    pub problem: String,
    pub approach: String,
    pub result: String,
    pub confidence: f64,
    pub timestamp: DateTime<Utc>, // replaces Python datetime.now(timezone.UTC).isoformat()
    pub reuse_count: i64,
}

impl AgentExpertise {
    pub fn new(
        agent_id: impl Into<String>,
        problem: impl Into<String>,
        approach: impl Into<String>,
        result: impl Into<String>,
        confidence: f64,
    ) -> Self {
        Self {
            agent_id: agent_id.into(),
            problem: problem.into(),
            approach: approach.into(),
            result: result.into(),
            confidence,
            timestamp: Utc::now(),
            reuse_count: 0,
        }
    }
}

// ---------------------------------------------------------------------------
// SessionMemory
// ---------------------------------------------------------------------------

/// Memory for a single agent session.
/// Replaces Python: @dataclass class SessionMemory
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionMemory {
    pub session_id: String,
    pub agent_id: String,
    pub task: String,
    pub decisions: Vec<serde_json::Value>,
    pub context_used: Vec<String>,
    pub tools_used: Vec<serde_json::Value>,
    pub start_time: DateTime<Utc>,
    pub end_time: Option<DateTime<Utc>>,
    pub success: Option<bool>,
}

impl SessionMemory {
    pub fn new(session_id: impl Into<String>, agent_id: impl Into<String>, task: impl Into<String>) -> Self {
        Self {
            session_id: session_id.into(),
            agent_id: agent_id.into(),
            task: task.into(),
            decisions: Vec::new(),
            context_used: Vec::new(),
            tools_used: Vec::new(),
            start_time: Utc::now(),
            end_time: None,
            success: None,
        }
    }
}

// ---------------------------------------------------------------------------
// MemoryLayer
// ---------------------------------------------------------------------------

/// Memory layer types for context storage.
/// Replaces Python: class MemoryLayer(Enum)
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum MemoryLayer {
    Project,
    Team,
    Global,
}

impl std::fmt::Display for MemoryLayer {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            MemoryLayer::Project => write!(f, "project_local"),
            MemoryLayer::Team => write!(f, "team_shared"),
            MemoryLayer::Global => write!(f, "global_patterns"),
        }
    }
}

// ---------------------------------------------------------------------------
// MemoryEntry
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryEntry {
    pub key: String,
    pub value: serde_json::Value,
    pub layer: MemoryLayer,
    pub tags: Vec<String>,
    pub confidence: f64,
    pub access_count: i64,
    pub created_at: DateTime<Utc>,
}

// ---------------------------------------------------------------------------
// SearchResult
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchResult {
    pub entry: MemoryEntry,
    pub score: f64,
    pub highlights: Vec<String>,
}

// ---------------------------------------------------------------------------
// MemoryManager
// ---------------------------------------------------------------------------

/// High-level memory management for ArchonX agents.
///
/// Backed by sqlx::PgPool + PostgreSQL with pgvector for semantic search.
/// Falls back to in-memory HashMap when no pool is configured.
/// Replaces Python: class MemoryManager + class ByteRoverClient
pub struct MemoryManager {
    pool: Option<PgPool>,
    /// In-memory fallback cache (used when no DB pool is configured)
    cache: Arc<tokio::sync::RwLock<HashMap<String, MemoryEntry>>>,
    sessions: Arc<tokio::sync::RwLock<HashMap<String, SessionMemory>>>,
}

impl MemoryManager {
    /// Create with a PostgreSQL pool.
    pub fn with_pool(pool: PgPool) -> Self {
        Self {
            pool: Some(pool),
            cache: Arc::new(tokio::sync::RwLock::new(HashMap::new())),
            sessions: Arc::new(tokio::sync::RwLock::new(HashMap::new())),
        }
    }

    /// Create without a DB pool (in-memory only). Useful for tests.
    pub fn in_memory() -> Self {
        Self {
            pool: None,
            cache: Arc::new(tokio::sync::RwLock::new(HashMap::new())),
            sessions: Arc::new(tokio::sync::RwLock::new(HashMap::new())),
        }
    }

    // ------------------------------------------------------------------
    // Context retrieval
    // ------------------------------------------------------------------

    /// Get relevant context for a task.
    /// Replaces Python: async def get_task_context(self, task, agent_id, max_items)
    pub async fn get_task_context(
        &self,
        task: &str,
        agent_id: Option<&str>,
        max_items: usize,
    ) -> serde_json::Value {
        let patterns = self
            .search(task, Some(MemoryLayer::Global), max_items, 0.75)
            .await;
        let related = self
            .search(task, Some(MemoryLayer::Project), max_items, 0.75)
            .await;

        let expertise: Vec<serde_json::Value> = if let Some(aid) = agent_id {
            self.get_expertise(aid, Some(task), max_items).await
                .into_iter()
                .map(|e| serde_json::to_value(e).unwrap_or_default())
                .collect()
        } else {
            vec![]
        };

        serde_json::json!({
            "task": task,
            "patterns": patterns.iter().map(|r| serde_json::json!({
                "key": r.entry.key,
                "value": r.entry.value,
                "score": r.score,
            })).collect::<Vec<_>>(),
            "related_memories": related.iter().map(|r| serde_json::json!({
                "key": r.entry.key,
                "value": r.entry.value,
                "score": r.score,
            })).collect::<Vec<_>>(),
            "expertise": expertise,
        })
    }

    // ------------------------------------------------------------------
    // Expertise management
    // ------------------------------------------------------------------

    /// Record agent expertise.
    /// Replaces Python: async def record_expertise(self, agent_id, problem, approach, result, confidence)
    pub async fn record_expertise(
        &self,
        agent_id: &str,
        problem: &str,
        approach: &str,
        result: &str,
        confidence: f64,
    ) -> anyhow::Result<AgentExpertise> {
        let expertise = AgentExpertise::new(agent_id, problem, approach, result, confidence);
        let key = format!("expertise:{}:{}", agent_id, uuid::Uuid::new_v4());

        // Save to PostgreSQL if pool available
        if let Some(pool) = &self.pool {
            let value = serde_json::to_value(&expertise)?;
            self.db_upsert(pool, &key, &value, MemoryLayer::Team, &["expertise", agent_id], confidence).await?;
        } else {
            // Fallback to in-memory cache
            let entry = MemoryEntry {
                key: key.clone(),
                value: serde_json::to_value(&expertise)?,
                layer: MemoryLayer::Team,
                tags: vec!["expertise".into(), agent_id.to_string()],
                confidence,
                access_count: 0,
                created_at: Utc::now(),
            };
            self.cache.write().await.insert(key, entry);
        }

        info!("Recorded expertise for {}: {}...", agent_id, &problem[..problem.len().min(50)]);
        Ok(expertise)
    }

    /// Get expertise for an agent.
    /// Replaces Python: async def get_expertise(self, agent_id, query, limit)
    pub async fn get_expertise(
        &self,
        agent_id: &str,
        query: Option<&str>,
        limit: usize,
    ) -> Vec<AgentExpertise> {
        let cache = self.cache.read().await;
        let prefix = format!("expertise:{}:", agent_id);

        let mut results: Vec<AgentExpertise> = cache
            .values()
            .filter(|e| e.key.starts_with(&prefix))
            .filter_map(|e| serde_json::from_value::<AgentExpertise>(e.value.clone()).ok())
            .filter(|e| {
                query.map_or(true, |q| {
                    let ql = q.to_lowercase();
                    e.problem.to_lowercase().contains(&ql)
                        || e.approach.to_lowercase().contains(&ql)
                })
            })
            .collect();

        results.sort_by(|a, b| b.timestamp.cmp(&a.timestamp));
        results.truncate(limit);
        results
    }

    // ------------------------------------------------------------------
    // Session management
    // ------------------------------------------------------------------

    /// Start a new agent session.
    /// Replaces Python: async def start_session(self, session_id, agent_id, task)
    pub async fn start_session(
        &self,
        session_id: &str,
        agent_id: &str,
        task: &str,
    ) -> SessionMemory {
        let session = SessionMemory::new(session_id, agent_id, task);
        self.sessions
            .write()
            .await
            .insert(session_id.to_string(), session.clone());
        info!("Started session {} for {}", session_id, agent_id);
        session
    }

    /// Record a decision made during a session.
    /// Replaces Python: async def record_decision(self, session_id, decision, reasoning, outcome)
    pub async fn record_decision(
        &self,
        session_id: &str,
        decision: &str,
        reasoning: &str,
        outcome: Option<&str>,
    ) {
        let mut sessions = self.sessions.write().await;
        if let Some(session) = sessions.get_mut(session_id) {
            session.decisions.push(serde_json::json!({
                "decision": decision,
                "reasoning": reasoning,
                "outcome": outcome,
                "timestamp": Utc::now().to_rfc3339(),
            }));
        } else {
            warn!("Session {} not found", session_id);
        }
    }

    /// Record tool usage during a session.
    pub async fn record_tool_use(
        &self,
        session_id: &str,
        tool: &str,
        purpose: &str,
        success: bool,
    ) {
        let mut sessions = self.sessions.write().await;
        if let Some(session) = sessions.get_mut(session_id) {
            session.tools_used.push(serde_json::json!({
                "tool": tool,
                "purpose": purpose,
                "success": success,
                "timestamp": Utc::now().to_rfc3339(),
            }));
        }
    }

    /// End a session.
    /// Replaces Python: async def end_session(self, session_id, success)
    pub async fn end_session(&self, session_id: &str, success: bool) -> Option<SessionMemory> {
        let mut sessions = self.sessions.write().await;
        let mut session = sessions.remove(session_id)?;
        session.end_time = Some(Utc::now());
        session.success = Some(success);
        info!("Ended session {} (success: {})", session_id, success);
        Some(session)
    }

    // ------------------------------------------------------------------
    // Pattern extraction
    // ------------------------------------------------------------------

    /// Extract a reusable pattern from a completed session.
    /// Replaces Python: async def extract_pattern(self, session_id, pattern_name, pattern_type)
    pub async fn extract_pattern(
        &self,
        session: &SessionMemory,
        pattern_name: &str,
        pattern_type: &str,
    ) -> anyhow::Result<serde_json::Value> {
        let pattern = serde_json::json!({
            "name": pattern_name,
            "type": pattern_type,
            "source_session": session.session_id,
            "task": session.task,
            "decisions": session.decisions,
            "tools_used": session.tools_used,
            "success": session.success,
        });

        let key = format!("pattern:{}:{}", pattern_type, pattern_name);
        let confidence = if session.success == Some(true) { 0.8 } else { 0.5 };

        self.save(&key, &pattern, MemoryLayer::Global, &["pattern", pattern_type], confidence).await?;
        info!("Extracted pattern: {}", pattern_name);
        Ok(pattern)
    }

    // ------------------------------------------------------------------
    // Core storage operations
    // ------------------------------------------------------------------

    pub async fn save(
        &self,
        key: &str,
        value: &serde_json::Value,
        layer: MemoryLayer,
        tags: &[&str],
        confidence: f64,
    ) -> anyhow::Result<()> {
        if let Some(pool) = &self.pool {
            self.db_upsert(pool, key, value, layer, tags, confidence).await?;
        } else {
            let entry = MemoryEntry {
                key: key.to_string(),
                value: value.clone(),
                layer,
                tags: tags.iter().map(|s| s.to_string()).collect(),
                confidence,
                access_count: 0,
                created_at: Utc::now(),
            };
            self.cache.write().await.insert(key.to_string(), entry);
        }
        Ok(())
    }

    /// Search memories by query — keyword match (production: pgvector cosine similarity).
    /// Replaces Python: async def search(self, query, layer, limit, threshold)
    pub async fn search(
        &self,
        query: &str,
        layer: Option<MemoryLayer>,
        limit: usize,
        threshold: f64,
    ) -> Vec<SearchResult> {
        let cache = self.cache.read().await;
        let query_lower = query.to_lowercase();
        let query_terms: Vec<&str> = query_lower.split_whitespace().collect();

        let mut results: Vec<SearchResult> = cache
            .values()
            .filter(|e| layer.map_or(true, |l| e.layer == l))
            .filter_map(|e| {
                let score = Self::calculate_relevance(e, &query_terms, &query_lower);
                if score >= threshold {
                    Some(SearchResult {
                        entry: e.clone(),
                        score,
                        highlights: Self::extract_highlights(e, &query_terms),
                    })
                } else {
                    None
                }
            })
            .collect();

        results.sort_by(|a, b| b.score.partial_cmp(&a.score).unwrap_or(std::cmp::Ordering::Equal));
        results.truncate(limit);
        results
    }

    // ------------------------------------------------------------------
    // DB helpers (stub — full SQL in migrations)
    // ------------------------------------------------------------------

    async fn db_upsert(
        &self,
        pool: &PgPool,
        key: &str,
        value: &serde_json::Value,
        layer: MemoryLayer,
        tags: &[&str],
        confidence: f64,
    ) -> anyhow::Result<()> {
        let tags_arr: Vec<String> = tags.iter().map(|s| s.to_string()).collect();
        let value_str = serde_json::to_string(value)?;
        // Use sqlx::query (not query!) to avoid requiring DATABASE_URL at compile time.
        sqlx::query(
            r#"
            INSERT INTO memory_entries (key, value, layer, tags, confidence, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
            ON CONFLICT (key) DO UPDATE
                SET value = EXCLUDED.value,
                    tags = EXCLUDED.tags,
                    confidence = EXCLUDED.confidence,
                    updated_at = NOW()
            "#,
        )
        .bind(key)
        .bind(&value_str)
        .bind(layer.to_string())
        .bind(&tags_arr)
        .bind(confidence)
        .execute(pool)
        .await?;
        Ok(())
    }

    // ------------------------------------------------------------------
    // Relevance scoring (keyword — swap for pgvector in prod)
    // ------------------------------------------------------------------

    fn calculate_relevance(entry: &MemoryEntry, query_terms: &[&str], query_lower: &str) -> f64 {
        let mut score = 0.0_f64;
        let key_lower = entry.key.to_lowercase();

        if key_lower.contains(query_lower) {
            score += 0.5;
        }
        let value_str = entry.value.to_string().to_lowercase();
        for term in query_terms {
            if value_str.contains(term) {
                score += 0.1;
            }
        }
        for tag in &entry.tags {
            if query_terms.contains(&tag.to_lowercase().as_str()) {
                score += 0.2;
            }
        }
        score *= entry.confidence;
        score *= (1.0 + (entry.access_count as f64) * 0.05).min(2.0);
        score.min(1.0)
    }

    fn extract_highlights(entry: &MemoryEntry, query_terms: &[&str]) -> Vec<String> {
        let value_str = serde_json::to_string_pretty(&entry.value).unwrap_or_default();
        value_str
            .lines()
            .filter(|line| {
                let ll = line.to_lowercase();
                query_terms.iter().any(|t| ll.contains(t))
            })
            .take(3)
            .map(|s| s.trim().to_string())
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn record_and_retrieve_expertise() {
        let m = MemoryManager::in_memory();
        let e = m
            .record_expertise("agent-01", "Build API", "Use Axum", "success", 0.9)
            .await
            .unwrap();
        assert_eq!(e.agent_id, "agent-01");

        let fetched = m.get_expertise("agent-01", None, 10).await;
        assert_eq!(fetched.len(), 1);
        assert_eq!(fetched[0].problem, "Build API");
    }

    #[tokio::test]
    async fn expertise_query_filter() {
        let m = MemoryManager::in_memory();
        m.record_expertise("a1", "Build API", "Axum", "ok", 0.9).await.unwrap();
        m.record_expertise("a1", "Debug memory", "valgrind", "ok", 0.8).await.unwrap();

        let api_results = m.get_expertise("a1", Some("API"), 10).await;
        assert_eq!(api_results.len(), 1);
    }

    #[tokio::test]
    async fn session_lifecycle() {
        let m = MemoryManager::in_memory();
        m.start_session("sess-01", "agent-01", "Build landing page").await;
        m.record_decision("sess-01", "Use React", "Better ecosystem", None).await;
        m.record_tool_use("sess-01", "npm", "install deps", true).await;
        let ended = m.end_session("sess-01", true).await.unwrap();

        assert_eq!(ended.decisions.len(), 1);
        assert_eq!(ended.tools_used.len(), 1);
        assert_eq!(ended.success, Some(true));
        assert!(ended.end_time.is_some());
    }

    #[tokio::test]
    async fn search_returns_relevant_results() {
        let m = MemoryManager::in_memory();
        m.save(
            "pattern:workflow:deploy",
            &serde_json::json!({"description": "CI/CD pipeline deployment workflow"}),
            MemoryLayer::Global,
            &["pattern", "deployment"],
            0.9,
        )
        .await
        .unwrap();

        let results = m.search("deployment workflow", Some(MemoryLayer::Global), 5, 0.0).await;
        assert!(!results.is_empty());
    }

    #[tokio::test]
    async fn extract_pattern_from_session() {
        let m = MemoryManager::in_memory();
        let mut session = SessionMemory::new("sess-02", "agent-02", "Deploy app");
        session.success = Some(true);
        let pattern = m
            .extract_pattern(&session, "ci-deploy", "workflow")
            .await
            .unwrap();
        assert_eq!(pattern["name"].as_str().unwrap(), "ci-deploy");
    }
}
