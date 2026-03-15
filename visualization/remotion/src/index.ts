import { Composition } from 'remotion';
import { KingModeIntro } from './KingModeIntro';

export const RemotionRoot = () => (
  <>
    <Composition
      id="KingModeIntro"
      component={KingModeIntro}
      durationInFrames={300}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{
        targetRevenue: 100_000_000,
        missionText: 'King Mode Activated · $100M by 2030 · 64 Agents · One Mission',
      }}
    />
  </>
);
