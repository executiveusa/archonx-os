/// Axum route handlers — exact API contract match with Python FastAPI.
///
/// Frontend contract (from archonx-synthia/apps/control-tower/src/app/page.tsx):
///   GET /healthz          → { ok: bool }
///   GET /api/agents       → { data: Agent[] }
///   GET /api/approvals    → { data: Approval[] }
///
/// Agent:   { agent_id, status, current_task, computer_id }
/// Approval:{ approval_id, action, context, status }
use std::sync::Arc;

use axum::{extract::State, Json};
use serde::{Deserialize, Serialize};

use archonx_core::agent::AgentRegistry;
use archonx_billing::TokenMeter;

// ---------------------------------------------------------------------------
// Shared application state
// ---------------------------------------------------------------------------

#[derive(Clone)]
pub struct AppState {
    pub registry: Arc<AgentRegistry>,
    pub meter: Arc<TokenMeter>,
    /// In-memory approvals store (replaces Python list-based pending_approvals)
    pub approvals: Arc<dashmap::DashMap<String, Approval>>,
}

impl AppState {
    pub fn new() -> Self {
        let registry = Arc::new(AgentRegistry::new());
        archonx_core::agent::build_all_agents(&registry)
            .expect("Failed to build agent registry");

        Self {
            registry,
            meter: Arc::new(TokenMeter::new()),
            approvals: Arc::new(dashmap::DashMap::new()),
        }
    }
}

// ---------------------------------------------------------------------------
// Response types — exact match with TypeScript interface in page.tsx
// ---------------------------------------------------------------------------

/// Agent response shape — matches TypeScript Agent interface.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentResponse {
    pub agent_id: String,
    pub status: String,
    pub current_task: Option<String>,
    pub computer_id: Option<String>,
}

/// Approval response shape — matches TypeScript Approval interface.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Approval {
    pub approval_id: String,
    pub action: String,
    pub context: String,
    pub status: String,
}

#[derive(Debug, Serialize)]
pub struct ListResponse<T> {
    pub data: Vec<T>,
}

#[derive(Debug, Serialize)]
pub struct HealthResponse {
    pub ok: bool,
}

// ---------------------------------------------------------------------------
// GET /healthz
// ---------------------------------------------------------------------------

pub async fn healthz() -> Json<HealthResponse> {
    Json(HealthResponse { ok: true })
}

// ---------------------------------------------------------------------------
// GET /api/agents
// ---------------------------------------------------------------------------

/// Returns all 64 agents with their current status and task.
/// Replaces Python: GET /api/agents → { data: Agent[] }
pub async fn get_agents(State(state): State<AppState>) -> Json<ListResponse<AgentResponse>> {
    let agents: Vec<AgentResponse> = state
        .registry
        .all()
        .into_iter()
        .map(|arc| {
            let a = arc.read().unwrap();
            AgentResponse {
                agent_id: a.agent_id.clone(),
                status: a.status.to_string(),
                current_task: a.current_task.clone(),
                computer_id: a.computer_id.clone(),
            }
        })
        .collect();

    Json(ListResponse { data: agents })
}

// ---------------------------------------------------------------------------
// GET /api/approvals
// ---------------------------------------------------------------------------

/// Returns pending approvals.
/// Replaces Python: GET /api/approvals → { data: Approval[] }
pub async fn get_approvals(State(state): State<AppState>) -> Json<ListResponse<Approval>> {
    let approvals: Vec<Approval> = state
        .approvals
        .iter()
        .map(|entry| entry.value().clone())
        .collect();

    Json(ListResponse { data: approvals })
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use axum::body::Body;
    use axum::http::{Request, StatusCode};
    use axum::Router;
    use tower::ServiceExt; // tower 0.4 ServiceExt for .oneshot()

    fn app() -> Router {
        use axum::routing::get;
        use tower_http::cors::CorsLayer;

        let state = AppState::new();
        Router::new()
            .route("/healthz", get(healthz))
            .route("/api/agents", get(get_agents))
            .route("/api/approvals", get(get_approvals))
            .layer(CorsLayer::permissive())
            .with_state(state)
    }

    async fn body_bytes(body: Body) -> bytes::Bytes {
        use http_body_util::BodyExt;
        body.collect().await.unwrap().to_bytes()
    }

    #[tokio::test]
    async fn healthz_returns_ok() {
        let app = app();
        let resp = app
            .oneshot(Request::builder().uri("/healthz").body(Body::empty()).unwrap())
            .await
            .unwrap();
        assert_eq!(resp.status(), StatusCode::OK);
        let body = body_bytes(resp.into_body()).await;
        let json: serde_json::Value = serde_json::from_slice(&body).unwrap();
        assert_eq!(json["ok"], true);
    }

    #[tokio::test]
    async fn get_agents_returns_64() {
        let app = app();
        let resp = app
            .oneshot(Request::builder().uri("/api/agents").body(Body::empty()).unwrap())
            .await
            .unwrap();
        assert_eq!(resp.status(), StatusCode::OK);
        let body = body_bytes(resp.into_body()).await;
        let json: serde_json::Value = serde_json::from_slice(&body).unwrap();
        let data = json["data"].as_array().unwrap();
        assert_eq!(data.len(), 64, "Expected 64 agents");
    }

    #[tokio::test]
    async fn agent_response_has_required_fields() {
        let app = app();
        let resp = app
            .oneshot(Request::builder().uri("/api/agents").body(Body::empty()).unwrap())
            .await
            .unwrap();
        let body = body_bytes(resp.into_body()).await;
        let json: serde_json::Value = serde_json::from_slice(&body).unwrap();
        let agent = &json["data"][0];
        assert!(agent["agent_id"].is_string(), "agent_id should be string");
        assert!(agent["status"].is_string(), "status should be string");
        // current_task and computer_id can be null
    }

    #[tokio::test]
    async fn get_approvals_returns_empty_list() {
        let app = app();
        let resp = app
            .oneshot(Request::builder().uri("/api/approvals").body(Body::empty()).unwrap())
            .await
            .unwrap();
        assert_eq!(resp.status(), StatusCode::OK);
        let body = body_bytes(resp.into_body()).await;
        let json: serde_json::Value = serde_json::from_slice(&body).unwrap();
        assert!(json["data"].is_array());
    }
}
