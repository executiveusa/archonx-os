
import React from 'react';
import { AppTab } from '../types';
import GlassCard from './UI/GlassCard';
import { 
  Zap, 
  Search, 
  Cpu, 
  Mic, 
  Clapperboard, 
  Share2, 
  BarChart3, 
  Activity,
  ArrowRight,
  RefreshCw,
  Terminal,
  ChevronRight
} from 'lucide-react';

interface Props {
  onAction: (tab: AppTab) => void;
}

const Dashboard: React.FC<Props> = ({ onAction }) => {
  const steps = [
    { id: 'research', label: 'Research', icon: <Search className="w-5 h-5" />, desc: 'Ingesting niche news', status: 'Active', tab: AppTab.Verification },
    { id: 'script', label: 'Write', icon: <Cpu className="w-5 h-5" />, desc: 'Truth-scripts', status: 'Active', tab: AppTab.Generator },
    { id: 'voice', label: 'Voice', icon: <Mic className="w-5 h-5" />, desc: 'Piper Synthesis', status: 'Idle', tab: AppTab.Brainstorm },
    { id: 'render', label: 'Render', icon: <Clapperboard className="w-5 h-5" />, desc: 'Veo 1080p', status: 'Idle', tab: AppTab.Production },
    { id: 'post', label: 'Publish', icon: <Share2 className="w-5 h-5" />, desc: 'TikTok/IG/YT', status: 'Complete', tab: AppTab.Dashboard },
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      {/* Hero Stats */}
      <div className="grid lg:grid-cols-3 gap-6">
        <GlassCard className="lg:col-span-2 p-10 flex flex-col justify-between min-h-[300px]">
          <div className="space-y-4">
            <div className="flex items-center gap-2 px-3 py-1 bg-yellow-400/10 rounded-full w-fit">
              <span className="w-1.5 h-1.5 rounded-full bg-yellow-400 animate-pulse" />
              <span className="text-[10px] font-black text-yellow-400 uppercase tracking-widest">Autonomous Active</span>
            </div>
            <h2 className="heading-font text-6xl text-white leading-none">PAULI IS ONLINE</h2>
            <p className="text-zinc-400 text-lg max-w-md font-medium leading-relaxed">
              Your autonomous factory is currently mining the n8n repo for truth-telling content patterns.
            </p>
          </div>
          
          <div className="flex flex-wrap gap-4 mt-8">
            <button 
              onClick={() => onAction(AppTab.Generator)}
              className="bg-yellow-400 text-black px-8 py-4 rounded-2xl font-black flex items-center gap-3 hover:bg-yellow-300 hover:scale-105 active:scale-95 transition-all shadow-xl shadow-yellow-400/10"
            >
              Start New Batch <ArrowRight className="w-5 h-5" />
            </button>
            <div className="px-6 py-4 bg-zinc-950/40 rounded-2xl border border-white/5 flex items-center gap-3 text-zinc-500 font-mono text-[10px] uppercase font-bold">
              <RefreshCw className="w-3 h-3 animate-spin text-yellow-400" />
              Updating n8n Index
            </div>
          </div>
        </GlassCard>

        <GlassCard className="p-10 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-8">
              <h3 className="text-[10px] font-black text-zinc-500 uppercase tracking-[0.2em]">Daily Reach</h3>
              <BarChart3 className="w-5 h-5 text-zinc-700" />
            </div>
            <div className="text-6xl font-black text-white mb-2 tabular-nums">1.4K</div>
            <p className="text-green-500 text-xs font-bold bg-green-500/10 px-2 py-1 rounded-md w-fit">+12% vs. Yesterday</p>
          </div>
          <div className="h-20 flex items-end gap-1.5">
             {[30, 60, 45, 80, 55, 70, 40, 75, 85, 95].map((h, i) => (
               <div key={i} className="flex-1 bg-yellow-400/20 rounded-t-lg transition-all hover:bg-yellow-400 group relative">
                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 bg-white text-black text-[8px] font-black px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">{h}%</div>
                  <div className="w-full h-full bg-yellow-400/40 rounded-t-lg" style={{ height: `${h}%` }}></div>
               </div>
             ))}
          </div>
        </GlassCard>
      </div>

      {/* Modern Pipeline Pipeline */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-sm font-black text-white uppercase tracking-widest flex items-center gap-3">
             <div className="w-2 h-8 bg-yellow-400 rounded-full" />
             Content Loop Pipeline
          </h3>
          <span className="text-[10px] font-mono text-zinc-500">POLLING_INTERVAL: 60s</span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {steps.map((step, i) => (
            <div 
              key={step.id} 
              onClick={() => onAction(step.tab)}
              className="group relative cursor-pointer"
            >
              <GlassCard className={`p-6 h-full transition-all duration-300 group-hover:translate-y-[-4px] group-hover:border-yellow-400/30 ${
                step.status === 'Active' ? 'ring-2 ring-yellow-400/20' : ''
              }`}>
                <div className={`w-14 h-14 rounded-2xl mb-6 flex items-center justify-center transition-all ${
                  step.status === 'Active' ? 'bg-yellow-400 text-black shadow-lg shadow-yellow-400/20 rotate-3 group-hover:rotate-6' : 'bg-zinc-800 text-zinc-500'
                }`}>
                  {step.icon}
                </div>
                <h4 className="font-black text-white text-lg mb-1">{step.label}</h4>
                <p className="text-[11px] text-zinc-500 font-medium mb-6 line-clamp-1">{step.desc}</p>
                <div className="flex items-center justify-between mt-auto">
                  <span className={`text-[9px] font-black uppercase px-2 py-1 rounded-md tracking-widest ${
                    step.status === 'Active' ? 'bg-blue-500/10 text-blue-400' : 
                    step.status === 'Complete' ? 'bg-green-500/10 text-green-400' : 'bg-zinc-900 text-zinc-600'
                  }`}>
                    {step.status}
                  </span>
                  <ChevronRight className="w-4 h-4 text-zinc-800 group-hover:text-yellow-400 transition-colors" />
                </div>
              </GlassCard>
              {i < steps.length - 1 && (
                <div className="hidden md:block absolute top-1/2 -right-2 w-4 h-px bg-zinc-800 z-0" />
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Command Center Logs */}
      <div className="grid md:grid-cols-2 gap-8 pb-12">
        <GlassCard className="p-8">
          <div className="flex items-center justify-between mb-8">
            <h3 className="text-xs font-black text-zinc-500 uppercase tracking-widest flex items-center gap-3">
              <Terminal className="w-4 h-4 text-yellow-400" /> Self-Heal Logs
            </h3>
            <span className="text-[9px] font-black bg-green-500/10 text-green-500 px-3 py-1 rounded-full border border-green-500/10 tracking-widest">AGENT_HEALTH_OPTIMAL</span>
          </div>
          <div className="space-y-4">
             {[
               { time: '14:02', msg: 'Detected 404 on TikTok API. Retrying with proxy...', status: 'Fixed', type: 'error' },
               { time: '12:45', msg: 'n8n workflow index stale. Re-indexing vendor repo.', status: 'Done', type: 'info' },
               { time: '09:12', msg: 'Pauli audio clipping in Scene 2. Adjusting gain.', status: 'Fixed', type: 'warning' },
               { time: '08:00', msg: 'Pipeline triggered by morning RSS ingest.', status: 'Info', type: 'info' }
             ].map((log, i) => (
               <div key={i} className="flex gap-4 text-[11px] font-mono p-4 bg-black/40 rounded-2xl border border-white/5 hover:border-white/10 transition-colors group">
                 <span className="text-zinc-600 shrink-0 font-bold">{log.time}</span>
                 <span className="text-zinc-400 flex-1 leading-relaxed">
                   <span className={`font-black uppercase mr-2 ${
                     log.type === 'error' ? 'text-red-400' : log.type === 'warning' ? 'text-yellow-400' : 'text-blue-400'
                   }`}>[{log.type}]</span>
                   {log.msg}
                 </span>
                 <span className={`font-black uppercase tracking-tighter ${log.status === 'Fixed' ? 'text-blue-400' : 'text-zinc-700'}`}>{log.status}</span>
               </div>
             ))}
          </div>
        </GlassCard>

        <div className="space-y-6">
          <GlassCard className="p-8 flex items-center justify-between hover:bg-zinc-900/40 transition-colors group cursor-pointer">
            <div className="flex items-center gap-6">
              <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center border border-white/10 group-hover:scale-110 transition-transform">
                <Activity className="w-8 h-8 text-zinc-500 group-hover:text-yellow-400 transition-colors" />
              </div>
              <div>
                <h4 className="font-black text-xl text-white">System Config</h4>
                <p className="text-xs text-zinc-500 font-medium">Configure webhooks & CRM sync</p>
              </div>
            </div>
            <ArrowRight className="w-6 h-6 text-zinc-800 group-hover:text-yellow-400 transition-colors translate-x-0 group-hover:translate-x-2" />
          </GlassCard>

          <GlassCard className="p-8 border-dashed border-zinc-800 flex flex-col items-center justify-center text-center space-y-4">
             <div className="p-4 bg-zinc-900/50 rounded-full">
                <BarChart3 className="w-10 h-10 text-zinc-700" />
             </div>
             <p className="text-sm font-bold text-zinc-400">Add Integration</p>
             <p className="text-[11px] text-zinc-600 max-w-xs font-medium">Connect Pauli to your custom Python runner to track high-value leads in real-time.</p>
             <button className="w-full py-4 bg-zinc-900/50 border border-white/5 text-zinc-500 rounded-2xl text-[10px] font-black uppercase tracking-widest hover:bg-zinc-800 hover:text-white transition-all">Configure Webhook</button>
          </GlassCard>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
