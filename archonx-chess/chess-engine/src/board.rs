/// Board state — 8×8 grid of optional pieces.
///
/// [SYNTHIA] STK: BoardState (64 squares, indexed [file][rank])
///           FLW: move application — O(1) square update
///           FBK: validation loop — illegal moves return Err

use serde::{Deserialize, Serialize};

use crate::agents::{AgentPiece, AGENT_ROSTER};

// ---------------------------------------------------------------------------
// Square address
// ---------------------------------------------------------------------------

/// A board square (file 0-7 = a-h, rank 0-7 = 1-8).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Square {
    pub file: u8,
    pub rank: u8,
}

impl Square {
    pub fn new(file: u8, rank: u8) -> Self {
        assert!(file < 8 && rank < 8, "Square ({},{}) out of bounds", file, rank);
        Self { file, rank }
    }

    /// Algebraic notation: "e4"
    pub fn to_algebraic(self) -> String {
        let file_char = (b'a' + self.file) as char;
        format!("{}{}", file_char, self.rank + 1)
    }

    pub fn from_algebraic(s: &str) -> Option<Self> {
        let bytes = s.as_bytes();
        if bytes.len() < 2 {
            return None;
        }
        let file = bytes[0].checked_sub(b'a')? ;
        let rank = bytes[1].checked_sub(b'1')?;
        if file < 8 && rank < 8 {
            Some(Self { file, rank })
        } else {
            None
        }
    }
}

impl std::fmt::Display for Square {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.to_algebraic())
    }
}

// ---------------------------------------------------------------------------
// Board state
// ---------------------------------------------------------------------------

/// Index into AGENT_ROSTER.  `None` means the square is empty.
pub type PieceIndex = u8;

/// 8×8 board — `board[file][rank]` = PieceIndex.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BoardState {
    /// board[file][rank] — MAX = empty
    grid: [[Option<PieceIndex>; 8]; 8],
    pub half_moves: u32,
    pub full_moves: u32,
    pub active_agent: Option<String>,
}

impl Default for BoardState {
    fn default() -> Self {
        Self::initial()
    }
}

impl BoardState {
    /// Starting position — all pieces at initial squares.
    pub fn initial() -> Self {
        let mut grid = [[None; 8]; 8];
        for (idx, piece) in AGENT_ROSTER.iter().enumerate() {
            grid[piece.start_file as usize][piece.start_rank as usize] =
                Some(idx as PieceIndex);
        }
        Self {
            grid,
            half_moves: 0,
            full_moves: 1,
            active_agent: None,
        }
    }

    /// Get piece at square.
    pub fn at(&self, sq: Square) -> Option<&AgentPiece> {
        self.grid[sq.file as usize][sq.rank as usize]
            .map(|idx| &AGENT_ROSTER[idx as usize])
    }

    /// True if square is occupied.
    pub fn is_occupied(&self, sq: Square) -> bool {
        self.grid[sq.file as usize][sq.rank as usize].is_some()
    }

    /// Apply a move (no legality check — caller is responsible).
    /// Returns the captured piece index if any.
    pub fn apply_move(&mut self, from: Square, to: Square) -> Option<PieceIndex> {
        let piece_idx = self.grid[from.file as usize][from.rank as usize].take();
        let captured = self.grid[to.file as usize][to.rank as usize].take();
        self.grid[to.file as usize][to.rank as usize] = piece_idx;
        if let Some(idx) = piece_idx {
            self.active_agent = Some(AGENT_ROSTER[idx as usize].agent_id.to_string());
        }
        self.half_moves += 1;
        captured
    }

    /// Clear a square (remove whatever piece is on it).
    /// Used for en passant capture cleanup.
    pub fn clear_square(&mut self, sq: Square) {
        self.grid[sq.file as usize][sq.rank as usize] = None;
    }

    /// All occupied squares with their piece references.
    pub fn pieces(&self) -> Vec<(Square, &AgentPiece)> {
        let mut result = Vec::with_capacity(32);
        for file in 0u8..8 {
            for rank in 0u8..8 {
                if let Some(idx) = self.grid[file as usize][rank as usize] {
                    result.push((Square::new(file, rank), &AGENT_ROSTER[idx as usize]));
                }
            }
        }
        result
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn initial_board_has_32_pieces() {
        let board = BoardState::initial();
        assert_eq!(board.pieces().len(), 32);
    }

    #[test]
    fn algebraic_roundtrip() {
        let sq = Square::new(4, 3); // e4
        assert_eq!(sq.to_algebraic(), "e4");
        assert_eq!(Square::from_algebraic("e4"), Some(sq));
    }

    #[test]
    fn move_application() {
        let mut board = BoardState::initial();
        // Move white pawn-2 (worker-001) from a2 to a4
        let from = Square::new(0, 1);
        let to = Square::new(0, 3);
        let captured = board.apply_move(from, to);
        assert!(captured.is_none());
        assert!(board.at(from).is_none());
        assert!(board.at(to).is_some());
    }
}
