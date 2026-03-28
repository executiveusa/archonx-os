// Chess Theater — EventParser
// Parses raw WS text → typed WsMessage. Returns null on unknown/malformed data.

import type { WsMessage } from '../types/events'

export function parseWsMessage(raw: string): WsMessage | null {
  try {
    const msg = JSON.parse(raw) as Record<string, unknown>
    if (typeof msg.type !== 'string') return null

    if (
      msg.type === 'board_state' ||
      msg.type === 'agent_action' ||
      msg.type === 'ping' ||
      msg.type === 'pong'
    ) {
      return msg as WsMessage
    }
    return null
  } catch {
    return null
  }
}
