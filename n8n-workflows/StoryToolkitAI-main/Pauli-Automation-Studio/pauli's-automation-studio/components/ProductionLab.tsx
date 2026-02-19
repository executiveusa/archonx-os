
import React, { useState, useEffect } from 'react';
import { GeminiService } from '../services/gemini';
import { Clapperboard, Loader2, Play, Download, AlertTriangle, ShieldCheck } from 'lucide-react';

interface Props {
  initialPrompt?: string;
}

const ProductionLab: React.FC<Props> = ({ initialPrompt = '' }) => {
  const [prompt, setPrompt] = useState(initialPrompt);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const gemini = new GeminiService();

  useEffect(() => {
    if (initialPrompt) setPrompt(initialPrompt);
  }, [initialPrompt]);

  const handleGenerate = async () => {
    if (!prompt) return;
    setIsLoading(true);
    setError(null);
    try {
      const url = await gemini.generateVideo(prompt, (msg) => setStatus(msg));
      setVideoUrl(url);
    } catch (err: any) {
      console.error(err);
      if (err.message === "API_KEY_ERROR") {
        setError("Your API key doesn't have access to Veo. Ensure you've selected a paid project with billing enabled.");
      } else {
        setError("Production stalled. Check your connection or API limits.");
      }
    } finally {
      setIsLoading(false);
      setStatus('');
    }
  };

  return (
    <div className="max-w-5xl mx-auto grid lg:grid-cols-2 gap-12">
      <div className="space-y-8">
        <div className="space-y-2">
          <h2 className="heading-font text-5xl text-yellow-400">Veo Production</h2>
          <p className="text-zinc-400">Turn your script scenes into high-quality 1080p animation. Pauli demands professional cuts.</p>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 p-6 rounded-3xl space-y-6 shadow-xl">
          <div className="space-y-2">
            <label className="text-xs font-mono text-zinc-500 uppercase">Director's Prompt</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="A close up of Pauli with a smirk, standing in a futuristic command center..."
              className="w-full h-40 bg-black border border-zinc-800 rounded-2xl p-4 text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-1 focus:ring-yellow-400 transition-all resize-none"
            />
          </div>

          <div className="p-4 bg-zinc-950 rounded-xl border border-zinc-800 flex items-start gap-3">
            <div className="p-2 bg-yellow-400/10 rounded-lg">
              <AlertTriangle className="w-4 h-4 text-yellow-400" />
            </div>
            <p className="text-[10px] text-zinc-500 leading-tight">
              Video generation can take 2-5 minutes. Veo models require a paid API key from a project with billing enabled.
            </p>
          </div>

          <button
            onClick={handleGenerate}
            disabled={isLoading || !prompt}
            className="w-full bg-yellow-400 hover:bg-yellow-300 disabled:opacity-50 text-black font-black py-4 rounded-2xl flex items-center justify-center gap-3 transition-transform active:scale-[0.98] shadow-lg shadow-yellow-400/10"
          >
            {isLoading ? <Loader2 className="w-6 h-6 animate-spin" /> : <Clapperboard className="w-6 h-6" />}
            Render Animation
          </button>
        </div>

        {error && (
          <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-2xl flex items-center gap-3 text-red-400">
            <ShieldCheck className="w-5 h-5 shrink-0" />
            <p className="text-xs font-bold">{error}</p>
          </div>
        )}
      </div>

      <div className="relative group">
        <div className={`w-full aspect-[16/9] bg-zinc-950 border-2 border-dashed border-zinc-800 rounded-3xl flex items-center justify-center overflow-hidden transition-all duration-700 ${videoUrl ? 'border-solid border-zinc-700 shadow-2xl' : ''}`}>
          {isLoading ? (
            <div className="flex flex-col items-center gap-6">
              <div className="relative">
                <div className="w-20 h-20 border-4 border-yellow-400/10 rounded-full"></div>
                <div className="absolute inset-0 border-4 border-yellow-400 border-t-transparent rounded-full animate-spin"></div>
              </div>
              <div className="text-center space-y-2">
                <p className="text-yellow-400 font-mono text-sm tracking-widest animate-pulse">{status || 'INITIALIZING'}</p>
                <p className="text-zinc-600 text-[10px] uppercase">Veo 3.1 Pro Engine • 1080p</p>
              </div>
            </div>
          ) : videoUrl ? (
            <video 
              src={videoUrl} 
              controls 
              autoPlay 
              loop 
              className="w-full h-full object-cover" 
            />
          ) : (
            <div className="flex flex-col items-center gap-4 opacity-20 group-hover:opacity-40 transition-opacity">
              <Play className="w-24 h-24" />
              <p className="font-bold text-lg tracking-tight">Production Output</p>
            </div>
          )}

          {videoUrl && (
            <div className="absolute top-4 right-4 flex gap-2">
              <a 
                href={videoUrl} 
                download="pauli_scene.mp4"
                className="bg-black/60 hover:bg-white hover:text-black backdrop-blur-md text-white p-3 rounded-xl transition-all border border-white/10"
              >
                <Download className="w-5 h-5" />
              </a>
            </div>
          )}
        </div>
        
        {videoUrl && (
           <div className="mt-4 p-4 bg-zinc-900 rounded-2xl border border-zinc-800 flex justify-between items-center">
              <div className="flex items-center gap-3">
                 <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]"></div>
                 <span className="text-xs font-mono text-zinc-400">MASTER_RENDER_SUCCESS</span>
              </div>
              <span className="text-xs font-mono text-zinc-500 uppercase tracking-widest">1080p • 16:9 • MP4</span>
           </div>
        )}
      </div>
    </div>
  );
};

export default ProductionLab;
