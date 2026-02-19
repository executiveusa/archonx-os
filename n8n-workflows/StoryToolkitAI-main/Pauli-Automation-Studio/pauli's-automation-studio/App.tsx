
import React, { useState, useEffect } from 'react';
import { AppTab } from './types';
import { TABS } from './constants';
import Dashboard from './components/Dashboard';
import ScriptLab from './components/ScriptLab';
import Brainstorm from './components/Brainstorm';
import VisualStudio from './components/VisualStudio';
import ImageAnalyzer from './components/ImageAnalyzer';
import FactChecker from './components/FactChecker';
import ProductionLab from './components/ProductionLab';
import { ShieldCheck, Cpu, LayoutDashboard, Menu, X } from 'lucide-react';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<AppTab>(AppTab.Dashboard);
  const [hasApiKey, setHasApiKey] = useState<boolean>(false);
  const [activeScenePrompt, setActiveScenePrompt] = useState<string>('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  useEffect(() => {
    const checkApiKey = async () => {
      if (window.aistudio) {
        const selected = await window.aistudio.hasSelectedApiKey();
        setHasApiKey(selected);
      } else {
        setHasApiKey(true);
      }
    };
    checkApiKey();
  }, []);

  const handleSelectKey = async () => {
    if (window.aistudio) {
      await window.aistudio.openSelectKey();
      setHasApiKey(true);
    }
  };

  const handleAnimateRequest = (prompt: string) => {
    setActiveScenePrompt(prompt);
    setActiveTab(AppTab.Production);
  };

  const renderContent = () => {
    switch (activeTab) {
      case AppTab.Dashboard: return <Dashboard onAction={(tab) => setActiveTab(tab)} />;
      case AppTab.Generator: return <ScriptLab onAnimate={handleAnimateRequest} />;
      case AppTab.Brainstorm: return <Brainstorm />;
      case AppTab.Visuals: return <VisualStudio />;
      case AppTab.Production: return <ProductionLab initialPrompt={activeScenePrompt} />;
      case AppTab.Analysis: return <ImageAnalyzer />;
      case AppTab.Verification: return <FactChecker />;
      default: return <Dashboard onAction={(tab) => setActiveTab(tab)} />;
    }
  };

  return (
    <div className="min-h-screen bg-black text-white font-sans selection:bg-yellow-400 selection:text-black">
      {/* Dynamic Background Glows */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-yellow-400/10 blur-[120px] rounded-full animate-pulse" />
        <div className="absolute top-[40%] -right-[10%] w-[50%] h-[50%] bg-blue-500/5 blur-[150px] rounded-full" />
      </div>

      <div className="relative z-10 flex h-screen overflow-hidden">
        {/* Mobile Sidebar Overlay */}
        {isSidebarOpen && (
          <div 
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden"
            onClick={() => setIsSidebarOpen(false)}
          />
        )}

        {/* Sidebar / Desktop Navigation */}
        <aside className={`
          fixed inset-y-0 left-0 z-50 w-72 bg-zinc-950 border-r border-zinc-800 transform transition-transform duration-300 md:relative md:translate-x-0
          ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}>
          <div className="p-8 flex items-center justify-between border-b border-zinc-900">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-yellow-400 rounded-2xl flex items-center justify-center shadow-[0_0_20px_rgba(250,204,21,0.3)]">
                <Cpu className="text-black w-6 h-6" />
              </div>
              <h1 className="heading-font text-2xl tracking-tighter text-yellow-400">PAULI STUDIO</h1>
            </div>
            <button className="md:hidden text-zinc-400" onClick={() => setIsSidebarOpen(false)}>
              <X className="w-6 h-6" />
            </button>
          </div>

          <nav className="flex-1 p-6 space-y-2 overflow-y-auto">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id);
                  setIsSidebarOpen(false);
                }}
                className={`w-full flex items-center gap-3 p-4 rounded-2xl transition-all group ${
                  activeTab === tab.id 
                    ? 'bg-yellow-400 text-black font-black shadow-lg scale-[1.02]' 
                    : 'text-zinc-500 hover:bg-zinc-900/50 hover:text-white'
                }`}
              >
                {tab.icon}
                <span className="font-bold text-sm tracking-tight">{tab.label}</span>
              </button>
            ))}
          </nav>

          {!hasApiKey && (
            <div className="p-6 border-t border-zinc-900">
              <button 
                onClick={handleSelectKey}
                className="w-full bg-zinc-900 hover:bg-zinc-800 p-3 rounded-2xl text-[10px] font-black uppercase tracking-widest border border-zinc-800 transition-colors flex items-center justify-center gap-2"
              >
                <ShieldCheck className="w-4 h-4 text-yellow-400" />
                <span>Connect Key</span>
              </button>
            </div>
          )}
        </aside>

        {/* Main Content */}
        <div className="flex-1 flex flex-col min-w-0">
          <header className="px-8 py-6 flex justify-between items-center md:hidden border-b border-zinc-900 bg-black/40 backdrop-blur-xl">
            <button onClick={() => setIsSidebarOpen(true)}>
              <Menu className="w-6 h-6" />
            </button>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-yellow-400 rounded-xl flex items-center justify-center">
                <Cpu className="text-black w-5 h-5" />
              </div>
              <span className="heading-font text-lg text-yellow-400">PAULI</span>
            </div>
            <div className="w-6" /> {/* Placeholder for balance */}
          </header>

          <main className="flex-1 overflow-y-auto custom-scrollbar pt-8 md:pt-12 px-4 md:px-12 pb-32">
            <div className="max-w-6xl mx-auto">
              {renderContent()}
            </div>
          </main>

          {/* Bottom Navigation (Mobile Only) */}
          <nav className="md:hidden fixed bottom-6 left-1/2 -translate-x-1/2 w-[90%] max-w-sm h-16 bg-zinc-950/80 backdrop-blur-2xl border border-white/10 rounded-3xl flex items-center justify-around px-6 z-40 shadow-2xl">
            {TABS.slice(0, 4).map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`p-3 rounded-2xl transition-all ${
                  activeTab === tab.id ? 'bg-yellow-400 text-black scale-110 shadow-lg' : 'text-zinc-500'
                }`}
              >
                {tab.icon}
              </button>
            ))}
          </nav>
        </div>
      </div>
    </div>
  );
};

export default App;
