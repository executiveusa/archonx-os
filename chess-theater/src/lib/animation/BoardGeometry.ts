// Chess Theater — BoardGeometry
// Maps algebraic chess square notation (e.g. "e4") to Three.js world coordinates.

import * as THREE from 'three'

// Board spans -3.5 to +3.5 on X and Z (8 squares × 1 unit each, centred at origin)
const SQUARE_SIZE = 1.0
const BOARD_OFFSET = 3.5

/**
 * Convert algebraic notation ("a1"–"h8") to a THREE.Vector3 at board level.
 * File a–h maps to X axis; rank 1–8 maps to Z axis.
 */
export function squareToWorld(square: string): THREE.Vector3 {
  const file = square.charCodeAt(0) - 97 // 'a' = 0 … 'h' = 7
  const rank = parseInt(square[1], 10) - 1 // '1' = 0 … '8' = 7

  const x = file * SQUARE_SIZE - BOARD_OFFSET + SQUARE_SIZE / 2
  const z = rank * SQUARE_SIZE - BOARD_OFFSET + SQUARE_SIZE / 2

  return new THREE.Vector3(x, 0, z)
}

/** Return the centre world position of a square index (0–63, row-major a1→h8). */
export function indexToWorld(index: number): THREE.Vector3 {
  const file = index % 8
  const rank = Math.floor(index / 8)
  const x = file * SQUARE_SIZE - BOARD_OFFSET + SQUARE_SIZE / 2
  const z = rank * SQUARE_SIZE - BOARD_OFFSET + SQUARE_SIZE / 2
  return new THREE.Vector3(x, 0, z)
}
