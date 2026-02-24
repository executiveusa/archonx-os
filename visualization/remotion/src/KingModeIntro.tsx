"""King Mode Intro — Remotion Composition

10-second intro sequence that plays when King Mode first activates.
Chess pieces assemble on the board, $100M counter starts from 0,
King piece glows gold.

Renders to: dashboard-agent-swarm/public/king-mode-intro.mp4
"""
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  Sequence,
  Audio,
  staticFile,
} from 'remotion';

// ---- Types ----------------------------------------------------------------

interface KingModeIntroProps {
  targetRevenue?: number;
  missionText?: string;
}

// ---- Sub-components -------------------------------------------------------

const GoldKingPiece: React.FC<{ progress: number }> = ({ progress }) => {
  const scale = interpolate(progress, [0, 1], [0.2, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const opacity = interpolate(progress, [0, 0.3], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const glow = interpolate(progress, [0.5, 1], [0, 40], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        position: 'absolute',
        width: 120,
        height: 120,
        left: '50%',
        top: '35%',
        transform: `translate(-50%, -50%) scale(${scale})`,
        opacity,
        fontSize: 80,
        filter: `drop-shadow(0 0 ${glow}px #F5A623)`,
        textAlign: 'center',
      }}
    >
      ♔
    </div>
  );
};

const RevenueCounter: React.FC<{ frame: number; fps: number; target: number }> = ({
  frame,
  fps,
  target,
}) => {
  const startFrame = fps * 3; // start at 3s
  const progress = Math.max(0, Math.min(1, (frame - startFrame) / (fps * 5)));
  const current = Math.floor(progress * target);
  const formatted = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(current);

  return (
    <div
      style={{
        position: 'absolute',
        bottom: '20%',
        left: 0,
        right: 0,
        textAlign: 'center',
        color: '#F5A623',
        fontSize: 48,
        fontFamily: 'monospace',
        fontWeight: 'bold',
        opacity: progress > 0 ? 1 : 0,
        textShadow: '0 0 20px #F5A623',
      }}
    >
      {formatted}
    </div>
  );
};

const MissionText: React.FC<{ progress: number; text: string }> = ({ progress, text }) => {
  const opacity = interpolate(progress, [0, 0.2, 0.8, 1], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        position: 'absolute',
        top: '60%',
        left: 0,
        right: 0,
        textAlign: 'center',
        color: '#00FFCC',
        fontSize: 24,
        fontFamily: 'monospace',
        letterSpacing: 4,
        opacity,
        textTransform: 'uppercase',
      }}
    >
      {text}
    </div>
  );
};

// ---- Main Composition -----------------------------------------------------

export const KingModeIntro: React.FC<KingModeIntroProps> = ({
  targetRevenue = 100_000_000,
  missionText = 'King Mode Activated · $100M by 2030 · 64 Agents · One Mission',
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const totalProgress = frame / durationInFrames;

  // Background fade from black to deep purple
  const bgOpacity = interpolate(frame, [0, fps * 0.5], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // King piece springs in at frame 30
  const kingSpring = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 60 },
    delay: fps * 1,
  });

  // Grid lines fade in
  const gridOpacity = interpolate(frame, [fps * 0.5, fps * 1.5], [0, 0.3], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        background: `rgba(5, 0, 20, ${bgOpacity})`,
        fontFamily: 'monospace',
        overflow: 'hidden',
      }}
    >
      {/* Chessboard grid overlay */}
      <AbsoluteFill
        style={{
          opacity: gridOpacity,
          backgroundImage:
            'repeating-linear-gradient(0deg, rgba(0,255,180,0.1) 0px, transparent 1px, transparent 80px, rgba(0,255,180,0.1) 80px), repeating-linear-gradient(90deg, rgba(0,255,180,0.1) 0px, transparent 1px, transparent 80px, rgba(0,255,180,0.1) 80px)',
        }}
      />

      {/* King Mode title */}
      <div
        style={{
          position: 'absolute',
          top: '15%',
          left: 0,
          right: 0,
          textAlign: 'center',
          color: 'white',
          fontSize: 64,
          fontWeight: 900,
          letterSpacing: 8,
          opacity: interpolate(frame, [fps * 0.2, fps * 0.8], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          }),
          textShadow: '0 0 40px rgba(100, 200, 255, 0.8)',
        }}
      >
        KING MODE
      </div>

      {/* Gold king chess piece */}
      <GoldKingPiece progress={kingSpring} />

      {/* Revenue counter */}
      <RevenueCounter frame={frame} fps={fps} target={targetRevenue} />

      {/* Mission text */}
      <MissionText progress={totalProgress} text={missionText} />

      {/* ArchonX logo bottom left */}
      <div
        style={{
          position: 'absolute',
          bottom: 40,
          left: 40,
          color: 'rgba(255,255,255,0.4)',
          fontSize: 16,
          letterSpacing: 2,
          opacity: interpolate(frame, [fps * 7, fps * 8], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          }),
        }}
      >
        ARCHONX OS · THE PAULI EFFECT
      </div>
    </AbsoluteFill>
  );
};
