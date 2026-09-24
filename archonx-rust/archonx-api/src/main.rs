/// archonx-api binary — Axum HTTP server replacing Python FastAPI.
///
/// Serves:
///   GET /healthz          → { ok: bool }
///   GET /api/agents       → { data: Agent[] }
///   GET /api/approvals    → { data: Approval[] }
///
/// Default port: 8000 (matches Python uvicorn default).
/// Override with API_PORT env var.
use std::net::SocketAddr;

use axum::routing::get;
use axum::Router;
use tower_http::cors::CorsLayer;
use tower_http::trace::TraceLayer;
use tracing_subscriber::EnvFilter;

mod routes;
use routes::{AppState, get_agents, get_approvals, healthz};

#[tokio::main]
async fn main() {
    // Initialize tracing — RUST_LOG=info by default
    tracing_subscriber::fmt()
        .with_env_filter(
            EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info")),
        )
        .init();

    let port: u16 = std::env::var("API_PORT")
        .ok()
        .and_then(|p| p.parse().ok())
        .unwrap_or(8000);

    let addr = SocketAddr::from(([0, 0, 0, 0], port));

    // Initialize application state — loads all 64 agents
    let state = AppState::new();

    let app = Router::new()
        .route("/healthz", get(healthz))
        .route("/api/agents", get(get_agents))
        .route("/api/approvals", get(get_approvals))
        // CORS — allow all origins for Next.js frontend on localhost:3000
        .layer(CorsLayer::permissive())
        // Request tracing
        .layer(TraceLayer::new_for_http())
        .with_state(state);

    tracing::info!("archonx-api listening on http://{}", addr);

    let listener = tokio::net::TcpListener::bind(addr)
        .await
        .expect("Failed to bind TCP listener");

    axum::serve(listener, app)
        .await
        .expect("Server error");
}
