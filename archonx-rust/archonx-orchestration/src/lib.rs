//! archonx-orchestration — agent orchestration and wave-based swarm deployment.
//!
//! Exposes:
//! - [`orchestrator::Orchestrator`] / [`orchestrator::get_orchestrator`] — singleton task dispatcher
//! - [`orchestrator::OrchestratorCommand`], [`orchestrator::OrchestratorResult`], [`orchestrator::Task`], [`orchestrator::TaskManager`]
//! - [`swarm::SwarmOrchestrator`] / [`swarm::WaveResult`] — parallel wave execution via `JoinSet`

pub mod orchestrator;
pub mod swarm;

pub use orchestrator::{
    Orchestrator, OrchestratorCommand, OrchestratorResult, Task, TaskManager, get_orchestrator,
};
pub use swarm::{SwarmOrchestrator, WaveResult};
