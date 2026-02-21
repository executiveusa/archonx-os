import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

/**
 * Agent Viewing Room - 3D Visualization
 * 
 * A 3D space where you can watch agents interact in real-time.
 * Each agent is represented as an avatar with connection lines
 * showing their communications.
 */

interface Agent {
  id: string;
  name: string;
  role: string;
  position: { x: number; y: number; z: number };
  status: string;
  color: string;
}

interface Command {
  from: string;
  to: string;
  type: string;
  timestamp: Date;
}

interface ViewingRoomProps {
  agents: Agent[];
  commands: Command[];
  onAgentClick?: (agentId: string) => void;
}

const AGENT_COLORS: Record<string, string> = {
  'SYNTHIA': '#ff00ff',  // Magenta - Queen
  'ARIA': '#00ffff',     // Cyan - Architect
  'NEXUS': '#ffff00',    // Yellow - Coordinator
  'ORACLE': '#ff8800',   // Orange - Analyst
  'PHANTOM': '#8800ff',  // Purple - Stealth
  'CIPHER': '#00ff00',   // Green - Security
  'VECTOR': '#0088ff',   // Blue - Deployment
  'PRISM': '#ff0088',    // Pink - Content
  'DARYA': '#ff0066',    // Hot Pink - Crypto Cutie
  'ECHO': '#88ff00',     // Lime - Voice
  'ATLAS': '#ff8800',    // Orange - Maps
  'NOVA': '#ff00ff',     // Magenta - Creative
};

