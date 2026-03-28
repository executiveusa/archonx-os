// Chess Theater — WebSocket event types

export type ActionType =
  | 'TASK_START'
  | 'TASK_COMPLETE'
  | 'COUNCIL_ENTER'
  | 'COUNCIL_EXIT'
  | 'COMMS_SEND'
  | 'ERROR'

export interface AgentAction {
  agentId: string
  actionType: ActionType
  fromSquare: string | null
  toSquare: string | null
  metadata?: Record<string, unknown>
}

export interface WsMessageBoardState {
  type: 'board_state'
  payload: {
    pieces: Array<{ agentId: string; square: string; status: string }>
    activeAgent: string | null
    lastAction: AgentAction & { timestamp: string } | null
  }
}

export interface WsMessageAgentAction {
  type: 'agent_action'
  payload: AgentAction & { timestamp: string }
}

export interface WsMessagePing {
  type: 'ping'
  timestamp: string
}

export interface WsMessagePong {
  type: 'pong'
  timestamp: string
}

export type WsMessage =
  | WsMessageBoardState
  | WsMessageAgentAction
  | WsMessagePing
  | WsMessagePong
