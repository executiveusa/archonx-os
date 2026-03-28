/// chess-engine — ArchonX agent chess board; core domain logic.
///
/// [SYNTHIA] STK: AgentPiece, BoardState, MoveHistory
///           FLW: move pipeline — bounded Vec (max 500 entries)
///           FBK: position validation loop
///           SEC: no external I/O; pure deterministic logic
pub mod agents;
pub mod board;
pub mod moves;
pub mod validation;

pub use agents::{AgentPiece, AgentRole, Crew, PieceColor, AGENT_ROSTER};
pub use board::{BoardState, Square};
pub use moves::{AgentMove, MoveResult, MoveType, Narration, execute_move};
pub use validation::{
    apply_legal_move, is_checkmate, is_in_check, is_legal_move, is_stalemate, legal_moves,
    CastlingRights, GameState, MoveKind, MoveOutcome,
};