export const ViewingRoom: React.FC<ViewingRoomProps> = ({
  agents,
  commands,
  onAgentClick
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const agentMeshesRef = useRef<Map<string, THREE.Mesh>>(new Map());
  const commandLinesRef = useRef<THREE.Line[]>([]);
  
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'orbit' | 'top' | 'agent'>('orbit');

  // Initialize Three.js scene
  useEffect(() => {
    if (!containerRef.current) return;

    // Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a1a);
    scene.fog = new THREE.Fog(0x0a0a1a, 10, 50);
    sceneRef.current = scene;

    // Camera
    const camera = new THREE.PerspectiveCamera(
      75,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(0, 10, 15);
    cameraRef.current = camera;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxDistance = 50;
    controls.minDistance = 5;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0xffffff, 1, 100);
    pointLight.position.set(0, 20, 0);
    scene.add(pointLight);

    // Grid floor
    const gridHelper = new THREE.GridHelper(30, 30, 0x444444, 0x222222);
    scene.add(gridHelper);

    // Central hub
    const hubGeometry = new THREE.SphereGeometry(1, 32, 32);
    const hubMaterial = new THREE.MeshPhongMaterial({
      color: 0x00ffff,
      emissive: 0x004444,
      transparent: true,
      opacity: 0.8
    });
    const hub = new THREE.Mesh(hubGeometry, hubMaterial);
    hub.position.set(0, 1, 0);
    scene.add(hub);

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      controls.update();
      
      // Rotate hub
      hub.rotation.y += 0.01;
      
      // Animate command lines
      commandLinesRef.current.forEach((line, index) => {
        const material = line.material as THREE.LineBasicMaterial;
        material.opacity = Math.max(0, material.opacity - 0.01);
        if (material.opacity <= 0) {
          scene.remove(line);
          commandLinesRef.current.splice(index, 1);
        }
      });
      
      renderer.render(scene, camera);
    };
    animate();

    // Handle resize
    const handleResize = () => {
      if (!containerRef.current) return;
      camera.aspect = containerRef.current.clientWidth / containerRef.current.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  // Update agent positions
  useEffect(() => {
    if (!sceneRef.current) return;

    // Remove old agent meshes
    agentMeshesRef.current.forEach((mesh) => {
      sceneRef.current!.remove(mesh);
    });
    agentMeshesRef.current.clear();

    // Create new agent meshes
    agents.forEach((agent) => {
      const color = AGENT_COLORS[agent.name] || '#ffffff';
      
      // Agent avatar (sphere with glow)
      const geometry = new THREE.SphereGeometry(0.5, 32, 32);
      const material = new THREE.MeshPhongMaterial({
        color: new THREE.Color(color),
        emissive: new THREE.Color(color).multiplyScalar(0.3),
        transparent: true,
        opacity: 0.9
      });
      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.set(agent.position.x, agent.position.y + 1, agent.position.z);
      mesh.userData = { agentId: agent.id };
      
      // Add name label (sprite)
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d')!;
      canvas.width = 256;
      canvas.height = 64;
      context.fillStyle = color;
      context.font = 'bold 24px Arial';
      context.textAlign = 'center';
      context.fillText(agent.name, 128, 40);
      
      const texture = new THREE.CanvasTexture(canvas);
      const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
      const sprite = new THREE.Sprite(spriteMaterial);
      sprite.position.set(0, 1, 0);
      sprite.scale.set(2, 0.5, 1);
      mesh.add(sprite);
      
      sceneRef.current!.add(mesh);
      agentMeshesRef.current.set(agent.id, mesh);
      
      // Connection line to hub
      const lineGeometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 1, 0),
        new THREE.Vector3(agent.position.x, agent.position.y + 1, agent.position.z)
      ]);
      const lineMaterial = new THREE.LineBasicMaterial({
        color: new THREE.Color(color),
        transparent: true,
        opacity: 0.3
      });
      const line = new THREE.Line(lineGeometry, lineMaterial);
      sceneRef.current!.add(line);
    });
  }, [agents]);

  // Visualize commands
  useEffect(() => {
    if (!sceneRef.current) return;

    commands.forEach((command) => {
      const fromMesh = agentMeshesRef.current.get(command.from);
      const toMesh = agentMeshesRef.current.get(command.to);
      
      if (fromMesh && toMesh) {
        const points = [
          fromMesh.position.clone(),
          toMesh.position.clone()
        ];
        
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({
          color: 0xffff00,
          transparent: true,
          opacity: 1
        });
        
        const line = new THREE.Line(geometry, material);
        sceneRef.current!.add(line);
        commandLinesRef.current.push(line);
      }
    });
  }, [commands]);

  return (
    <div className="viewing-room">
      <div className="viewing-room-header">
        <h2>🎮 Agent Viewing Room</h2>
        <div className="view-controls">
          <button onClick={() => setViewMode('orbit')}>Orbit</button>
          <button onClick={() => setViewMode('top')}>Top</button>
          <button onClick={() => setViewMode('agent')}>Agent</button>
        </div>
      </div>
      
      <div 
        ref={containerRef} 
        className="viewing-room-canvas"
        style={{ width: '100%', height: '500px' }}
      />
      
      <div className="agent-list">
        <h3>Active Agents ({agents.length})</h3>
        <div className="agent-grid">
          {agents.map((agent) => (
            <div
              key={agent.id}
              className={`agent-card ${selectedAgent === agent.id ? 'selected' : ''}`}
              onClick={() => {
                setSelectedAgent(agent.id);
                onAgentClick?.(agent.id);
              }}
              style={{ borderColor: AGENT_COLORS[agent.name] }}
            >
              <div 
                className="agent-avatar"
                style={{ backgroundColor: AGENT_COLORS[agent.name] }}
              />
              <div className="agent-info">
                <span className="agent-name">{agent.name}</span>
                <span className="agent-role">{agent.role}</span>
              </div>
              <div className={`agent-status ${agent.status}`} />
            </div>
          ))}
        </div>
      </div>
      
      <style>{`
        .viewing-room {
          background: #0a0a1a;
          border-radius: 12px;
          padding: 20px;
          color: white;
        }
        
        .viewing-room-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }
        
        .view-controls button {
          background: #1a1a2e;
          border: 1px solid #333;
          color: white;
          padding: 8px 16px;
          margin-left: 8px;
          border-radius: 4px;
          cursor: pointer;
        }
        
        .view-controls button:hover {
          background: #2a2a4e;
        }
        
        .agent-list {
          margin-top: 20px;
        }
        
        .agent-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
          gap: 10px;
        }
        
        .agent-card {
          background: #1a1a2e;
          border: 2px solid;
          border-radius: 8px;
          padding: 10px;
          display: flex;
          align-items: center;
          gap: 10px;
          cursor: pointer;
          transition: transform 0.2s;
        }
        
        .agent-card:hover {
          transform: scale(1.05);
        }
        
        .agent-card.selected {
          box-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
        }
        
        .agent-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
        }
        
        .agent-info {
          display: flex;
          flex-direction: column;
        }
        
        .agent-name {
          font-weight: bold;
        }
        
        .agent-role {
          font-size: 12px;
          opacity: 0.7;
        }
        
        .agent-status {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          margin-left: auto;
        }
        
        .agent-status.active {
          background: #00ff00;
          box-shadow: 0 0 10px #00ff00;
        }
        
        .agent-status.working {
          background: #ffff00;
          animation: pulse 1s infinite;
        }
        
        .agent-status.idle {
          background: #666;
        }
        
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
};

export default ViewingRoom;
