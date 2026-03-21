/// Agent struct, AgentRegistry, and key agent facades.
/// Replaces: archonx/core/agents.py
///
/// All 64 agents are defined here — exact same IDs, names, positions,
/// and specialty strings as the Python source.
use std::collections::HashMap;
use std::sync::{Arc, RwLock};

use dashmap::DashMap;
use serde::{Deserialize, Serialize};
use tracing::info;

use crate::types::{AgentId, AgentStatus, Crew, Role};

// ---------------------------------------------------------------------------
// Agent struct
// ---------------------------------------------------------------------------

/// A single ArchonX agent.
/// Replaces Python: @dataclass class Agent
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Agent {
    pub agent_id: String, // String slug IDs preserved from Python for API compat
    pub name: String,
    pub role: Role,
    pub crew: Crew,
    pub position: String,   // Chess notation e.g. "D1"
    pub specialty: String,
    pub model: String,
    pub status: AgentStatus,
    pub health: f64,          // 0.0 – 1.0
    pub tasks_completed: u64,
    pub score: f64,
    pub skills: Vec<String>,
    pub reports_to: Option<String>,
    pub commands: Vec<String>,
    pub metadata: serde_json::Value,
    // Runtime-only fields (not in Python but needed for Axum responses)
    pub current_task: Option<String>,
    pub computer_id: Option<String>,
}

impl Agent {
    pub fn new(
        agent_id: impl Into<String>,
        name: impl Into<String>,
        role: Role,
        crew: Crew,
        position: impl Into<String>,
        specialty: impl Into<String>,
    ) -> Self {
        Self {
            agent_id: agent_id.into(),
            name: name.into(),
            role,
            crew,
            position: position.into(),
            specialty: specialty.into(),
            model: "anthropic/claude-sonnet-4-20250514".to_string(),
            status: AgentStatus::Idle,
            health: 1.0,
            tasks_completed: 0,
            score: 0.0,
            skills: Vec::new(),
            reports_to: None,
            commands: Vec::new(),
            metadata: serde_json::Value::Object(serde_json::Map::new()),
            current_task: None,
            computer_id: None,
        }
    }

    pub fn with_reports_to(mut self, superior: impl Into<String>) -> Self {
        self.reports_to = Some(superior.into());
        self
    }

    pub fn with_metadata(mut self, meta: serde_json::Value) -> Self {
        self.metadata = meta;
        self
    }

    pub fn activate(&mut self) {
        self.status = AgentStatus::Active;
    }

    pub fn deactivate(&mut self) {
        self.status = AgentStatus::Idle;
    }

    pub fn record_task(&mut self, points: f64) {
        self.tasks_completed += 1;
        self.score += points;
    }
}

// ---------------------------------------------------------------------------
// AgentRegistry — DashMap for lock-free concurrent reads
// ---------------------------------------------------------------------------

/// Central registry holding all 64 agents.
/// Uses DashMap<String, Arc<RwLock<Agent>>> for lock-free reads.
/// Replaces Python: class AgentRegistry
#[derive(Default)]
pub struct AgentRegistry {
    agents: DashMap<String, Arc<RwLock<Agent>>>,
}

impl AgentRegistry {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn register(&self, agent: Agent) -> anyhow::Result<()> {
        if self.agents.contains_key(&agent.agent_id) {
            return Err(anyhow::anyhow!("Duplicate agent_id: {}", agent.agent_id));
        }
        self.agents
            .insert(agent.agent_id.clone(), Arc::new(RwLock::new(agent)));
        Ok(())
    }

    pub fn get(&self, agent_id: &str) -> Option<Arc<RwLock<Agent>>> {
        self.agents.get(agent_id).map(|v| v.value().clone())
    }

    pub fn get_by_crew(&self, crew: Crew) -> Vec<Arc<RwLock<Agent>>> {
        self.agents
            .iter()
            .filter(|e| e.value().read().unwrap().crew == crew)
            .map(|e| e.value().clone())
            .collect()
    }

