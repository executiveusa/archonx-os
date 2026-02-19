
export interface PauliScene {
  scene_id: number;
  visual_description: string;
  pauli_dialogue: string;
  on_screen_text: string;
  sound_fx: string;
  b_roll_or_overlay: string;
  cta_step?: string;
}

export interface PauliScript {
  title: string;
  duration_seconds: number;
  hook: string;
  scenes: PauliScene[];
  cta: {
    offer: string;
    next_step: string;
    link_text: string;
  };
  keywords: string[];
  thumbnail_text: string;
}

export interface PipelineTask {
  id: string;
  label: string;
  status: 'idle' | 'running' | 'success' | 'error';
  lastRun?: string;
}

export enum AppTab {
  Dashboard = 'dashboard',
  Generator = 'generator',
  Brainstorm = 'brainstorm',
  Visuals = 'visuals',
  Production = 'production',
  Analysis = 'analysis',
  Verification = 'verification'
}
