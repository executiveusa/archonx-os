// Chess Theater — PieceAnimator
// Lerp-based arc trajectory for piece movement.
// Idle breathing pulse via sin oscillation.

import * as THREE from 'three'
import { squareToWorld } from './BoardGeometry'
import { applyAnimState } from './PieceMaterial'

const MOVE_DURATION_MS = 800
const ARC_HEIGHT = 2.4 // board_width * 0.3

interface ActiveAnim {
  mesh: THREE.Mesh
  startPos: THREE.Vector3
  endPos: THREE.Vector3
  startTime: number
  onComplete?: () => void
}

export class PieceAnimator {
  private activeAnims: Map<string, ActiveAnim> = new Map()
  private startTime = Date.now()

  /** Call once per frame — updates all animations */
  update(pieces: THREE.Group): void {
    const now = Date.now()
    const elapsed = (now - this.startTime) / 1000

    // Breathing idle for non-animating pieces
    pieces.children.forEach((obj: THREE.Object3D) => {
      const mesh = obj as THREE.Mesh
      const anim = this.activeAnims.get(mesh.name)
      if (!anim) {
        // Subtle idle scale breathe
        const breathe = 1 + Math.sin(elapsed * 1.5 + mesh.position.x) * 0.025
        mesh.scale.setScalar(breathe)
      }
    })

    // Update arc animations
    for (const [agentId, anim] of this.activeAnims.entries()) {
      const t = Math.min((now - anim.startTime) / MOVE_DURATION_MS, 1)
      const eased = easeOutCubic(t)

      // Arc: lerp XZ, parabola Y
      const x = anim.startPos.x + (anim.endPos.x - anim.startPos.x) * eased
      const z = anim.startPos.z + (anim.endPos.z - anim.startPos.z) * eased
      const y = anim.startPos.y + ARC_HEIGHT * Math.sin(Math.PI * t)
      anim.mesh.position.set(x, y, z)

      if (t >= 1) {
        anim.mesh.position.copy(anim.endPos)
        this.activeAnims.delete(agentId)
        anim.onComplete?.()
      }
    }
  }

  /** Trigger arc-move animation from current position to targetSquare */
  movePiece(mesh: THREE.Mesh, toSquare: string, onComplete?: () => void): void {
    const { x, z } = squareToWorld(toSquare)
    const endPos = new THREE.Vector3(x, mesh.position.y, z)
    this.activeAnims.set(mesh.name, {
      mesh,
      startPos: mesh.position.clone(),
      endPos,
      startTime: Date.now(),
      onComplete,
    })
  }

  /** Apply visual state (emissive/color) to piece material */
  applyState(mesh: THREE.Mesh, state: string): void {
    const mat = mesh.material as THREE.MeshStandardMaterial
    const crew = mesh.userData.crew as string
    applyAnimState(mat, state, crew as 'white' | 'black')
  }
}

function easeOutCubic(t: number): number {
  return 1 - Math.pow(1 - t, 3)
}