    pub fn get_by_role(&self, role: Role, crew: Option<Crew>) -> Vec<Arc<RwLock<Agent>>> {
        self.agents
            .iter()
            .filter(|e| {
                let a = e.value().read().unwrap();
                a.role == role && crew.map_or(true, |c| a.crew == c)
            })
            .map(|e| e.value().clone())
            .collect()
    }

    pub fn all(&self) -> Vec<Arc<RwLock<Agent>>> {
        self.agents.iter().map(|e| e.value().clone()).collect()
    }

    pub fn len(&self) -> usize {
        self.agents.len()
    }

    pub fn is_empty(&self) -> bool {
        self.agents.is_empty()
    }
}

// ---------------------------------------------------------------------------
// Agent Roster — all 64 agents, exact match with Python source
// ---------------------------------------------------------------------------

/// Build all 64 agents into the registry.
/// Replaces Python: def build_all_agents(registry)
pub fn build_all_agents(registry: &AgentRegistry) -> anyhow::Result<()> {
    for agent in all_agents() {
        registry.register(agent)?;
    }
    info!("Registered {} agents.", registry.len());
    Ok(())
}

fn all_agents() -> Vec<Agent> {
    let mut agents = Vec::with_capacity(64);
    agents.extend(white_back_rank());
    agents.extend(white_front_rank());
    agents.extend(white_extended());
    agents.extend(black_back_rank());
    agents.extend(black_front_rank());
    agents.extend(black_extended());
    agents
}

// --- White Crew Back Rank (8 agents) ---

fn white_back_rank() -> Vec<Agent> {
    vec![
        Agent::new("fortress_rook_white_a", "Fortress", Role::Rook, Crew::White, "A1", "Backend infrastructure")
            .with_reports_to("pauli_king_white"),
        Agent::new("blitz_knight_white_b", "Blitz", Role::Knight, Crew::White, "B1", "Rapid deployment")
            .with_reports_to("synthia_queen_white")
            .with_metadata(serde_json::json!({
                "lemonis_department": "People",
                "lemonis_pillar": 1,
                "department_mission": "Ensure right agents are aligned, accountable, and coachable. Run agent ACK cycles. Enforce crew culture and King Mode alignment."
            })),
        Agent::new("oracle_bishop_white_c", "Oracle", Role::Bishop, Crew::White, "C1", "Data analytics")
            .with_reports_to("synthia_queen_white"),
        Agent::new("synthia_queen_white", "Synthia", Role::Queen, Crew::White, "D1", "Tactical execution & coordination")
            .with_reports_to("pauli_king_white"),
        Agent::new("pauli_king_white", "Pauli", Role::King, Crew::White, "E1", "Strategic decisions"),
        Agent::new("sage_bishop_white_f", "Sage", Role::Bishop, Crew::White, "F1", "Knowledge management")
            .with_reports_to("synthia_queen_white"),
        Agent::new("patch_knight_white_g", "Patch", Role::Knight, Crew::White, "G1", "Hotfix repair")
            .with_reports_to("synthia_queen_white")
            .with_metadata(serde_json::json!({
                "lemonis_department": "Process",
                "lemonis_pillar": 2,
                "department_mission": "Own workflow documentation, PAULIWHEEL enforcement, ops reporting, loop management. Ensure nothing ships without verified process."
            })),
        Agent::new("sentinel_rook_white_h", "Sentinel", Role::Rook, Crew::White, "H1", "Security defense")
            .with_reports_to("pauli_king_white"),
    ]
}

// --- White Crew Front Rank / Pawns Row 2 (8 agents) ---

