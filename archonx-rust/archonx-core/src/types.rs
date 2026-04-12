/// Core shared types used across all ArchonX crates.
/// Replaces Python enums and dataclasses from archonx/core/agents.py
/// and archonx/core/flywheel.py.
use serde::{Deserialize, Serialize};
use uuid::Uuid;

// ---------------------------------------------------------------------------
// Newtype ID wrappers — prevent mixing up AgentId with TaskId at compile time
// ---------------------------------------------------------------------------

/// Unique identifier for an agent. Newtype over Uuid.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(transparent)]
pub struct AgentId(pub Uuid);

impl AgentId {
    pub fn new() -> Self {
        Self(Uuid::new_v4())
    }

    pub fn from_str(s: &str) -> Option<Self> {
        Uuid::parse_str(s).ok().map(Self)
    }
}

impl Default for AgentId {
    fn default() -> Self {
        Self::new()
    }
}

impl std::fmt::Display for AgentId {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

/// Unique identifier for a task. Newtype over Uuid.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(transparent)]
pub struct TaskId(pub Uuid);

impl TaskId {
    pub fn new() -> Self {
        Self(Uuid::new_v4())
    }
}

impl Default for TaskId {
    fn default() -> Self {
        Self::new()
    }
}

impl std::fmt::Display for TaskId {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

// ---------------------------------------------------------------------------
// Crew — which side of the board
// ---------------------------------------------------------------------------

/// The two crews in the ArchonX swarm.
/// Replaces Python: class Crew(str, Enum): WHITE = "white" / BLACK = "black"
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Crew {
    White,
    Black,
}

impl std::fmt::Display for Crew {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Crew::White => write!(f, "white"),
            Crew::Black => write!(f, "black"),
        }
    }
}

impl std::str::FromStr for Crew {
    type Err = anyhow::Error;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "white" => Ok(Crew::White),
            "black" => Ok(Crew::Black),
            other => Err(anyhow::anyhow!("Unknown crew: {}", other)),
        }
    }
}

// ---------------------------------------------------------------------------
// Role — chess-piece role
// ---------------------------------------------------------------------------

/// Agent roles corresponding to chess pieces.
/// Replaces Python: class Role(str, Enum)
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Role {
    King,
    Queen,
    Rook,
    Knight,
    Bishop,
    Pawn,
}

impl std::fmt::Display for Role {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let s = match self {
            Role::King => "king",
            Role::Queen => "queen",
            Role::Rook => "rook",
            Role::Knight => "knight",
            Role::Bishop => "bishop",
            Role::Pawn => "pawn",
        };
        write!(f, "{}", s)
    }
}

impl std::str::FromStr for Role {
    type Err = anyhow::Error;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "king" => Ok(Role::King),
            "queen" => Ok(Role::Queen),
            "rook" => Ok(Role::Rook),
            "knight" => Ok(Role::Knight),
            "bishop" => Ok(Role::Bishop),
            "pawn" => Ok(Role::Pawn),
            other => Err(anyhow::anyhow!("Unknown role: {}", other)),
        }
    }
}

// ---------------------------------------------------------------------------
// AgentStatus
// ---------------------------------------------------------------------------

/// Lifecycle status of an agent.
/// Replaces Python: class AgentStatus(str, Enum)
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize, Default)]
#[serde(rename_all = "lowercase")]
pub enum AgentStatus {
    #[default]
    Idle,
    Active,
    Busy,
    Error,
    Offline,
}

impl std::fmt::Display for AgentStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let s = match self {
            AgentStatus::Idle => "idle",
            AgentStatus::Active => "active",
            AgentStatus::Busy => "busy",
            AgentStatus::Error => "error",
            AgentStatus::Offline => "offline",
        };
        write!(f, "{}", s)
    }
}

// ---------------------------------------------------------------------------
// ImprovementPriority
// ---------------------------------------------------------------------------

/// Priority levels for flywheel improvements.
/// Replaces Python: class ImprovementPriority(str, Enum)
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize, Default)]
#[serde(rename_all = "lowercase")]
pub enum ImprovementPriority {
    Critical, // Blocks revenue / security
    High,     // Enables new capability
    #[default]
    Medium, // Performance / UX
    Low,      // Nice-to-have
}

