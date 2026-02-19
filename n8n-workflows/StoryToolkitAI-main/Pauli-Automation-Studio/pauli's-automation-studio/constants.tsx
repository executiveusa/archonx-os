
import React from 'react';
import { 
  Mic, 
  Image as ImageIcon, 
  Search, 
  Cpu, 
  Video,
  Clapperboard,
  LayoutDashboard,
  Zap
} from 'lucide-react';
import { AppTab } from './types';

export const TABS = [
  { id: AppTab.Dashboard, label: 'Control Center', icon: <LayoutDashboard className="w-5 h-5" /> },
  { id: AppTab.Generator, label: 'Script Lab', icon: <Cpu className="w-5 h-5" /> },
  { id: AppTab.Brainstorm, label: 'Live Brainstorm', icon: <Mic className="w-5 h-5" /> },
  { id: AppTab.Visuals, label: 'Scene Studio', icon: <ImageIcon className="w-5 h-5" /> },
  { id: AppTab.Production, label: 'Animate (Veo)', icon: <Clapperboard className="w-5 h-5" /> },
  { id: AppTab.Analysis, label: 'B-Roll Critic', icon: <Video className="w-5 h-5" /> },
  { id: AppTab.Verification, label: 'Fact Checker', icon: <Search className="w-5 h-5" /> },
];

export const PAULI_SYSTEM_PROMPT = `
You are Pauli, a hip, direct, and slightly cynical automation teacher.
Your style is urban, Gen Z/Millennial friendly, and zero fluff.
You explain complex automation concepts (n8n vs Python) using metaphors that stick.
You hate marketing jargon. You value "long-term reliability" over "speed-to-demo".
`;