fn white_front_rank() -> Vec<Agent> {
    vec![
        Agent::new("scout_pawn_white_a", "Scout", Role::Pawn, Crew::White, "A2", "Reconnaissance (undercover)").with_reports_to("synthia_queen_white"),
        Agent::new("craft_pawn_white_b", "Craft", Role::Pawn, Crew::White, "B2", "Frontend development (undercover)").with_reports_to("synthia_queen_white"),
        Agent::new("quill_pawn_white_c", "Quill", Role::Pawn, Crew::White, "C2", "Content creation (undercover)").with_reports_to("synthia_queen_white"),
        Agent::new("lens_pawn_white_d", "Lens", Role::Pawn, Crew::White, "D2", "Visual design (undercover)").with_reports_to("synthia_queen_white"),
        Agent::new("cipher_pawn_white_e", "Cipher", Role::Pawn, Crew::White, "E2", "Encryption (undercover)").with_reports_to("synthia_queen_white"),
        Agent::new("pulse_pawn_white_f", "Pulse", Role::Pawn, Crew::White, "F2", "Performance monitoring (undercover)").with_reports_to("synthia_queen_white"),
        Agent::new("probe_pawn_white_g", "Probe", Role::Pawn, Crew::White, "G2", "Testing (undercover)").with_reports_to("synthia_queen_white"),
        Agent::new("link_pawn_white_h", "Link", Role::Pawn, Crew::White, "H2", "API integration (undercover)").with_reports_to("synthia_queen_white"),
    ]
}

// --- White Extended Rows 3-4 (16 agents) ---

fn white_extended() -> Vec<Agent> {
    let specs: &[(&str, &str, &str, &str)] = &[
        ("relay_pawn_white_a3", "Relay", "A3", "Message routing"),
        ("forge_pawn_white_b3", "Forge", "B3", "Code generation"),
        ("compass_pawn_white_c3", "Compass", "C3", "Navigation & search"),
        ("anvil_pawn_white_d3", "Anvil", "D3", "Build pipelines"),
        ("ember_pawn_white_e3", "Ember", "E3", "Incident response"),
        ("weave_pawn_white_f3", "Weave", "F3", "Workflow orchestration"),
        ("flint_pawn_white_g3", "Flint", "G3", "Alerting & notifications"),
        ("tide_pawn_white_h3", "Tide", "H3", "Data streaming"),
        ("ark_pawn_white_a4", "Ark", "A4", "Backup & recovery"),
        ("bolt_pawn_white_b4", "Bolt", "B4", "Speed optimisation"),
        ("crest_pawn_white_c4", "Crest", "C4", "Branding & identity"),
        ("drift_pawn_white_d4", "Drift", "D4", "A/B testing"),
        ("echo_pawn_white_e4", "Echo", "E4", "Logging & audit trail"),
        ("fuse_pawn_white_f4", "Fuse", "F4", "Integration middleware"),
        ("grip_pawn_white_g4", "Grip", "G4", "Access control"),
        ("haven_pawn_white_h4", "Haven", "H4", "Compliance & governance"),
    ];
    specs
        .iter()
        .map(|(id, name, pos, spec)| {
            Agent::new(*id, *name, Role::Pawn, Crew::White, *pos, *spec)
                .with_reports_to("synthia_queen_white")
        })
        .collect()
}

// --- Black Crew Back Rank (8 agents) ---

