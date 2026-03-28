'use client'

import { useEffect, useRef, useState } from 'react'
import { SceneManager } from '@/lib/scene/SceneManager'
import { ChessWebSocket } from '@/lib/ws/ChessWebSocket'
import type { BoardState } from '@/lib/types/agents'
import type { ConnectionStatus as ConnectionStatusType } from '@/lib/ws/ChessWebSocket'
import AgentHUD from './AgentHUD'
import ConnectionStatus from './ConnectionStatus'

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? 'ws://localhost:3300/ws'

export default function ChessTheater() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const sceneRef = useRef<SceneManager | null>(null)
  const wsRef = useRef<ChessWebSocket | null>(null)

  const [boardState, setBoardState] = useState<BoardState | null>(null)
  const [connStatus, setConnStatus] = useState<ConnectionStatusType>('connecting')

  useEffect(() => {
    if (!canvasRef.current) return

    // Init Three.js scene
    const scene = new SceneManager()
    scene.init(canvasRef.current)
    sceneRef.current = scene

    // Init WebSocket
    const ws = new ChessWebSocket(WS_URL, {
      onBoardState: (state) => {
        setBoardState(state)
        scene.applyBoardState(state)
      },
      onAgentAction: () => {
        // Future: trigger specific animations on agent_action events
      },
      onStatusChange: setConnStatus,
    })
    ws.connect()
    wsRef.current = ws

    return () => {
      ws.destroy()
      scene.dispose()
    }
  }, [])

  return (
    <div className="relative w-full h-screen">
      <canvas
        id="chess-theater-canvas"
        ref={canvasRef}
        className="w-full h-full block"
      />
      <div className="hud-overlay">
        <AgentHUD boardState={boardState} />
        <ConnectionStatus status={connStatus} />
      </div>
    </div>
  )
}
