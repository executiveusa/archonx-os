// Chess Theater — BoardGeometry
// Creates an 8×8 board mesh with dark/light navy squares and gold border.

import * as THREE from 'three'

const DARK_SQUARE = new THREE.Color('#1a1a2e')
const LIGHT_SQUARE = new THREE.Color('#16213e')
const GOLD = new THREE.Color('#FFD700')

/** Size of each square in Three.js world units */
export const SQUARE_SIZE = 1.0
/** Board total span = 8 units */
export const BOARD_SPAN = 8 * SQUARE_SIZE
/** Offset so board is centred at origin */
export const BOARD_OFFSET = -BOARD_SPAN / 2 + SQUARE_SIZE / 2

/**
 * Returns a Three.js Group containing:
 * - 64 square meshes (dark/light pattern)
 * - A thin gold border plane underneath
 */
export function createBoard(): THREE.Group {
  const group = new THREE.Group()
  group.name = 'board'

  // Base border — slightly larger than board, thin slab
  const borderGeo = new THREE.BoxGeometry(BOARD_SPAN + 0.12, 0.04, BOARD_SPAN + 0.12)
  const borderMat = new THREE.MeshStandardMaterial({
    color: GOLD,
    metalness: 0.8,
    roughness: 0.4,
    opacity: 0.85,
    transparent: true,
  })
  const border = new THREE.Mesh(borderGeo, borderMat)
  border.position.y = -0.03
  border.receiveShadow = true
  group.add(border)

  // 64 squares
  const squareGeo = new THREE.BoxGeometry(SQUARE_SIZE, 0.02, SQUARE_SIZE)
  for (let rank = 0; rank < 8; rank++) {
    for (let file = 0; file < 8; file++) {
      const isDark = (rank + file) % 2 === 0
      const mat = new THREE.MeshStandardMaterial({
        color: isDark ? DARK_SQUARE : LIGHT_SQUARE,
        roughness: 0.9,
        metalness: 0.1,
      })
      mat.name = `sq_${String.fromCharCode(97 + file)}${rank + 1}`
      const mesh = new THREE.Mesh(squareGeo, mat)
      mesh.name = mat.name
      mesh.position.set(
        BOARD_OFFSET + file * SQUARE_SIZE,
        0,
        BOARD_OFFSET + rank * SQUARE_SIZE,
      )
      mesh.receiveShadow = true
      group.add(mesh)
    }
  }

  return group
}

/** Convert algebraic notation (e.g. "e4") to Three.js world XZ position */
export function squareToWorld(square: string): { x: number; z: number } {
  const file = square.charCodeAt(0) - 97 // a→0, h→7
  const rank = parseInt(square[1], 10) - 1 // '1'→0, '8'→7
  return {
    x: BOARD_OFFSET + file * SQUARE_SIZE,
    z: BOARD_OFFSET + rank * SQUARE_SIZE,
  }
}

/** Update a square's emissive intensity — used for active-agent pulse effect */
export function pulseSquare(board: THREE.Group, square: string, intensity: number): void {
  const mesh = board.getObjectByName(`sq_${square}`) as THREE.Mesh | undefined
  if (!mesh) return
  const mat = mesh.material as THREE.MeshStandardMaterial
  mat.emissive.set(intensity > 0 ? '#00BFFF' : '#000000')
  mat.emissiveIntensity = intensity
}
