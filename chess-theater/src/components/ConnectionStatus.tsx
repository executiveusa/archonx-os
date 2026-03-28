import type { ConnectionStatus as Status } from '@/lib/ws/ChessWebSocket'

const STATUS_CONFIG: Record<Status, { dot: string; label: string; color: string }> = {
  connecting:   { dot: '●', label: 'CONNECTING', color: '#FFD700' },
  connected:    { dot: '●', label: 'LIVE',        color: '#00ff88' },
  disconnected: { dot: '●', label: 'OFFLINE',     color: '#888888' },
  error:        { dot: '●', label: 'ERROR',        color: '#FF0000' },
}

export default function ConnectionStatus({ status }: { status: Status }) {
  const cfg = STATUS_CONFIG[status]
  return (
    <div
      className="absolute bottom-4 right-4 flex items-center gap-2 text-xs font-mono"
      style={{ color: cfg.color }}
    >
      <span>{cfg.dot}</span>
      <span>CHESS SERVER {cfg.label}</span>
    </div>
  )
}
