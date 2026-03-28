// Chess Theater — PieceMaterial
// Applies animation-state-driven emissive/colour changes to piece materials.

import * as THREE from 'three'

// Emissive intensity and colour per animation state and crew
// ColorRepresentation was added in @types/three 0.130 — use number | string for r128 compat
type ColorLike = number | string
const STATE_EMISSIVE: Record<string, Record<'white' | 'black', ColorLike>> = {
  IDLE: { white: 0x000000, black: 0x000000 },
  THINKING: { white: 0x0044ff, black: 0xff4400 },
  MOVING: { white: 0x00ffaa, black: 0xffaa00 },
  RESOLVED: { white: 0x00ff44, black: 0xff0044 },
}

const STATE_INTENSITY: Record<string, number> = {
  IDLE: 0,
  THINKING: 0.35,
  MOVING: 0.55,
  RESOLVED: 0.25,
}

/**
 * Mutate the given MeshStandardMaterial to reflect the animation state.
 * @param mat   The piece's material (must be MeshStandardMaterial)
 * @param state One of IDLE | THINKING | MOVING | RESOLVED
 * @param crew  'white' | 'black' — determines emissive colour palette
 */
export function applyAnimState(
  mat: THREE.MeshStandardMaterial,
  state: string,
  crew: 'white' | 'black' = 'white',
): void {
  const emissivePalette = STATE_EMISSIVE[state] ?? STATE_EMISSIVE.IDLE
  const intensity = STATE_INTENSITY[state] ?? 0

  mat.emissive.set(emissivePalette[crew])
  mat.emissiveIntensity = intensity
  mat.needsUpdate = true
}

/** Build a base MeshStandardMaterial for a chess piece by crew. */
export function buildPieceMaterial(crew: 'white' | 'black'): THREE.MeshStandardMaterial {
  return new THREE.MeshStandardMaterial({
    color: crew === 'white' ? 0xf0ede0 : 0x1a1a2e,
    roughness: 0.35,
    metalness: 0.15,
    emissive: 0x000000,
    emissiveIntensity: 0,
  })
}
