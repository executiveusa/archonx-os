
import React, { useState } from 'react';
import { GeminiService } from '../services/gemini';
import { Search, ExternalLink, ShieldCheck, AlertCircle, Loader2 } from 'lucide-react';

const FactChecker: React.FC = () => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<{ text: string, chunks: any[] } | null>(null);
  const gemini = new GeminiService();

  const handleSearch = async () => {
    if (!query) return;
    setIsLoading(true);
    try {
      const groundedResult = await gemini.searchGrounding(query);
      setResult(groundedResult);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="bg-zinc-950 border border-zinc-800 rounded-3xl p-8">
        <div className="flex items-center gap-4 mb-8">
           <div className="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(59,130,246,0.2)]">
              <Search className="text-white w-6 h-6" />
           </div>
           <div>
             <h2 className="heading-font text-4xl text-white">Truth Grounding</h2>
             <p className="text-zinc-500 text-sm">Verify automation facts with real-time Google Search data.</p>
           </div>
        </div>

        <div className="flex gap-4">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., Latest benchmarks for Python vs n8n execution..."
            className="flex-1 bg-zinc-900 border border-zinc-800 rounded-2xl px-6 py-4 text-zinc-100 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
          />
          <button
            onClick={handleSearch}
            disabled={isLoading || !query}
            className="bg-blue-500 hover:bg-blue-400 text-white font-bold px-8 py-4 rounded-2xl flex items-center gap-2 disabled:opacity-50 transition-all active:scale-95"
          >
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <ShieldCheck className="w-5 h-5" />}
            Verify
          </button>
        </div>
      </div>

      {result && (
        <div className="grid md:grid-cols-3 gap-8">
          <div className="md:col-span-2 space-y-6">
            <div className="bg-zinc-900/50 border border-zinc-800 rounded-3xl p-8 prose prose-invert max-w-none">
               <h3 className="text-xl font-bold text-white mb-4">The Verifed Truth</h3>
               <p className="text-zinc-300 leading-relaxed whitespace-pre-wrap">{result.text}</p>
            </div>
          </div>

          <div className="space-y-6">
            <div className="bg-zinc-950 border border-zinc-800 rounded-3xl p-6">
               <h4 className="text-xs font-mono text-zinc-500 uppercase mb-4 tracking-widest flex items-center gap-2">
                 <ExternalLink className="w-3 h-3" /> Sources Found
               </h4>
               <div className="space-y-3">
                 {result.chunks.map((chunk: any, i: number) => (
                   chunk.web && (
                     <a 
                       key={i} 
                       href={chunk.web.uri} 
                       target="_blank" 
                       rel="noopener noreferrer"
                       className="block p-3 bg-zinc-900 hover:bg-zinc-800 rounded-xl border border-zinc-800 transition-colors group"
                     >
                       <p className="text-sm font-bold text-zinc-200 line-clamp-1 group-hover:text-blue-400 transition-colors">{chunk.web.title || 'Referenced Source'}</p>
                       <p className="text-[10px] text-zinc-500 font-mono mt-1 truncate">{chunk.web.uri}</p>
                     </a>
                   )
                 ))}
                 {result.chunks.length === 0 && <p className="text-xs text-zinc-600 italic">No direct links returned, but info is grounded.</p>}
               </div>
            </div>

            <div className="p-4 bg-yellow-400/10 border border-yellow-400/20 rounded-2xl flex gap-3">
               <AlertCircle className="w-5 h-5 text-yellow-500 shrink-0" />
               <p className="text-[10px] text-yellow-200/60 leading-tight">
                 Grounded search helps Pauli stay accurate. n8n vs Python benchmarks change as libraries update. Always cross-verify critical production logic.
               </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FactChecker;
