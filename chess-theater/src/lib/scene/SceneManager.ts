// Chess Theater — SceneManager
// Initialises Three.js scene, camera, renderer, lights.
// Lifecycle: init() → update(deltaTime) → dispose()

import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import { createBoard } from './BoardGeometry'
import { createAllPieces } from './PieceFactory'
import { PieceAnimator } from '../animation/PieceAnimator'
import { AGENT_ROSTER } from '../types/agents'
import type { BoardState } from '../types/agents'

export class SceneManager {
  private renderer!: THREE.WebGLRenderer
  private scene!: THREE.Scene
  private camera!: THREE.PerspectiveCamera
  private controls!: OrbitControls
  private board!: THREE.Group
  private piecesGroup!: THREE.Group
  private animator!: PieceAnimator
  private animFrameId: number | null = null
  private autoRotateAngle = 0

  init(canvas: HTMLCanvasElement): void {
    // Renderer
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false })
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    this.renderer.setSize(canvas.clientWidth, canvas.clientHeight)
    this.renderer.shadowMap.enabled = true
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap
    this.renderer.outputEncoding = THREE.sRGBEncoding
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping
    this.renderer.toneMappingExposure = 1.2

    // Scene
    this.scene = new THREE.Scene()
    this.scene.background = new THREE.Color('#000005')
    this.scene.fog = new THREE.FogExp2('#000010', 0.04)

    // Camera
    this.camera = new THREE.PerspectiveCamera(45, canvas.clientWidth / canvas.clientHeight, 0.1, 100)
    this.camera.position.set(0, 12, 14)
    this.camera.lookAt(0, 0, 0)

    // Orbit controls
    this.controls = new OrbitControls(this.camera, canvas)
    this.controls.enableDamping = true
    this.controls.dampingFactor = 0.05
    this.controls.minPolarAngle = THREE.MathUtils.degToRad(15)
    this.controls.maxPolarAngle = THREE.MathUtils.degToRad(75)
    this.controls.minDistance = 6
    this.controls.maxDistance = 25
    this.controls.autoRotate = false // we handle manual rotation in idle

    // Lighting
    const ambient = new THREE.AmbientLight('#0a0a1a', 0.3)
    this.scene.add(ambient)

    const keyLight = new THREE.DirectionalLight('#ffffff', 1.2)
    keyLight.position.set(5, 10, 5)
    keyLight.castShadow = true
    keyLight.shadow.mapSize.setScalar(1024)
    this.scene.add(keyLight)

    const fillLight = new THREE.DirectionalLight('#4040ff', 0.4)
    fillLight.position.set(-5, 5, -5)
    this.scene.add(fillLight)

    const rimLight = new THREE.PointLight('#ff4400', 0.6, 30)
    rimLight.position.set(0, 2, -8)
    this.scene.add(rimLight)

    // Board
    this.board = createBoard()
    this.scene.add(this.board)

    // Pieces
    this.piecesGroup = createAllPieces(AGENT_ROSTER)
    this.scene.add(this.piecesGroup)

    // Animator
    this.animator = new PieceAnimator()

    // Resize handling
    const onResize = () => {
      this.camera.aspect = canvas.clientWidth / canvas.clientHeight
      this.camera.updateProjectionMatrix()
      this.renderer.setSize(canvas.clientWidth, canvas.clientHeight)
    }
    window.addEventListener('resize', onResize)

    this.startLoop()
  }

  private startLoop(): void {
    const tick = () => {
      this.animFrameId = requestAnimationFrame(tick)
      this.controls.update()

      // Slow cinematic auto-rotation when idle
      this.autoRotateAngle += 0.0008
      this.camera.position.x = Math.sin(this.autoRotateAngle) * 14
      this.camera.position.z = Math.cos(this.autoRotateAngle) * 14
      this.camera.lookAt(0, 0, 0)

      this.animator.update(this.piecesGroup)
      this.renderer.render(this.scene, this.camera)
    }
    tick()
  }

  applyBoardState(state: BoardState): void {
    for (const pieceState of state.pieces) {
      const mesh = this.piecesGroup.getObjectByName(pieceState.agentId) as THREE.Mesh | undefined
      if (!mesh) continue

      this.animator.applyState(mesh, pieceState.animState)

      if (pieceState.animState === 'moving' && pieceState.targetSquare) {
        this.animator.movePiece(mesh, pieceState.targetSquare)
      }
    }
  }

  dispose(): void {
    if (this.animFrameId !== null) cancelAnimationFrame(this.animFrameId)
    this.controls.dispose()
    this.renderer.dispose()
  }
}
