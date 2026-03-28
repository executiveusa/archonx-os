// Chess Theater — PieceFactory
// Creates Three.js Mesh objects for each of the 32 agent pieces.
// Uses geometric primitives (no GLTF dependency — guaranteed render).

import * as THREE from 'three'
import { squareToWorld } from './BoardGeometry'
import { createPieceMaterial } from './PieceMaterial'
import type { AgentPiece } from '../types/agents'

const PIECE_Y = 0.02 // sits on top of the board plane

function buildKingGeometry(): THREE.BufferGeometry {
  // Lathe geometry: crown silhouette
  const points = [
    new THREE.Vector2(0.0, 0.0),
    new THREE.Vector2(0.18, 0.0),
    new THREE.Vector2(0.16, 0.3),
    new THREE.Vector2(0.12, 0.5),
    new THREE.Vector2(0.15, 0.7),
    new THREE.Vector2(0.10, 0.9),
    new THREE.Vector2(0.06, 1.1),
    new THREE.Vector2(0.08, 1.2),
  ]
  return new THREE.LatheGeometry(points, 16)
}

function buildQueenGeometry(): THREE.BufferGeometry {
  const points = [
    new THREE.Vector2(0.0, 0.0),
    new THREE.Vector2(0.17, 0.0),
    new THREE.Vector2(0.15, 0.25),
    new THREE.Vector2(0.11, 0.45),
    new THREE.Vector2(0.13, 0.65),
    new THREE.Vector2(0.09, 0.85),
    new THREE.Vector2(0.05, 1.1),
  ]
  return new THREE.LatheGeometry(points, 16)
}

function buildRookGeometry(): THREE.BufferGeometry {
  const geo = new THREE.BoxGeometry(0.28, 0.7, 0.28)
  // chamfered top via CylinderGeometry on top
  return geo
}

function buildBishopGeometry(): THREE.BufferGeometry {
  const points = [
    new THREE.Vector2(0.0, 0.0),
    new THREE.Vector2(0.14, 0.0),
    new THREE.Vector2(0.13, 0.3),
    new THREE.Vector2(0.08, 0.6),
    new THREE.Vector2(0.04, 0.9),
    new THREE.Vector2(0.02, 1.0),
  ]
  return new THREE.LatheGeometry(points, 12)
}

function buildKnightGeometry(): THREE.BufferGeometry {
  // Abstracted horse-head: offset sphere
  const geo = new THREE.SphereGeometry(0.18, 12, 12)
  geo.translate(0.06, 0.55, 0)
  return geo
}

function buildPawnGeometry(): THREE.BufferGeometry {
  const geo = new THREE.SphereGeometry(0.14, 10, 10)
  geo.translate(0, 0.45, 0)
  return geo
}

const GEOMETRY_BUILDERS: Record<string, () => THREE.BufferGeometry> = {
  king:   buildKingGeometry,
  queen:  buildQueenGeometry,
  rook:   buildRookGeometry,
  bishop: buildBishopGeometry,
  knight: buildKnightGeometry,
  pawn:   buildPawnGeometry,
}

/** Create a single Three.js mesh for an AgentPiece */
export function createPieceMesh(piece: AgentPiece): THREE.Mesh {
  const geoFactory = GEOMETRY_BUILDERS[piece.pieceType] ?? buildPawnGeometry
  const geometry = geoFactory()
  const material = createPieceMaterial(piece.agentId, piece.crew, piece.pieceType, piece.color)

  const mesh = new THREE.Mesh(geometry, material)
  mesh.name = piece.agentId
  mesh.castShadow = true

  const { x, z } = squareToWorld(piece.square)
  mesh.position.set(x, PIECE_Y, z)

  // Store metadata
  mesh.userData = { agentId: piece.agentId, crew: piece.crew, pieceType: piece.pieceType }

  return mesh
}

/** Create all 32 piece meshes from the roster; returns a group */
export function createAllPieces(roster: AgentPiece[]): THREE.Group {
  const group = new THREE.Group()
  group.name = 'pieces'
  for (const piece of roster) {
    group.add(createPieceMesh(piece))
  }
  return group
}