fn black_back_rank() -> Vec<Agent> {
    vec![
        Agent::new("bastion_rook_black_a", "Bastion", Role::Rook, Crew::Black, "A8", "Backend infrastructure")
            .with_reports_to("mirror_king_black"),
        Agent::new("flash_knight_black_b", "Flash", Role::Knight, Crew::Black, "B8", "Rapid deployment")
            .with_reports_to("shadow_queen_black")
            .with_metadata(serde_json::json!({
                "lemonis_department": "Product",
                "lemonis_pillar": 3,
                "department_mission": "Evaluate product quality, SKU logic, margin analysis, and feature gate decisions. Ensure what's built is differentiated and market-worthy."
            })),
        Agent::new("seer_bishop_black_c", "Seer", Role::Bishop, Crew::Black, "C8", "Data analytics")
            .with_reports_to("shadow_queen_black"),
        Agent::new("shadow_queen_black", "Shadow", Role::Queen, Crew::Black, "D8", "Tactical execution & coordination")
            .with_reports_to("mirror_king_black"),
        Agent::new("mirror_king_black", "Mirror", Role::King, Crew::Black, "E8", "Strategic decisions"),
        Agent::new("mystic_bishop_black_f", "Mystic", Role::Bishop, Crew::Black, "F8", "Knowledge management")
            .with_reports_to("shadow_queen_black"),
        Agent::new("glitch_knight_black_g", "Glitch", Role::Knight, Crew::Black, "G8", "Hotfix repair")
            .with_reports_to("shadow_queen_black")
            .with_metadata(serde_json::json!({
                "lemonis_department": "Gratitude",
                "lemonis_pillar": 4,
                "department_mission": "Operate BENEVOLENCIA™ social purpose initiatives. Embed gratitude and social impact into every transaction. Business with soul.",
                "brand": "BENEVOLENCIA™",
                "visual": {"color": "gold", "hex": "#F5A623", "glow": "warm", "particle": "dove_heart"}
            })),
        Agent::new("warden_rook_black_h", "Warden", Role::Rook, Crew::Black, "H8", "Security defense")
            .with_reports_to("mirror_king_black"),
    ]
}

// --- Black Crew Front Rank / Pawns Row 7 (8 agents) ---

fn black_front_rank() -> Vec<Agent> {
    vec![
        Agent::new("shade_pawn_black_a", "Shade", Role::Pawn, Crew::Black, "A7", "Reconnaissance (undercover)").with_reports_to("shadow_queen_black"),
        Agent::new("pixel_pawn_black_b", "Pixel", Role::Pawn, Crew::Black, "B7", "Frontend development (undercover)").with_reports_to("shadow_queen_black"),
        Agent::new("inker_pawn_black_c", "Inker", Role::Pawn, Crew::Black, "C7", "Content creation (undercover)").with_reports_to("shadow_queen_black"),
        Agent::new("prism_pawn_black_d", "Prism", Role::Pawn, Crew::Black, "D7", "Visual design (undercover)").with_reports_to("shadow_queen_black"),
        Agent::new("vault_pawn_black_e", "Vault", Role::Pawn, Crew::Black, "E7", "Encryption (undercover)").with_reports_to("shadow_queen_black"),
        Agent::new("surge_pawn_black_f", "Surge", Role::Pawn, Crew::Black, "F7", "Performance monitoring (undercover)").with_reports_to("shadow_queen_black"),
        Agent::new("trace_pawn_black_g", "Trace", Role::Pawn, Crew::Black, "G7", "Testing (undercover)").with_reports_to("shadow_queen_black"),
        Agent::new("nexus_pawn_black_h", "Nexus", Role::Pawn, Crew::Black, "H7", "API integration (undercover)").with_reports_to("shadow_queen_black"),
    ]
}

// --- Black Extended Rows 5-6 (16 agents) ---

fn black_extended() -> Vec<Agent> {
    let specs: &[(&str, &str, &str, &str)] = &[
        ("signal_pawn_black_a6", "Signal", "A6", "Message routing"),
        ("alloy_pawn_black_b6", "Alloy", "B6", "Code generation"),
        ("beacon_pawn_black_c6", "Beacon", "C6", "Navigation & search"),
        ("hammer_pawn_black_d6", "Hammer", "D6", "Build pipelines"),
        ("spark_pawn_black_e6", "Spark", "E6", "Incident response"),
        ("loom_pawn_black_f6", "Loom", "F6", "Workflow orchestration"),
        ("siren_pawn_black_g6", "Siren", "G6", "Alerting & notifications"),
        ("current_pawn_black_h6", "Current", "H6", "Data streaming"),
        ("vault2_pawn_black_a5", "Bunker", "A5", "Backup & recovery"),
        ("dash_pawn_black_b5", "Dash", "B5", "Speed optimisation"),
        ("emblem_pawn_black_c5", "Emblem", "C5", "Branding & identity"),
        ("split_pawn_black_d5", "Split", "D5", "A/B testing"),
        ("ledger_pawn_black_e5", "Ledger", "E5", "Logging & audit trail"),
        ("bridge_pawn_black_f5", "Bridge", "F5", "Integration middleware"),
        ("lock_pawn_black_g5", "Lock", "G5", "Access control"),
        ("shield_pawn_black_h5", "Shield", "H5", "Compliance & governance"),
    ];
    specs
        .iter()
        .map(|(id, name, pos, spec)| {
            Agent::new(*id, *name, Role::Pawn, Crew::Black, *pos, *spec)
                .with_reports_to("shadow_queen_black")
        })
        .collect()
}