impl ImprovementPriority {
    /// Numeric weight for priority × effort scoring.
    pub fn weight(self) -> u32 {
        match self {
            ImprovementPriority::Critical => 4,
            ImprovementPriority::High => 3,
            ImprovementPriority::Medium => 2,
            ImprovementPriority::Low => 1,
        }
    }
}

impl std::fmt::Display for ImprovementPriority {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let s = match self {
            ImprovementPriority::Critical => "critical",
            ImprovementPriority::High => "high",
            ImprovementPriority::Medium => "medium",
            ImprovementPriority::Low => "low",
        };
        write!(f, "{}", s)
    }
}

impl std::str::FromStr for ImprovementPriority {
    type Err = anyhow::Error;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "critical" => Ok(ImprovementPriority::Critical),
            "high" => Ok(ImprovementPriority::High),
            "medium" => Ok(ImprovementPriority::Medium),
            "low" => Ok(ImprovementPriority::Low),
            other => Err(anyhow::anyhow!("Unknown priority: {}", other)),
        }
    }
}

// ---------------------------------------------------------------------------
// TaskType
// ---------------------------------------------------------------------------

/// Types of tasks the orchestrator can create.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize, Default)]
#[serde(rename_all = "lowercase")]
pub enum TaskType {
    #[default]
    Code,
    Review,
    Deploy,
    Test,
    Analysis,
    Security,
    Documentation,
    Integration,
    Optimization,
    Custom,
}

impl std::fmt::Display for TaskType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let s = match self {
            TaskType::Code => "code",
            TaskType::Review => "review",
            TaskType::Deploy => "deploy",
            TaskType::Test => "test",
            TaskType::Analysis => "analysis",
            TaskType::Security => "security",
            TaskType::Documentation => "documentation",
            TaskType::Integration => "integration",
            TaskType::Optimization => "optimization",
            TaskType::Custom => "custom",
        };
        write!(f, "{}", s)
    }
}

// ---------------------------------------------------------------------------
// TaskStatus
// ---------------------------------------------------------------------------

/// Lifecycle status of a task.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize, Default)]
#[serde(rename_all = "snake_case")]
pub enum TaskStatus {
    #[default]
    Pending,
    Implementing,
    InReview,
    Paused,
    Completed,
    Failed,
}

impl std::fmt::Display for TaskStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let s = match self {
            TaskStatus::Pending => "pending",
            TaskStatus::Implementing => "implementing",
            TaskStatus::InReview => "in_review",
            TaskStatus::Paused => "paused",
            TaskStatus::Completed => "completed",
            TaskStatus::Failed => "failed",
        };
        write!(f, "{}", s)
    }
}

// ---------------------------------------------------------------------------
// TaskPriority
// ---------------------------------------------------------------------------

/// Priority of a task.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize, Default)]
#[serde(rename_all = "lowercase")]
pub enum TaskPriority {
    Low,
    #[default]
    Normal,
    High,
    Critical,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn agent_id_roundtrip() {
        let id = AgentId::new();
        let s = id.to_string();
        let id2 = AgentId(Uuid::parse_str(&s).unwrap());
        assert_eq!(id, id2);
    }

    #[test]
    fn crew_display_and_parse() {
        assert_eq!(Crew::White.to_string(), "white");
        assert_eq!(Crew::Black.to_string(), "black");
        assert_eq!("white".parse::<Crew>().unwrap(), Crew::White);
    }

    #[test]
    fn role_display_and_parse() {
        for (role, s) in [
            (Role::King, "king"),
            (Role::Queen, "queen"),
            (Role::Rook, "rook"),
            (Role::Knight, "knight"),
            (Role::Bishop, "bishop"),
            (Role::Pawn, "pawn"),
        ] {
            assert_eq!(role.to_string(), s);
            assert_eq!(s.parse::<Role>().unwrap(), role);
        }
    }

    #[test]
    fn improvement_priority_weights() {
        assert_eq!(ImprovementPriority::Critical.weight(), 4);
        assert_eq!(ImprovementPriority::High.weight(), 3);
        assert_eq!(ImprovementPriority::Medium.weight(), 2);
        assert_eq!(ImprovementPriority::Low.weight(), 1);
    }

    #[test]
    fn serde_agent_status() {
        let s = serde_json::to_string(&AgentStatus::Active).unwrap();
        assert_eq!(s, r#""active""#);
        let d: AgentStatus = serde_json::from_str(&s).unwrap();
        assert_eq!(d, AgentStatus::Active);
    }
}
