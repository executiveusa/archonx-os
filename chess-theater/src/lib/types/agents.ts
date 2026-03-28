// Chess Theater — Agent type definitions
// Maps to AGENT_ROSTER in archonx-chess/chess-engine/src/agents.rs

export type PieceType = 'king' | 'queen' | 'rook' | 'bishop' | 'knight' | 'pawn'
export type Crew = 'white' | 'black'

export interface AgentPiece {
  agentId: string
  pieceType: PieceType
  crew: Crew
  square: string        // algebraic notation e.g. "e1"
  color: string         // hex color for material
  label?: string        // display name
}

export type ActionType =
  | 'move'
  | 'execute_task'
  | 'debate'
  | 'consensus'
  | 'escalate'
  | 'block'
  | 'commit'
  | 'deploy'
  | 'idle'

export type PieceAnimState = 'idle' | 'thinking' | 'moving' | 'active' | 'done' | 'error'

export interface PieceRenderState {
  agentId: string
  square: string
  animState: PieceAnimState
  targetSquare?: string     // set when moving
}

export interface BoardState {
  pieces: PieceRenderState[]
  activeAgent: string | null
  lastAction: LastAction | null
  timestamp: string
}

export interface LastAction {
  agentId: string
  actionType: ActionType
  fromSquare: string | null
  toSquare: string | null
  timestamp: string
}

// Static roster — mirrors CHESS_THEATER_SPEC agent_roster_mapping
export const AGENT_ROSTER: AgentPiece[] = [
  // White — rank 1 (back row)
  { agentId: 'iron_claw_rook',    pieceType: 'rook',   crew: 'white', square: 'a1', color: '#E8E8F0' },
  { agentId: 'lightning_knight',  pieceType: 'knight', crew: 'white', square: 'b1', color: '#E8E8F0' },
  { agentId: 'devika_bishop',     pieceType: 'bishop', crew: 'white', square: 'c1', color: '#E8E8F0' },
  { agentId: 'synthia_queen',     pieceType: 'queen',  crew: 'white', square: 'd1', color: '#FFD700' },
  { agentId: 'pauli_king',        pieceType: 'king',   crew: 'white', square: 'e1', color: '#FFFFFF' },
  { agentId: 'popebot_bishop',    pieceType: 'bishop', crew: 'white', square: 'f1', color: '#E8E8F0' },
  { agentId: 'agent_zero_knight', pieceType: 'knight', crew: 'white', square: 'g1', color: '#E8E8F0' },
  { agentId: 'visionclaw_rook',   pieceType: 'rook',   crew: 'white', square: 'h1', color: '#E8E8F0' },
  // White — rank 2 (pawns)
  { agentId: 'cipher_pawn',  pieceType: 'pawn', crew: 'white', square: 'a2', color: '#C8C8D8' },
  { agentId: 'craft_pawn',   pieceType: 'pawn', crew: 'white', square: 'b2', color: '#C8C8D8' },
  { agentId: 'lens_pawn',    pieceType: 'pawn', crew: 'white', square: 'c2', color: '#C8C8D8' },
  { agentId: 'link_pawn',    pieceType: 'pawn', crew: 'white', square: 'd2', color: '#C8C8D8' },
  { agentId: 'probe_pawn',   pieceType: 'pawn', crew: 'white', square: 'e2', color: '#C8C8D8' },
  { agentId: 'pulse_pawn',   pieceType: 'pawn', crew: 'white', square: 'f2', color: '#C8C8D8' },
  { agentId: 'quill_pawn',   pieceType: 'pawn', crew: 'white', square: 'g2', color: '#C8C8D8' },
  { agentId: 'scout_pawn',   pieceType: 'pawn', crew: 'white', square: 'h2', color: '#C8C8D8' },
  // Black — rank 8 (back row)
  { agentId: 'frankenstack_rook', pieceType: 'rook',   crew: 'black', square: 'a8', color: '#1A0A2E' },
  { agentId: 'flash_knight',      pieceType: 'knight', crew: 'black', square: 'b8', color: '#1A0A2E' },
  { agentId: 'brenner_bishop',    pieceType: 'bishop', crew: 'black', square: 'c8', color: '#1A0A2E' },
  { agentId: 'cynthia_queen',     pieceType: 'queen',  crew: 'black', square: 'd8', color: '#9B30FF' },
  { agentId: 'shannon_king',      pieceType: 'king',   crew: 'black', square: 'e8', color: '#0D0D1A' },
  { agentId: 'tyrone_bishop',     pieceType: 'bishop', crew: 'black', square: 'f8', color: '#1A0A2E' },
  { agentId: 'cosmos_knight',     pieceType: 'knight', crew: 'black', square: 'g8', color: '#1A0A2E' },
  { agentId: 'pooracho_rook',     pieceType: 'rook',   crew: 'black', square: 'h8', color: '#1A0A2E' },
  // Black — rank 7 (pawns)
  { agentId: 'bridge_pawn',  pieceType: 'pawn', crew: 'black', square: 'a7', color: '#2A1A4E' },
  { agentId: 'echo_pawn',    pieceType: 'pawn', crew: 'black', square: 'b7', color: '#2A1A4E' },
  { agentId: 'forge_pawn',   pieceType: 'pawn', crew: 'black', square: 'c7', color: '#2A1A4E' },
  { agentId: 'pixel_pawn',   pieceType: 'pawn', crew: 'black', square: 'd7', color: '#2A1A4E' },
  { agentId: 'spark_pawn',   pieceType: 'pawn', crew: 'black', square: 'e7', color: '#2A1A4E' },
  { agentId: 'trace_pawn',   pieceType: 'pawn', crew: 'black', square: 'f7', color: '#2A1A4E' },
  { agentId: 'vault_pawn',   pieceType: 'pawn', crew: 'black', square: 'g7', color: '#2A1A4E' },
  { agentId: 'glitch_knight',pieceType: 'knight', crew: 'black', square: 'h7', color: '#2A1A4E' },
]