// ---------------------------------------------------------------------------
// Convenience facades
// ---------------------------------------------------------------------------

/// Facade for Synthia (White Queen / Agent Zero).
/// Replaces Python: class SynthiaQueen
pub struct SynthiaQueen;

impl SynthiaQueen {
    /// Get and activate the Synthia agent from the registry.
    pub fn initialize(registry: &AgentRegistry) -> anyhow::Result<Arc<RwLock<Agent>>> {
        let arc = registry
            .get("synthia_queen_white")
            .ok_or_else(|| anyhow::anyhow!("Synthia not found in registry"))?;
        arc.write().unwrap().activate();
        info!("Synthia (White Queen) initialized at D1");
        Ok(arc)
    }
}

/// Facade for Pauli (White King).
/// Replaces Python: class PauliKing
pub struct PauliKing;

impl PauliKing {
    pub fn initialize(registry: &AgentRegistry) -> anyhow::Result<Arc<RwLock<Agent>>> {
        let arc = registry
            .get("pauli_king_white")
            .ok_or_else(|| anyhow::anyhow!("Pauli not found in registry"))?;
        arc.write().unwrap().activate();
        info!("Pauli (White King) initialized at E1");
        Ok(arc)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn make_registry() -> AgentRegistry {
        let r = AgentRegistry::new();
        build_all_agents(&r).expect("build failed");
        r
    }

    #[test]
    fn build_all_agents_produces_64() {
        let r = make_registry();
        assert_eq!(r.len(), 64, "Expected exactly 64 agents, got {}", r.len());
    }

    #[test]
    fn get_by_crew_white_is_32() {
        let r = make_registry();
        assert_eq!(r.get_by_crew(Crew::White).len(), 32);
    }

    #[test]
    fn get_by_crew_black_is_32() {
        let r = make_registry();
        assert_eq!(r.get_by_crew(Crew::Black).len(), 32);
    }

    #[test]
    fn get_by_role_kings() {
        let r = make_registry();
        let kings = r.get_by_role(Role::King, None);
        assert_eq!(kings.len(), 2, "Expected 2 kings (White + Black)");
    }

    #[test]
    fn get_by_role_queens_crew_filter() {
        let r = make_registry();
        let wq = r.get_by_role(Role::Queen, Some(Crew::White));
        assert_eq!(wq.len(), 1);
        assert_eq!(wq[0].read().unwrap().agent_id, "synthia_queen_white");
    }

    #[test]
    fn no_duplicate_agent_ids() {
        let all = all_agents();
        let mut seen = std::collections::HashSet::new();
        for a in &all {
            assert!(seen.insert(a.agent_id.clone()), "Duplicate: {}", a.agent_id);
        }
    }

    #[test]
    fn synthia_facade_initializes() {
        let r = make_registry();
        let arc = SynthiaQueen::initialize(&r).unwrap();
        assert_eq!(arc.read().unwrap().status, AgentStatus::Active);
    }

    #[test]
    fn duplicate_registration_fails() {
        let r = AgentRegistry::new();
        let a = Agent::new("dup_test", "Test", Role::Pawn, Crew::White, "A1", "test");
        r.register(a.clone()).unwrap();
        assert!(r.register(a).is_err());
    }
}
