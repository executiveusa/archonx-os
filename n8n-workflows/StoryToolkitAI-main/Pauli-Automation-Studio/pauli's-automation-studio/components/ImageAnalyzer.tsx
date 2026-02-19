
import React, { useState } from 'react';
import { GeminiService } from '../services/gemini';
import { Video, Upload, Search, Loader2, Sparkles, MessageSquare } from 'lucide-react';

const ImageAnalyzer: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [critique, setCritique] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const gemini = new GeminiService();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleAnalyze = async () => {
    if (!preview || !selectedFile) return;
    setIsLoading(true);
    try {
      const prompt = "You are Pauli, a cynical automation expert. Critique this B-roll or screenshot. Does it look like enterprise-grade automation or low-code hype? Be direct, hip, and funny.";
      const result = await gemini.analyzeMedia(preview, selectedFile.type, prompt);
      setCritique(result || "Pauli is speechless. (That's probably not a good thing)");
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center space-y-2">
        <h2 className="heading-font text-5xl text-yellow-400">B-Roll Critic</h2>
        <p className="text-zinc-400">Upload a screenshot of your automation or B-roll for Pauli's ruthless critique.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <div className="space-y-4">
          <div 
            onClick={() => document.getElementById('file-upload')?.click()}
            className={`aspect-video rounded-3xl border-2 border-dashed border-zinc-800 flex flex-col items-center justify-center cursor-pointer transition-all hover:bg-zinc-900/50 hover:border-yellow-400/50 group overflow-hidden relative ${preview ? 'border-solid border-zinc-700' : ''}`}
          >
            {preview ? (
              <img src={preview} className="w-full h-full object-cover" alt="Preview" />
            ) : (
              <>
                <Upload className="w-12 h-12 text-zinc-600 mb-4 group-hover:text-yellow-400 transition-colors" />
                <p className="text-zinc-500 font-bold">Drop Asset Here</p>
                <p className="text-zinc-700 text-xs font-mono">JPG, PNG, WEBP (B-roll Frames)</p>
              </>
            )}
            <input id="file-upload" type="file" className="hidden" onChange={handleFileChange} />
          </div>

          <button
            onClick={handleAnalyze}
            disabled={!preview || isLoading}
            className="w-full bg-white text-black font-black py-4 rounded-2xl flex items-center justify-center gap-3 hover:bg-zinc-200 transition-all disabled:opacity-50"
          >
            {isLoading ? <Loader2 className="w-6 h-6 animate-spin" /> : <Search className="w-6 h-6" />}
            Ask Pauli's Opinion
          </button>
        </div>

        <div className="bg-zinc-950 border-2 border-zinc-800 rounded-3xl p-6 relative overflow-hidden flex flex-col min-h-[300px]">
           <div className="absolute top-0 left-0 w-full h-1 bg-yellow-400"></div>
           <div className="flex items-center gap-2 mb-6 text-zinc-500 font-mono text-[10px] uppercase">
             <MessageSquare className="w-3 h-3 text-yellow-400" />
             <span>CRITIQUE_MODULE_ACTIVE</span>
           </div>

           {isLoading ? (
             <div className="flex-1 flex flex-col items-center justify-center space-y-4">
                <div className="flex gap-1">
                   <div className="w-2 h-2 bg-yellow-400 rounded-full animate-bounce" style={{animationDelay: '0s'}}></div>
                   <div className="w-2 h-2 bg-yellow-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                   <div className="w-2 h-2 bg-yellow-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
                <p className="text-zinc-500 font-mono text-xs">PAULI_IS_JUDGING_YOU...</p>
             </div>
           ) : critique ? (
             <div className="flex-1 space-y-4">
               <p className="text-xl font-bold leading-relaxed text-zinc-100 italic">"{critique}"</p>
               <div className="pt-6 border-t border-zinc-900 mt-auto flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-yellow-400 flex items-center justify-center text-black font-black text-xs">P</div>
                  <div>
                    <p className="text-[10px] font-mono text-zinc-500 uppercase">Status</p>
                    <p className="text-xs font-bold text-yellow-400">CRITICAL_VERDICT_DELIVERED</p>
                  </div>
               </div>
             </div>
           ) : (
             <div className="flex-1 flex flex-col items-center justify-center text-center opacity-20">
               <Sparkles className="w-16 h-16 mb-4" />
               <p className="font-bold">Waiting for input...</p>
             </div>
           )}
        </div>
      </div>
    </div>
  );
};

export default ImageAnalyzer;
