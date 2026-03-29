'use client'

import { useEffect, useRef, useState } from 'react'
import { SceneManager } from '@/lib/scene/SceneManager'
import { ChessWebSocket } from '@/lib/ws/ChessWebSocket'
import type { BoardState } from '@/lib/types/agents'
import type { ConnectionStatus as ConnectionStatusType } from '@/lib/ws/ChessWebSocket'
import AgentHUD from './AgentHUD'
import ConnectionStatus from './ConnectionStatus'

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? 'ws://localhost:3300/ws'

function detectWebGL(): boolean {
  try {
    const c = document.createElement('canvas')
    return !!(c.getContext('webgl2') || c.getContext('webgl'))
  } catch {
    return false
  }
}

export default function ChessTheater() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const sceneRef = useRef<SceneManager | null>(null)
  const wsRef = useRef<ChessWebSocket | null>(null)

  const [boardState, setBoardState] = useState<BoardState | null>(null)
  const [connStatus, setConnStatus] = useState<ConnectionStatusType>('connecting')
  const [initError, setInitError] = useState<string | null>(null)

  useEffect(() => {
    if (!canvasRef.current) return

    if (!detectWebGL()) {
      setInitError('WebGL is not supported in this browser. Chess Theater requires a GPU-enabled browser.')
      return
    }

    try {
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
    } catch (err) {
      setInitError(`Failed to initialize 3D scene: ${err instanceof Error ? err.message : String(err)}`)
    }
  }, [])

  if (initError) {
    return (
      <div className="flex items-center justify-center w-full h-screen bg-black text-white">
        <div className="text-center max-w-md">
          <h1 className="text-2xl font-bold mb-4">Chess Theater</h1>
          <p className="text-gray-400">{initError}</p>
        </div>
      </div>
    )
  }

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
