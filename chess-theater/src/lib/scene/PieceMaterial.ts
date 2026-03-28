// Chess Theater — PieceMaterial
// Metallic silver for white crew, matte obsidian for black crew.
// Returns MeshStandardMaterial per piece (cloned — not shared across pieces).

import * as THREE from 'three'
import type { Crew, PieceType } from '../types/agents'

/** Special overrides for king and queen */
const SPECIAL_COLORS: Partial<Record<string, string>> = {
  pauli_king: '#FFFFFF',
  synthia_queen: '#FFD700',
  shannon_king: '#0D0D1A',
  cynthia_queen: '#9B30FF',
}

export function createPieceMaterial(
  agentId: string,
  crew: Crew,
  pieceType: PieceType,
  baseColor: string,
): THREE.MeshStandardMaterial {
  const color = SPECIAL_COLORS[agentId] ?? baseColor

  if (crew === 'white') {
    return new THREE.MeshStandardMaterial({
      color: new THREE.Color(color),
      metalness: pieceType === 'king' ? 0.9 : pieceType === 'queen' ? 0.85 : 0.7,
      roughness: pieceType === 'king' ? 0.15 : 0.25,
      envMapIntensity: 1.0,
    })
  }

  // Black crew — matte obsidian
  return new THREE.MeshStandardMaterial({
    color: new THREE.Color(color),
    metalness: 0.15,
    roughness: 0.85,
    envMapIntensity: 0.3,
  })
}

/** Apply animation-state color/emissive modifiers to an existing material */
export function applyAnimState(
  mat: THREE.MeshStandardMaterial,
  state: string,
  crew: Crew,
): void {
  // Reset
  mat.emissiveIntensity = 0
  mat.emissive.set('#000000')
  mat.opacity = 1
  mat.transparent = false

  switch (state) {
    case 'thinking':
      mat.emissive.set('#FF8C00')
      mat.emissiveIntensity = 0.3
      break
    case 'active':
      mat.emissive.set(crew === 'white' ? '#00BFFF' : '#FF00FF')
      mat.emissiveIntensity = 0.5
      break
    case 'done':
      mat.emissive.set('#FFFFFF')
      mat.emissiveIntensity = 0.6
      break
    case 'error':
      mat.emissive.set('#FF0000')
      mat.emissiveIntensity = 0.8
      break
  }
}
