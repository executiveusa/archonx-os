import type { BoardState } from '@/lib/types/agents'
import { AGENT_ROSTER } from '@/lib/types/agents'

interface Props {
  boardState: BoardState | null
}

export default function AgentHUD({ boardState }: Props) {
  const activeId = boardState?.activeAgent ?? null
  const activePiece = activeId ? AGENT_ROSTER.find((p) => p.agentId === activeId) : null
  const lastAction = boardState?.lastAction ?? null

  const activeCount = boardState?.pieces.filter((p) => p.animState !== 'idle').length ?? 0

  return (
    <>
      {/* System metrics — top left */}
      <div className="absolute top-4 left-4 font-mono text-xs text-[#00ff88] space-y-1">
        <div>ARCHON-X OS</div>
        <div>AGENTS ACTIVE: {activeCount}</div>
        <div className="opacity-60">
          {boardState ? new Date(boardState.timestamp).toLocaleTimeString() : '—'}
        </div>
      </div>

      {/* Active agent card — top right */}
      {activePiece && (
        <div
          className="absolute top-4 right-4 rounded-lg p-4 text-sm font-mono backdrop-blur-md"
          style={{
            border: `1px solid ${activePiece.crew === 'white' ? '#00BFFF' : '#FF00FF'}`,
            background: 'rgba(10, 10, 30, 0.7)',
            color: activePiece.crew === 'white' ? '#00BFFF' : '#FF00FF',
          }}
        >
          <div className="uppercase text-xs opacity-70 mb-1">{activePiece.crew} CREW</div>
          <div className="text-base font-bold">{activePiece.agentId.replace(/_/g, ' ').toUpperCase()}</div>
          <div className="text-xs opacity-80 mt-1">{activePiece.pieceType} · {activePiece.square}</div>
          {lastAction && (
            <div className="text-xs opacity-60 mt-2">{lastAction.actionType.replace(/_/g, ' ')}</div>
          )}
        </div>
      )}

      {/* Council indicator — bottom center */}
      {boardState?.pieces.some((p) => p.animState === 'thinking') && (
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 text-xs font-mono text-[#FF8C00] opacity-90">
          ⚖ HERMES COUNCIL IN SESSION
        </div>
      )}
    </>
  )
}
