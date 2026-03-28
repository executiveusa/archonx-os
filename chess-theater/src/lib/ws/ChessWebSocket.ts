// Chess Theater — ChessWebSocket
// Manages connection to chess-server port 3300 with auto-reconnect.

import { parseWsMessage } from './EventParser'
import { ReconnectStrategy } from './ReconnectStrategy'
import type { WsMessage } from '../types/events'
import type { BoardState } from '../types/agents'

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error'

export interface ChessWsCallbacks {
  onBoardState: (state: BoardState) => void
  onAgentAction: (msg: WsMessage) => void
  onStatusChange: (status: ConnectionStatus) => void
}

export class ChessWebSocket {
  private ws: WebSocket | null = null
  private reconnect = new ReconnectStrategy()
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private destroyed = false

  constructor(
    private readonly url: string,
    private readonly callbacks: ChessWsCallbacks,
  ) {}

  connect(): void {
    if (this.destroyed) return
    this.callbacks.onStatusChange('connecting')

    this.ws = new WebSocket(this.url)

    this.ws.onopen = () => {
      this.reconnect.reset()
      this.callbacks.onStatusChange('connected')
    }

    this.ws.onmessage = (ev: MessageEvent<string>) => {
      const msg = parseWsMessage(ev.data)
      if (!msg) return

      if (msg.type === 'ping') {
        this.ws?.send(JSON.stringify({ type: 'pong', timestamp: new Date().toISOString() }))
        return
      }

      if (msg.type === 'board_state') {
        const payload = msg.payload
        const boardState: BoardState = {
          pieces: payload.pieces.map((p) => ({
            agentId: p.agentId,
            square: p.square,
            animState: (p.status as BoardState['pieces'][number]['animState']) ?? 'idle',
          })),
          activeAgent: payload.activeAgent,
          lastAction: payload.lastAction
            ? {
                agentId: payload.lastAction.agentId,
                actionType: payload.lastAction.actionType,
                fromSquare: payload.lastAction.fromSquare,
                toSquare: payload.lastAction.toSquare,
                timestamp: payload.lastAction.timestamp,
              }
            : null,
          timestamp: new Date().toISOString(),
        }
        this.callbacks.onBoardState(boardState)
        return
      }

      if (msg.type === 'agent_action') {
        this.callbacks.onAgentAction(msg)
      }
    }

    this.ws.onclose = () => {
      if (this.destroyed) return
      this.callbacks.onStatusChange('disconnected')
      const delay = this.reconnect.nextDelay()
      this.reconnectTimer = setTimeout(() => this.connect(), delay)
    }

    this.ws.onerror = () => {
      this.callbacks.onStatusChange('error')
    }
  }

  destroy(): void {
    this.destroyed = true
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    this.ws?.close()
  }
}
