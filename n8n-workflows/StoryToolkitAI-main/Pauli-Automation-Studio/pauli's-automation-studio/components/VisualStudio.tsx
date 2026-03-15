
import React, { useState } from 'react';
import { GeminiService } from '../services/gemini';
import { ImageIcon, Wand2, Loader2, Download, Maximize2, Layers } from 'lucide-react';

const VisualStudio: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [aspectRatio, setAspectRatio] = useState('16:9');
  const [isLoading, setIsLoading] = useState(false);
  const [image, setImage] = useState<string | null>(null);
  const gemini = new GeminiService();

  const handleGenerate = async () => {
    if (!prompt) return;
    setIsLoading(true);
    try {
      // Pauli's specific style enforcement
      const fullPrompt = `A stylized urban cartoon in the 'Pauli's Truth' aesthetic. Sharp outlines, vibrant but gritty colors, Gen Z appeal. Subject: ${prompt}`;
      const url = await gemini.generateImage(fullPrompt, aspectRatio);
      setImage(url);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const ratios = ['1:1', '3:4', '4:3', '9:16', '16:9', '21:9'];

  return (
    <div className="max-w-5xl mx-auto grid lg:grid-cols-2 gap-12">
      <div className="space-y-8">
        <div className="space-y-2">
          <h2 className="heading-font text-5xl text-yellow-400">Scene Studio</h2>
          <p className="text-zinc-400">Create the gritty urban cartoon visuals for your script. Pauli likes high-contrast, bold imagery.</p>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 p-6 rounded-3xl space-y-6 shadow-xl">
          <div className="space-y-2">
            <label className="text-xs font-mono text-zinc-500 uppercase">Prompt (Describe the scene)</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Pauli standing in front of a giant wall of messy n8n nodes, looking unimpressed..."
              className="w-full h-40 bg-black border border-zinc-800 rounded-2xl p-4 text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-1 focus:ring-yellow-400 transition-all resize-none"
            />
          </div>

          <div className="space-y-4">
            <label className="text-xs font-mono text-zinc-500 uppercase flex items-center gap-2">
               <Layers className="w-3 h-3" /> Aspect Ratio
            </label>
            <div className="grid grid-cols-3 gap-2">
              {ratios.map(r => (
                <button
                  key={r}
                  onClick={() => setAspectRatio(r)}
                  className={`py-2 rounded-lg text-xs font-bold transition-all ${
                    aspectRatio === r ? 'bg-yellow-400 text-black' : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                  }`}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleGenerate}
            disabled={isLoading || !prompt}
            className="w-full bg-yellow-400 hover:bg-yellow-300 disabled:opacity-50 text-black font-black py-4 rounded-2xl flex items-center justify-center gap-3 transition-transform active:scale-[0.98] shadow-lg shadow-yellow-400/10"
          >
            {isLoading ? <Loader2 className="w-6 h-6 animate-spin" /> : <Wand2 className="w-6 h-6" />}
            Render Cartoon Scene
          </button>
        </div>
      </div>

      <div className="relative group">
        <div className={`w-full aspect-square md:aspect-[16/9] bg-zinc-950 border-2 border-dashed border-zinc-800 rounded-3xl flex items-center justify-center overflow-hidden transition-all duration-700 ${image ? 'border-solid border-zinc-700' : ''}`}>
          {isLoading ? (
            <div className="flex flex-col items-center gap-4">
              <div className="w-12 h-12 border-4 border-yellow-400/20 border-t-yellow-400 rounded-full animate-spin"></div>
              <p className="text-zinc-500 font-mono text-xs animate-pulse">GENERATING_PIXELS...</p>
            </div>
          ) : image ? (
            <img src={image} className="w-full h-full object-cover" alt="Generated scene" />
          ) : (
            <div className="flex flex-col items-center gap-4 opacity-20 group-hover:opacity-40 transition-opacity">
              <ImageIcon className="w-24 h-24" />
              <p className="font-bold text-lg">Visual Output</p>
            </div>
          )}

          {image && (
            <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-4">
              <button className="bg-white text-black p-4 rounded-full hover:scale-110 transition-transform">
                <Download className="w-6 h-6" />
              </button>
              <button className="bg-white text-black p-4 rounded-full hover:scale-110 transition-transform">
                <Maximize2 className="w-6 h-6" />
              </button>
            </div>
          )}
        </div>
        
        {image && (
           <div className="mt-4 p-4 bg-zinc-900 rounded-xl border border-zinc-800 flex justify-between items-center">
              <div className="flex items-center gap-3">
                 <div className="w-2 h-2 rounded-full bg-green-500"></div>
                 <span className="text-xs font-mono text-zinc-400">1K_RESOLUTION_STYLIZED</span>
              </div>
              <span className="text-xs font-mono text-zinc-500 uppercase">{aspectRatio}</span>
           </div>
        )}
      </div>
    </div>
  );
};

export default VisualStudio;
