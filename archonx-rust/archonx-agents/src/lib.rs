/// archonx-agents — agent persona traits and router.
///
/// Re-exports archonx-core agent types and adds:
/// - AgentPersona trait: step() for per-agent behavior
/// - AgentRouter: dispatch tasks to agents by role
pub mod persona;
pub mod router;

pub use persona::AgentPersona;
pub use router::AgentRouter;
