
import React, { useState } from 'react';
import { GeminiService } from '../services/gemini';
import { PauliScript } from '../types';
import { Download, Loader2, Wand2, Clapperboard, Target, Zap } from 'lucide-react';

interface Props {
  onAnimate: (prompt: string) => void;
}

const ScriptLab: React.FC<Props> = ({ onAnimate }) => {
  const [topic, setTopic] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [script, setScript] = useState<PauliScript | null>(null);
  const gemini = new GeminiService();

  const handleGenerate = async () => {
    if (!topic) return;
    setIsLoading(true);
    try {
      const prompt = `
        You are Pauli, a hip, cynical automation expert. 
        Generate a 'Pauli's Cartoon Truth' script in UGC ad format.
        
        TOPIC: ${topic}
        AUDIENCE: Urban Gen Z / Millennials, skeptical of hype.
        TONE: Funny, direct, zero fluff, no jargon.
        
        REQUIREMENTS:
        - Hook (max 12 words) -> Punchlines -> Payoff -> CTA.
        - Define automation: 'when X happens, do Y.'
        - Contrast n8n (UI wrapper) vs Python (Code/Logs/Control).
        - Explain why n8n sells: speed, demos, non-dev buyers.
        - Explain reliability: code + tests + monitoring wins long-term.
        - End with: 'We install a self-healing automation stack in your business.'
        
        Return the response in the specified JSON schema.
      `;
      const result = await gemini.generateScript(prompt);
      setScript(result);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-20">
      <div className="bg-zinc-950 border-2 border-zinc-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden group">
        <div className="absolute top-0 right-0 w-64 h-64 bg-yellow-400/5 blur-[100px] pointer-events-none"></div>
        
        <div className="flex items-center gap-3 mb-6">
           <Target className="w-8 h-8 text-yellow-400" />
           <h3 className="heading-font text-4xl text-yellow-400">UGC Script Factory</h3>
        </div>
        
        <div className="space-y-4">
          <div className="relative">
            <textarea
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Why n8n demos look cool but Python runs your bank..."
              className="w-full h-32 bg-zinc-900 border border-zinc-800 rounded-2xl p-4 text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-yellow-400 transition-all resize-none"
            />
          </div>
          
          <div className="flex gap-4">
            <button
              onClick={handleGenerate}
              disabled={isLoading || !topic}
              className="flex-1 bg-yellow-400 hover:bg-yellow-300 disabled:opacity-50 text-black font-black py-4 rounded-2xl flex items-center justify-center gap-3 transition-transform active:scale-[0.98]"
            >
              {isLoading ? <Loader2 className="w-6 h-6 animate-spin" /> : <Wand2 className="w-6 h-6" />}
              Generate High-Conversion Script
            </button>
          </div>
        </div>
      </div>

      {script && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-400" />
              <h4 className="text-2xl font-black text-white">{script.title}</h4>
            </div>
            <div className="flex gap-2">
              <span className="px-3 py-1 bg-zinc-900 text-zinc-400 rounded-full text-xs font-mono">{script.duration_seconds}s</span>
              <button className="p-2 bg-zinc-900 hover:bg-zinc-800 rounded-lg text-zinc-400"><Download className="w-4 h-4" /></button>
            </div>
          </div>

          <div className="grid gap-6">
            <div className="bg-yellow-400/10 border border-yellow-400/20 p-6 rounded-2xl">
               <span className="text-[10px] font-mono text-yellow-500 block mb-1">THE HOOK (12 WORDS MAX)</span>
               <p className="text-2xl font-black text-yellow-400 leading-tight">"{script.hook}"</p>
            </div>

            {script.scenes.map((scene) => (
              <div key={scene.scene_id} className="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden group">
                <div className="flex bg-zinc-800/50 px-4 py-2 border-b border-zinc-800 justify-between items-center">
                  <span className="text-xs font-mono font-bold">SCENE_0{scene.scene_id}</span>
                  <div className="flex gap-4">
                    <span className="text-[10px] text-zinc-500 uppercase">{scene.sound_fx}</span>
                    <button 
                      onClick={() => onAnimate(`${scene.visual_description}. High-end urban cartoon style.`)}
                      className="text-[10px] font-bold text-yellow-400 hover:text-white flex items-center gap-1 transition-colors"
                    >
                      <Clapperboard className="w-3 h-3" /> ANIMATE
                    </button>
                  </div>
                </div>
                <div className="p-6 grid md:grid-cols-2 gap-8">
                  <div className="space-y-4">
                    <div>
                      <span className="text-[10px] font-mono text-zinc-500 block mb-1 uppercase">Visual Description</span>
                      <p className="text-sm text-zinc-300 italic">"{scene.visual_description}"</p>
                    </div>
                    <div>
                      <span className="text-[10px] font-mono text-zinc-500 block mb-1 uppercase">On-Screen Text</span>
                      <p className="text-sm font-black text-white uppercase tracking-tighter">"{scene.on_screen_text}"</p>
                    </div>
                  </div>
                  <div className="bg-black/40 p-4 rounded-xl border border-zinc-800">
                    <span className="text-[10px] font-mono text-blue-400 block mb-2 uppercase">Pauli Script</span>
                    <p className="text-zinc-100 leading-relaxed font-medium">"{scene.pauli_dialogue}"</p>
                  </div>
                </div>
              </div>
            ))}

            <div className="bg-zinc-950 border-2 border-white rounded-3xl p-8 flex flex-col items-center text-center space-y-4">
               <span className="bg-white text-black px-4 py-1 text-xs font-black rounded-full uppercase">Payoff & CTA</span>
               <h5 className="text-3xl font-black text-white">{script.cta.offer}</h5>
               <p className="text-zinc-400 max-w-sm">{script.cta.next_step}</p>
               <button className="bg-white text-black px-10 py-4 rounded-2xl font-black hover:bg-zinc-200 transition-all scale-105 shadow-xl">
                 {script.cta.link_text}
               </button>
               <div className="pt-4 flex gap-4 text-[10px] font-mono text-zinc-600">
                 {script.keywords.map(k => <span key={k}>#{k}</span>)}
               </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScriptLab;
