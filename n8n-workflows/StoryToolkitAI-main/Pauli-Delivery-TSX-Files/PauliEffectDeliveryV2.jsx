import { useState, useEffect, useRef } from "react";

// ============================================================================
// THE PAULI EFFECT - CLIENT DELIVERY EXPERIENCE V2
// "You got sent for." - AI for people with purpose.
// Hormozi Value Stack + Liquid Animations + Purpose-First Messaging
// ============================================================================

// CONFIG - Update per client
const CONFIG = {
  company: {
    name: "The Pauli Effect",
    tagline: "AI for people with purpose.",
    mission: "Empowering social purpose companies, nonprofits, and forward-thinking humans to cross the AI bridge.",
    url: "https://thepaulieffect.com",
    donationUrl: "https://buymeacoffee.com/thepaulieffect",
  },
  client: {
    name: "Veronika N. Dimitrova",
    businessName: "Strategic Business Partner",
    siteUrl: "https://veronika-site.vercel.app",
  },
  urgency: {
    deadline: "December 31, 2024",
    deadlineShort: "NYE 2024",
  }
};

// Pauli mascot placeholder
const PAULI_PLACEHOLDER = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 280'%3E%3Crect fill='%231a1a2e' width='200' height='280' rx='20'/%3E%3Ctext x='100' y='140' text-anchor='middle' fill='%2322c55e' font-size='60'%3E🧔%3C/text%3E%3Ctext x='100' y='200' text-anchor='middle' fill='white' font-size='12'%3EPauli%3C/text%3E%3C/svg%3E";

// ============================================================================
// ICONS
// ============================================================================
const Icons = {
  ChevronLeft: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><path d="M15 18l-6-6 6-6"/></svg>,
  ChevronRight: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><path d="M9 18l6-6-6-6"/></svg>,
  Rocket: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-6 h-6"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/></svg>,
  Brain: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-6 h-6"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-1.54z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-1.54z"/></svg>,
  Shield: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-6 h-6"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>,
  Zap: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-6 h-6"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>,
  Sparkles: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>,
  Heart: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/></svg>,
  Link: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>,
  Share: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>,
  Download: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>,
  Twitter: () => <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>,
  LinkedIn: () => <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>,
  Code: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-6 h-6"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>,
  Users: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-6 h-6"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>,
  Gift: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-6 h-6"><polyline points="20 12 20 22 4 22 4 12"/><rect x="2" y="7" width="20" height="5"/><line x1="12" y1="22" x2="12" y2="7"/><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"/><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"/></svg>,
  Clock: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-6 h-6"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>,
  Check: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><polyline points="20 6 9 17 4 12"/></svg>,
  Star: () => <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>,
  Server: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>,
  Refresh: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/></svg>,
  Target: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-6 h-6"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>,
  Crown: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><path d="m2 4 3 12h14l3-12-6 7-4-7-4 7-6-7zm3 16h14"/></svg>,
  AlertCircle: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>,
  X: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>,
};

// ============================================================================
// STYLES - WITH LIQUID ANIMATIONS
// ============================================================================
const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=DM+Sans:wght@400;500;600;700&display=swap');
  
  .font-corleone { font-family: "Cinzel", serif; letter-spacing: 0.04em; }
  .font-body { font-family: "DM Sans", system-ui, sans-serif; }
  .pauli-perspective { perspective: 2000px; }
  .pauli-book-page { transform-origin: left center; transform-style: preserve-3d; }
  .pauli-page-flip-next { animation: pauliPageFlipNext 0.6s ease-out; }
  .pauli-page-flip-prev { animation: pauliPageFlipPrev 0.6s ease-out; }
  
  @keyframes pauliPageFlipNext {
    0% { transform: rotateY(0deg) translateZ(0); }
    35% { transform: rotateY(-14deg) translateZ(20px) scale(0.99); box-shadow: 0 20px 40px rgba(0,0,0,0.6); }
    100% { transform: rotateY(0deg) translateZ(0); box-shadow: 0 10px 30px rgba(0,0,0,0.4); }
  }
  @keyframes pauliPageFlipPrev {
    0% { transform: rotateY(0deg) translateZ(0); }
    35% { transform: rotateY(14deg) translateZ(20px) scale(0.99); box-shadow: 0 20px 40px rgba(0,0,0,0.6); }
    100% { transform: rotateY(0deg) translateZ(0); }
  }
  @keyframes pulse-ring { 0%, 100% { transform: scale(0.8); opacity: 0.8; } 50% { transform: scale(1.2); opacity: 0.4; } }
  @keyframes float { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-10px) rotate(2deg); } }
  @keyframes blob-morph {
    0%, 100% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
    25% { border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%; }
    50% { border-radius: 50% 60% 30% 60% / 30% 60% 70% 40%; }
    75% { border-radius: 60% 40% 60% 30% / 70% 30% 50% 60%; }
  }
  @keyframes liquid-flow { 0% { transform: translateX(-100%) skewX(-15deg); } 100% { transform: translateX(200%) skewX(-15deg); } }
  @keyframes gradient-shift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
  @keyframes glow-pulse { 0%, 100% { box-shadow: 0 0 20px rgba(34, 197, 94, 0.3); } 50% { box-shadow: 0 0 40px rgba(34, 197, 94, 0.5); } }
  @keyframes countdown-pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.02); } }
  
  .animate-pulse-ring { animation: pulse-ring 2s ease-in-out infinite; }
  .animate-float { animation: float 4s ease-in-out infinite; }
  .animate-blob { animation: blob-morph 8s ease-in-out infinite; }
  .animate-gradient { background-size: 200% 200%; animation: gradient-shift 4s ease infinite; }
  .animate-glow-pulse { animation: glow-pulse 2s ease-in-out infinite; }
  .animate-countdown { animation: countdown-pulse 1s ease-in-out infinite; }
  
  .glass-card { background: rgba(255,255,255,0.03); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.08); }
  .gradient-text { background: linear-gradient(135deg, #22c55e 0%, #06b6d4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
  .glow-emerald { box-shadow: 0 0 40px rgba(34, 197, 94, 0.3); }
  .liquid-blob { animation: blob-morph 8s ease-in-out infinite; }
  .liquid-highlight { position: relative; overflow: hidden; }
  .liquid-highlight::after { content: ''; position: absolute; top: 0; left: 0; width: 50%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent); animation: liquid-flow 3s ease-in-out infinite; }
  
  .tier-recommended { position: relative; transform: scale(1.02); z-index: 10; }
  .tier-recommended::before { content: ''; position: absolute; inset: -2px; background: linear-gradient(135deg, #22c55e, #06b6d4, #22c55e); border-radius: inherit; z-index: -1; animation: gradient-shift 3s ease infinite; background-size: 200% 200%; }
  .urgency-bar { background: linear-gradient(90deg, #ef4444, #f97316, #ef4444); background-size: 200% 100%; animation: gradient-shift 2s ease infinite; }
`;

// ============================================================================
// LIQUID BLOB
// ============================================================================
const LiquidBlob = ({ className = "", color = "emerald", size = "w-64 h-64", delay = 0 }) => {
  const colors = { emerald: "bg-emerald-500/20", cyan: "bg-cyan-500/20", purple: "bg-purple-500/20", yellow: "bg-yellow-500/10" };
  return <div className={`absolute rounded-full blur-3xl ${colors[color]} ${size} liquid-blob ${className}`} style={{ animationDelay: `${delay}s` }} />;
};

// ============================================================================
// UTILITIES
// ============================================================================
const FadeIn = ({ children, delay = 0, className = "" }) => {
  const [visible, setVisible] = useState(false);
  useEffect(() => { const t = setTimeout(() => setVisible(true), delay); return () => clearTimeout(t); }, [delay]);
  return <div className={`transition-all duration-700 ${visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"} ${className}`}>{children}</div>;
};

// ============================================================================
// INTRO SCREEN
// ============================================================================
const IntroScreen = ({ onGoSeePauli, onRunHide }) => (
  <div className="min-h-screen bg-gray-950 flex flex-col items-center justify-center p-6 text-center relative overflow-hidden font-body">
    <LiquidBlob color="emerald" size="w-96 h-96" className="top-0 left-1/4 -translate-x-1/2 -translate-y-1/2" delay={0} />
    <LiquidBlob color="cyan" size="w-80 h-80" className="bottom-0 right-1/4 translate-x-1/2 translate-y-1/2" delay={2} />
    <LiquidBlob color="purple" size="w-64 h-64" className="top-1/2 right-0 translate-x-1/2" delay={4} />
    
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
      <div className="w-64 h-64 rounded-full border border-emerald-500/20 animate-pulse-ring" />
    </div>
    
    <FadeIn>
      <div className="relative">
        <div className="relative glass-card rounded-3xl p-8 max-w-sm mx-auto border border-emerald-500/20 animate-glow-pulse">
          <div className="absolute inset-0 rounded-3xl overflow-hidden"><div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-cyan-500/5" /></div>
          <div className="relative">
            <div className="w-28 h-36 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-gray-800 to-gray-900 flex items-center justify-center text-5xl shadow-2xl animate-float border border-white/5">🧔</div>
            <p className="text-xs text-emerald-400 tracking-widest uppercase font-semibold mb-2">Pauli wants to see you.</p>
            <h1 className="font-corleone text-4xl text-white mb-3">You got<br /><span className="gradient-text">sent for.</span></h1>
            <p className="text-gray-500 text-sm mb-6">Delivered for <span className="text-white font-medium">{CONFIG.client.name}</span></p>
            <div className="space-y-3">
              <button onClick={onGoSeePauli} className="w-full py-3 px-6 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-xl text-black font-semibold text-sm hover:opacity-90 transition-all shadow-lg shadow-emerald-500/30 liquid-highlight">Go See Pauli</button>
              <button onClick={onRunHide} className="w-full py-3 px-6 glass-card rounded-xl text-gray-400 font-medium text-sm hover:text-white hover:bg-white/5 transition-all">Run &amp; Hide</button>
            </div>
          </div>
        </div>
        <div className="mt-8 inline-flex items-center gap-2 px-4 py-2 glass-card rounded-full">
          <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center text-xs">🧔</div>
          <span className="text-gray-400 text-xs">{CONFIG.company.name}</span>
          <span className="text-gray-600 text-xs">• {CONFIG.company.tagline}</span>
        </div>
      </div>
    </FadeIn>
  </div>
);

// ============================================================================
// RUN & HIDE SCREEN
// ============================================================================
const RunHideScreen = ({ onCaught }) => {
  const [countdown, setCountdown] = useState(5);
  useEffect(() => {
    const interval = setInterval(() => {
      setCountdown((prev) => { if (prev <= 1) { clearInterval(interval); onCaught(); return 0; } return prev - 1; });
    }, 1000);
    return () => clearInterval(interval);
  }, [onCaught]);

  const crewMembers = [
    { name: "Pauli", role: "The Don", emoji: "🧔" },
    { name: "The Strategist", role: "Vision", emoji: "🧠" },
    { name: "The Builder", role: "Execution", emoji: "🛠️" },
    { name: "The Guardian", role: "Security", emoji: "🛡️" },
    { name: "The Storyteller", role: "Voice", emoji: "📜" },
  ];

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col items-center justify-center p-6 text-center relative overflow-hidden font-body">
      <LiquidBlob color="emerald" size="w-64 h-64" className="top-1/4 left-1/4" delay={0} />
      <LiquidBlob color="cyan" size="w-48 h-48" className="bottom-1/4 right-1/4" delay={1} />
      
      <FadeIn>
        <p className="text-red-400 text-xs uppercase tracking-widest mb-3 font-semibold">You can't hide from purpose.</p>
        <h2 className="font-corleone text-3xl text-white mb-8">The crew surrounds you.</h2>
      </FadeIn>

      <FadeIn delay={300}>
        <div className="relative w-64 h-64">
          <div className="absolute inset-0 rounded-full border border-emerald-500/20 animate-pulse-ring" />
          <div className="absolute inset-4 rounded-full border border-emerald-500/10 animate-pulse-ring" style={{ animationDelay: "0.5s" }} />
          {crewMembers.map((member, i) => {
            const angle = (i / crewMembers.length) * 2 * Math.PI - Math.PI / 2;
            const x = 128 + 100 * Math.cos(angle);
            const y = 128 + 100 * Math.sin(angle);
            return (
              <div key={member.name} className="absolute flex flex-col items-center" style={{ left: x, top: y, transform: "translate(-50%, -50%)", animation: `float ${3 + i * 0.5}s ease-in-out infinite`, animationDelay: `${i * 0.2}s` }}>
                <div className="w-14 h-14 rounded-full glass-card flex items-center justify-center text-2xl border border-white/10">{member.emoji}</div>
                <span className="mt-2 text-xs text-white font-medium">{member.name}</span>
                <span className="text-[10px] text-gray-500">{member.role}</span>
              </div>
            );
          })}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-28 h-28 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center">
              <p className="text-[10px] text-emerald-200 text-center px-3 leading-relaxed">We surround you<br />with good systems,<br />not pressure.</p>
            </div>
          </div>
        </div>
      </FadeIn>

      <FadeIn delay={500}><p className="text-xs text-gray-600 animate-pulse mt-8">Redirecting you to Pauli in {countdown}...</p></FadeIn>
    </div>
  );
};

// ============================================================================
// SOCIAL SHARE CARD
// ============================================================================
const SocialShareCard = ({ clientName, siteUrl, onClose }) => {
  const [copied, setCopied] = useState(false);
  const shareText = `I got sent for by @ThePauliEffect 🧔\n\nMy new AI-powered site just dropped. Built by a purpose-driven crew that actually lets you own your code.\n\n${siteUrl}\n\n#ThePauliEffect #AIForGood`;
  const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}`;
  const linkedInUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(siteUrl)}`;
  const copyToClipboard = () => { navigator.clipboard.writeText(shareText); setCopied(true); setTimeout(() => setCopied(false), 2000); };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4 font-body">
      <FadeIn>
        <div className="max-w-md w-full glass-card rounded-3xl p-6 border border-emerald-500/20">
          <div className="flex justify-between items-start mb-6">
            <div><p className="text-xs text-emerald-400 tracking-wider uppercase font-semibold">Share Your Win</p><h3 className="font-corleone text-2xl text-white mt-1">I Got Sent For.</h3></div>
            <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors text-2xl leading-none">&times;</button>
          </div>
          <div className="bg-gradient-to-br from-gray-900 to-black rounded-2xl p-5 mb-6 border border-white/5">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center text-xl">🧔</div>
              <div><p className="text-white font-semibold text-sm">{clientName}</p><p className="text-gray-500 text-xs">just got sent for</p></div>
            </div>
            <p className="text-gray-300 text-sm mb-3">My new AI-powered site just dropped. Built by a purpose-driven crew that actually lets you own your code. 🚀</p>
            <div className="flex items-center gap-2 text-emerald-400 text-xs"><Icons.Link /><span className="truncate">{siteUrl}</span></div>
          </div>
          <div className="space-y-3">
            <a href={twitterUrl} target="_blank" rel="noreferrer" className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-black rounded-xl text-white font-medium text-sm hover:bg-gray-900 transition-colors border border-white/10"><Icons.Twitter />Share on X / Twitter</a>
            <a href={linkedInUrl} target="_blank" rel="noreferrer" className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-[#0077B5] rounded-xl text-white font-medium text-sm hover:bg-[#006399] transition-colors"><Icons.LinkedIn />Share on LinkedIn</a>
            <button onClick={copyToClipboard} className="w-full flex items-center justify-center gap-2 px-4 py-3 glass-card rounded-xl text-white font-medium text-sm hover:bg-white/10 transition-colors">{copied ? <Icons.Check /> : <Icons.Share />}{copied ? "Copied!" : "Copy to Clipboard"}</button>
          </div>
          <p className="text-center text-xs text-gray-600 mt-4">Help us help more purpose-driven projects. 💚</p>
        </div>
      </FadeIn>
    </div>
  );
};

// ============================================================================
// SLIDES
// ============================================================================
const TitleSlide = ({ clientName }) => (
  <div className="flex flex-col items-center justify-center h-full text-center px-6 relative overflow-hidden">
    <div className="absolute inset-0 pointer-events-none">
      <div className="absolute top-10 left-10 w-32 h-32 bg-emerald-500/10 rounded-full blur-3xl liquid-blob" />
      <div className="absolute bottom-10 right-10 w-24 h-24 bg-cyan-500/10 rounded-full blur-3xl liquid-blob" style={{ animationDelay: "2s" }} />
    </div>
    <FadeIn><div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/10 rounded-full text-emerald-400 text-sm font-medium mb-6 border border-emerald-500/20"><Icons.Sparkles /><span>{CONFIG.company.name}</span></div></FadeIn>
    <FadeIn delay={200}><h1 className="font-corleone text-4xl md:text-5xl text-white mb-4 leading-tight">Your <span className="gradient-text">purpose-driven site</span><br />is ready.</h1></FadeIn>
    <FadeIn delay={400}><p className="text-base text-gray-400 max-w-lg mb-6 leading-relaxed">Built by a crew that only works with people and organizations that actually have a purpose. You own the code. You own the data. You own the future.</p></FadeIn>
    <FadeIn delay={600}><p className="text-sm text-gray-600">Delivered for <span className="text-white font-medium">{clientName}</span></p></FadeIn>
  </div>
);

// PROBLEM SLIDE - WITH "YOU HAVE A PURPOSE" HERO
const ProblemSlide = () => (
  <div className="h-full px-6 py-6 overflow-auto relative">
    <div className="absolute top-0 right-0 w-48 h-48 bg-red-500/5 rounded-full blur-3xl liquid-blob" />
    <FadeIn><span className="text-red-400 text-xs font-semibold uppercase tracking-wider">The Problem</span><h2 className="font-corleone text-2xl md:text-3xl text-white mt-2 mb-4">Why Pauli had to<br />get involved.</h2></FadeIn>
    
    {/* HERO: YOU HAVE A PURPOSE */}
    <FadeIn delay={100}>
      <div className="mb-4 p-4 rounded-xl border-2 border-emerald-500/30 bg-gradient-to-br from-emerald-500/10 to-cyan-500/5 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/5 to-transparent liquid-highlight" />
        <div className="relative flex items-start gap-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-400 flex-shrink-0"><Icons.Target /></div>
          <div>
            <h3 className="text-white font-bold text-base mb-1">You Have a Purpose.</h3>
            <p className="text-emerald-200/80 text-sm leading-relaxed">In a world drowning in noise and algorithm chasing, you actually stand for something. That's rare. That's powerful. That's why we only work with people like you.</p>
          </div>
        </div>
      </div>
    </FadeIn>
    
    <div className="grid grid-cols-2 gap-3 max-w-2xl">
      {[
        { icon: Icons.Clock, title: "Websites Wait", desc: "They sit hoping someone visits." },
        { icon: Icons.Users, title: "Visitors Vanish", desc: "97% leave with no follow-up." },
        { icon: Icons.Code, title: "Code Hostage", desc: "You rent tools that lock you in." },
        { icon: Icons.Brain, title: "AI Gap", desc: "The bridge feels impossible." },
      ].map((item, i) => (
        <FadeIn key={i} delay={200 + i * 100}>
          <div className="glass-card rounded-xl p-3 border-red-500/10">
            <div className="text-red-400 mb-1.5"><item.icon /></div>
            <h3 className="text-white font-semibold text-xs mb-0.5">{item.title}</h3>
            <p className="text-gray-500 text-[10px] leading-relaxed">{item.desc}</p>
          </div>
        </FadeIn>
      ))}
    </div>
  </div>
);

// SOLUTION SLIDE - "WHAT TEAM PAULI BUILT FOR YOU"
const SolutionSlide = () => (
  <div className="h-full px-6 py-6 overflow-auto relative">
    <div className="absolute top-10 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-3xl liquid-blob" />
    <div className="absolute bottom-10 left-0 w-24 h-24 bg-cyan-500/10 rounded-full blur-3xl liquid-blob" style={{ animationDelay: "3s" }} />
    <FadeIn><span className="text-emerald-400 text-xs font-semibold uppercase tracking-wider">The Solution</span><h2 className="font-corleone text-2xl md:text-3xl text-white mt-2 mb-5">What Team Pauli<br /><span className="gradient-text">built for you.</span></h2></FadeIn>
    <div className="space-y-3 max-w-xl relative">
      {[
        { icon: Icons.Brain, title: "AI-Powered Agents", desc: "24/7 lead qualification, support, and nurturing that never sleeps.", gradient: "from-purple-500 to-pink-500" },
        { icon: Icons.Rocket, title: "Proactive Outreach", desc: "Your site hunts instead of waiting for visitors to appear.", gradient: "from-cyan-500 to-blue-500" },
        { icon: Icons.Shield, title: "Full Code Ownership", desc: "Every line of code is yours. No lock-in. No hostage situations. Ever.", gradient: "from-emerald-500 to-teal-500" },
      ].map((item, i) => (
        <FadeIn key={i} delay={200 + i * 150}>
          <div className="flex items-start gap-4 glass-card rounded-xl p-4 liquid-highlight">
            <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${item.gradient} flex items-center justify-center text-white flex-shrink-0`}><item.icon /></div>
            <div><h3 className="text-white font-semibold text-sm mb-1">{item.title}</h3><p className="text-gray-400 text-xs leading-relaxed">{item.desc}</p></div>
          </div>
        </FadeIn>
      ))}
    </div>
  </div>
);

const ProcessSlide = () => (
  <div className="h-full px-6 py-6 overflow-auto relative">
    <div className="absolute bottom-0 right-0 w-40 h-40 bg-cyan-500/10 rounded-full blur-3xl liquid-blob" />
    <FadeIn><span className="text-cyan-400 text-xs font-semibold uppercase tracking-wider">The Process</span><h2 className="font-corleone text-2xl md:text-3xl text-white mt-2 mb-5">Your 30-day<br />live run.</h2></FadeIn>
    <div className="grid grid-cols-2 gap-3 max-w-lg">
      {[
        { num: "01", title: "We Build", desc: "AI-powered site + agent dashboard", color: "emerald" },
        { num: "02", title: "You Test", desc: "30 days on our hosting, free", color: "cyan" },
        { num: "03", title: "You Choose", desc: "Partner, Self-Host, or Static", color: "purple" },
        { num: "04", title: "We Deliver", desc: "Full codebase transferred to you", color: "yellow" },
      ].map((step, i) => {
        const colors = { emerald: "text-emerald-400 border-emerald-500/30", cyan: "text-cyan-400 border-cyan-500/30", purple: "text-purple-400 border-purple-500/30", yellow: "text-yellow-400 border-yellow-500/30" };
        return (
          <FadeIn key={i} delay={200 + i * 100}>
            <div className={`glass-card rounded-xl p-3 border ${colors[step.color]}`}>
              <span className={`text-xs font-mono ${colors[step.color].split(' ')[0]}`}>{step.num}</span>
              <h3 className="text-white font-semibold text-sm mt-1.5 mb-0.5">{step.title}</h3>
              <p className="text-gray-500 text-[10px] leading-relaxed">{step.desc}</p>
            </div>
          </FadeIn>
        );
      })}
    </div>
  </div>
);

// ============================================================================
// PRICING SLIDE - HORMOZI 3-TIER VALUE STACK
// ============================================================================
const PricingSlide = () => {
  const [selectedTier, setSelectedTier] = useState(1);
  
  const tiers = [
    {
      id: 0, name: "Starter", subtitle: "DIY Path", price: "$1,997", priceNote: "one-time",
      description: "For the scrappy founder who wants to learn",
      valueStack: [
        { item: "Smart Site Template", value: "$3,000", included: true },
        { item: "Setup Guide & Docs", value: "$500", included: true },
        { item: "1 AI Agent (Basic)", value: "$1,000", included: true },
        { item: "Community Access", value: "$500", included: true },
        { item: "Source Code", value: "$2,000", included: true },
      ],
      totalValue: "$7,000", notIncluded: ["Done-for-you setup", "Custom AI agents", "Priority support"],
      color: "gray", badge: null,
    },
    {
      id: 1, name: "Partner", subtitle: "Done With You", price: "$4,997", priceNote: "one-time",
      description: "For purpose-driven leaders ready to scale",
      valueStack: [
        { item: "Custom Smart Site", value: "$8,000", included: true },
        { item: "3 AI Agents (Advanced)", value: "$5,000", included: true },
        { item: "Agent Dashboard", value: "$3,000", included: true },
        { item: "Full Source Code", value: "$5,000", included: true },
        { item: "30-Day Live Run", value: "$2,000", included: true },
        { item: "Setup + Onboarding", value: "$1,500", included: true },
        { item: "Strategy Session", value: "$500", included: true },
      ],
      totalValue: "$25,000", notIncluded: [],
      extras: ["$997/yr hosting (optional)", "$2,497/yr retainer (optional)"],
      color: "emerald", badge: "MOST POPULAR", recommended: true,
    },
    {
      id: 2, name: "Enterprise", subtitle: "Done For You", price: "$12,997", priceNote: "one-time",
      description: "White glove for established organizations",
      valueStack: [
        { item: "Everything in Partner", value: "$25,000", included: true },
        { item: "Unlimited AI Agents", value: "$15,000", included: true },
        { item: "Custom Integrations", value: "$8,000", included: true },
        { item: "Dedicated Support", value: "$5,000", included: true },
        { item: "Quarterly Strategy", value: "$4,000", included: true },
        { item: "First Year Hosting", value: "$997", included: true },
      ],
      totalValue: "$58,000", notIncluded: [], color: "purple", badge: "BEST VALUE",
    },
  ];

  return (
    <div className="h-full px-4 py-4 overflow-auto relative">
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/2 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl liquid-blob -translate-x-1/2 -translate-y-1/2" />
        <div className="absolute bottom-0 right-0 w-48 h-48 bg-cyan-500/10 rounded-full blur-3xl liquid-blob translate-x-1/4 translate-y-1/4" style={{ animationDelay: "2s" }} />
      </div>
      
      <FadeIn>
        <div className="text-center mb-3">
          <span className="text-yellow-400 text-xs font-semibold uppercase tracking-wider">The Investment</span>
          <h2 className="font-corleone text-2xl text-white mt-1">The Offer You Can't Refuse.</h2>
          <p className="text-gray-500 text-xs mt-1 italic">(but you probably shouldn't)</p>
        </div>
      </FadeIn>

      <FadeIn delay={100}>
        <div className="urgency-bar rounded-lg px-3 py-2 mb-3 flex items-center justify-center gap-2 animate-countdown">
          <Icons.AlertCircle className="w-4 h-4 text-white" />
          <span className="text-white text-xs font-bold">⏰ Expires {CONFIG.urgency.deadlineShort} • Prices increase Jan 1st</span>
        </div>
      </FadeIn>

      <div className="grid grid-cols-3 gap-2 mb-3 relative">
        {tiers.map((tier, i) => {
          const isRecommended = tier.recommended;
          const colorMap = { gray: "border-gray-700 bg-gray-900/50", emerald: "border-emerald-500/50 bg-emerald-500/5", purple: "border-purple-500/30 bg-purple-500/5" };
          return (
            <FadeIn key={tier.id} delay={200 + i * 100}>
              <div className={`relative rounded-xl p-2.5 cursor-pointer transition-all ${colorMap[tier.color]} ${isRecommended ? "tier-recommended" : ""} ${selectedTier === tier.id ? "ring-2 ring-emerald-500" : ""}`} onClick={() => setSelectedTier(tier.id)}>
                {tier.badge && <div className={`absolute -top-2 left-1/2 -translate-x-1/2 px-2 py-0.5 rounded-full text-[7px] font-bold ${isRecommended ? "bg-emerald-500 text-black" : "bg-purple-500 text-white"}`}>{tier.badge}</div>}
                <div className="text-center mb-1.5 pt-1">
                  <h3 className={`font-bold text-xs ${isRecommended ? "text-emerald-400" : "text-white"}`}>{tier.name}</h3>
                  <p className="text-gray-500 text-[8px]">{tier.subtitle}</p>
                </div>
                <div className="text-center mb-1.5">
                  <div className={`text-lg font-bold ${isRecommended ? "text-white" : "text-gray-300"}`}>{tier.price}</div>
                  <div className="text-[8px] text-gray-500">{tier.priceNote}</div>
                </div>
                <div className="text-center mb-1.5 py-0.5 rounded bg-black/30">
                  <span className="text-[8px] text-gray-500">Value: </span>
                  <span className="text-[9px] text-gray-400 line-through">{tier.totalValue}</span>
                </div>
                <div className="space-y-0.5">
                  {tier.valueStack.slice(0, 3).map((item, idx) => (
                    <div key={idx} className="flex items-center gap-1 text-[8px]">
                      <span className="text-emerald-400">✓</span>
                      <span className="text-gray-400 truncate">{item.item}</span>
                    </div>
                  ))}
                  {tier.valueStack.length > 3 && <div className="text-[8px] text-gray-500 pl-3">+{tier.valueStack.length - 3} more...</div>}
                </div>
              </div>
            </FadeIn>
          );
        })}
      </div>

      <FadeIn delay={500}>
        <div className="glass-card rounded-xl p-3 border border-emerald-500/20">
          <div className="flex items-center justify-between mb-2">
            <div>
              <span className="text-emerald-400 text-xs font-semibold">{tiers[selectedTier].name} Package</span>
              <p className="text-gray-500 text-[9px]">{tiers[selectedTier].description}</p>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-white">{tiers[selectedTier].price}</div>
              <div className="text-[8px] text-gray-500 line-through">Value: {tiers[selectedTier].totalValue}</div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-[9px]">
            {tiers[selectedTier].valueStack.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <span className="flex items-center gap-1 text-gray-300"><span className="text-emerald-400">✓</span>{item.item}</span>
                <span className="text-gray-600 line-through">{item.value}</span>
              </div>
            ))}
          </div>
          {tiers[selectedTier].extras && (
            <div className="mt-2 pt-2 border-t border-white/5">
              {tiers[selectedTier].extras.map((extra, idx) => (
                <div key={idx} className="flex items-center gap-1 text-[8px] text-gray-500"><Icons.Gift className="w-3 h-3" />{extra}</div>
              ))}
            </div>
          )}
        </div>
      </FadeIn>
    </div>
  );
};

const OwnershipSlide = () => (
  <div className="h-full px-6 py-6 overflow-auto relative">
    <div className="absolute top-0 left-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-3xl liquid-blob" />
    <FadeIn><span className="text-emerald-400 text-xs font-semibold uppercase tracking-wider">Your Rights</span><h2 className="font-corleone text-2xl md:text-3xl text-white mt-2 mb-5">You own<br />everything.</h2></FadeIn>
    <div className="space-y-3 max-w-md">
      {[
        { icon: Icons.Code, title: "Full Source Code", desc: "Every line is yours. Forever. No exceptions." },
        { icon: Icons.Shield, title: "Zero Lock-In", desc: "Take it anywhere. Any developer can work on it." },
        { icon: Icons.Server, title: "Host Anywhere", desc: "Our servers, yours, Vercel, AWS—your choice." },
        { icon: Icons.Heart, title: "Backup with Permission", desc: "We keep a secure copy. Just in case." },
      ].map((item, i) => (
        <FadeIn key={i} delay={200 + i * 100}>
          <div className="flex items-start gap-4 glass-card rounded-xl p-4 liquid-highlight">
            <div className="w-9 h-9 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-400 flex-shrink-0"><item.icon /></div>
            <div><h3 className="text-white font-semibold text-sm mb-0.5">{item.title}</h3><p className="text-gray-500 text-xs">{item.desc}</p></div>
          </div>
        </FadeIn>
      ))}
    </div>
  </div>
);

// FINAL SLIDE - "PAULI FINDS YOU" CLOSER
const ScratchRevealSlide = ({ clientName, siteUrl, onShare }) => {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const isDrawingRef = useRef(false);
  const [hasScratched, setHasScratched] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;
    const rect = container.getBoundingClientRect();
    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;
    ctx.scale(dpr, dpr);
    ctx.fillStyle = "#0a0a0f";
    ctx.fillRect(0, 0, rect.width, rect.height);
    const gradient = ctx.createLinearGradient(0, 0, rect.width, rect.height);
    gradient.addColorStop(0, "#22c55e");
    gradient.addColorStop(1, "#06b6d4");
    ctx.globalAlpha = 0.9;
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, rect.width, rect.height);
    ctx.globalAlpha = 1;
    ctx.fillStyle = "rgba(0,0,0,0.4)";
    ctx.font = "bold 14px system-ui";
    ctx.textAlign = "center";
    ctx.fillText("✨ SCRATCH TO REVEAL ✨", rect.width / 2, rect.height / 2);
  }, []);

  const checkScratchPercent = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const pixels = imageData.data;
    let transparent = 0;
    for (let i = 3; i < pixels.length; i += 4) { if (pixels[i] < 128) transparent++; }
    const percent = (transparent / (pixels.length / 4)) * 100;
    if (percent > 30 && !hasScratched) setHasScratched(true);
  };

  const scratchAt = (clientX, clientY) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const rect = canvas.getBoundingClientRect();
    const x = (clientX - rect.left);
    const y = (clientY - rect.top);
    ctx.globalCompositeOperation = "destination-out";
    ctx.beginPath();
    ctx.arc(x, y, 30, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalCompositeOperation = "source-over";
    checkScratchPercent();
  };

  const handlePointerDown = (e) => { isDrawingRef.current = true; scratchAt(e.clientX, e.clientY); };
  const handlePointerMove = (e) => { if (!isDrawingRef.current) return; scratchAt(e.clientX, e.clientY); };
  const handlePointerUp = () => { isDrawingRef.current = false; };

  return (
    <div className="h-full px-6 py-5 overflow-auto relative">
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/4 left-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-3xl liquid-blob" />
        <div className="absolute bottom-1/4 right-0 w-24 h-24 bg-cyan-500/10 rounded-full blur-3xl liquid-blob" style={{ animationDelay: "2s" }} />
      </div>
      
      <FadeIn><span className="text-emerald-400 text-xs font-semibold uppercase tracking-wider">Your Site</span><h2 className="font-corleone text-xl text-white mt-1 mb-3">Scratch to reveal.</h2></FadeIn>

      <FadeIn delay={200}>
        <div ref={containerRef} className="relative w-full max-w-sm mx-auto aspect-video rounded-2xl overflow-hidden shadow-2xl">
          <div className="absolute inset-0 bg-gradient-to-br from-gray-900 to-black flex flex-col items-center justify-center p-4">
            <div className="inline-flex items-center gap-1 px-2 py-1 bg-emerald-500/20 rounded-full text-emerald-400 text-[10px] font-medium mb-3"><Icons.Sparkles className="w-3 h-3" />Live</div>
            <h3 className="text-white font-semibold text-sm text-center mb-1">{CONFIG.client.businessName}</h3>
            <p className="text-gray-500 text-xs mb-3">Built to serve your community.</p>
            <div className="flex items-center gap-1 text-emerald-400 text-xs"><Icons.Link className="w-3 h-3" /><span className="truncate max-w-[150px]">{siteUrl}</span></div>
          </div>
          <canvas ref={canvasRef} className="absolute inset-0 cursor-crosshair touch-none" onPointerDown={handlePointerDown} onPointerMove={handlePointerMove} onPointerUp={handlePointerUp} onPointerLeave={handlePointerUp} />
        </div>
      </FadeIn>

      {hasScratched && (
        <FadeIn delay={0}>
          <div className="flex flex-col gap-2 mt-3 max-w-sm mx-auto">
            <a href={siteUrl} target="_blank" rel="noreferrer" className="w-full py-2.5 px-4 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-xl text-black font-semibold text-sm text-center hover:opacity-90 transition-all shadow-lg shadow-emerald-500/30 liquid-highlight">Visit My Live Site</a>
            <button onClick={onShare} className="w-full py-2.5 px-4 glass-card rounded-xl text-white font-medium text-sm flex items-center justify-center gap-2 hover:bg-white/10 transition-colors"><Icons.Share />Share: I Got Sent For</button>
          </div>
        </FadeIn>
      )}

      {/* "PAULI FINDS YOU" CLOSER */}
      <FadeIn delay={400}>
        <div className="mt-4 text-center max-w-sm mx-auto">
          <div className="glass-card rounded-xl p-4 border border-emerald-500/20">
            <p className="text-gray-500 text-xs mb-1">But wait... how do I find Pauli?</p>
            <p className="text-white font-semibold text-sm mb-1">You don't.</p>
            <p className="gradient-text font-corleone text-lg">Pauli finds you.</p>
            <div className="mt-3 pt-3 border-t border-white/5">
              <p className="text-gray-400 text-xs">We'll be in touch. <span className="text-emerald-400">Enjoy your site.</span> 🧔</p>
            </div>
          </div>
        </div>
      </FadeIn>
    </div>
  );
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================
export default function PauliEffectDelivery() {
  const [mode, setMode] = useState("intro");
  const [currentSlide, setCurrentSlide] = useState(0);
  const [flipDirection, setFlipDirection] = useState(null);
  const [showShareModal, setShowShareModal] = useState(false);

  const slides = [
    { id: "title", component: TitleSlide },
    { id: "problem", component: ProblemSlide },
    { id: "solution", component: SolutionSlide },
    { id: "process", component: ProcessSlide },
    { id: "pricing", component: PricingSlide },
    { id: "ownership", component: OwnershipSlide },
    { id: "reveal", component: ScratchRevealSlide },
  ];

  const goToSlide = (index, dir) => { if (index < 0 || index >= slides.length) return; setFlipDirection(dir); setCurrentSlide(index); setTimeout(() => setFlipDirection(null), 650); };
  const nextSlide = () => { if (currentSlide < slides.length - 1) goToSlide(currentSlide + 1, "next"); };
  const prevSlide = () => { if (currentSlide > 0) goToSlide(currentSlide - 1, "prev"); };

  useEffect(() => {
    if (mode !== "deck") return;
    const handleKeyDown = (e) => {
      if (e.key === "ArrowRight" || e.key === " ") { e.preventDefault(); nextSlide(); }
      else if (e.key === "ArrowLeft") { e.preventDefault(); prevSlide(); }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [mode, currentSlide]);

  useEffect(() => { const styleEl = document.createElement("style"); styleEl.textContent = styles; document.head.appendChild(styleEl); return () => document.head.removeChild(styleEl); }, []);

  if (mode === "intro") return <IntroScreen onGoSeePauli={() => setMode("deck")} onRunHide={() => setMode("runHide")} />;
  if (mode === "runHide") return <RunHideScreen onCaught={() => setMode("deck")} />;

  const CurrentSlide = slides[currentSlide].component;

  return (
    <div className="min-h-screen bg-gray-950 text-white font-body">
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <LiquidBlob color="emerald" size="w-64 h-64" className="top-0 left-1/4" delay={0} />
        <LiquidBlob color="cyan" size="w-64 h-64" className="bottom-0 right-1/4" delay={2} />
        <LiquidBlob color="purple" size="w-48 h-48" className="top-1/2 right-0" delay={4} />
      </div>

      <header className="fixed top-0 left-0 right-0 z-40 p-4 flex justify-between items-center bg-black/60 backdrop-blur-xl border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center text-lg shadow-lg shadow-emerald-500/30">🧔</div>
          <div className="hidden sm:block"><p className="font-corleone text-sm text-white">{CONFIG.company.name}</p><p className="text-[10px] text-gray-500">{CONFIG.company.tagline}</p></div>
        </div>
        <div className="flex gap-1.5">{slides.map((_, i) => (<div key={i} className={`h-1.5 rounded-full transition-all duration-300 ${i <= currentSlide ? "w-5 bg-gradient-to-r from-emerald-500 to-cyan-500" : "w-2 bg-gray-700"}`} />))}</div>
        <div className="text-xs text-gray-500 font-mono">{String(currentSlide + 1).padStart(2, "0")} / {String(slides.length).padStart(2, "0")}</div>
      </header>

      <main className="pt-20 pb-24 min-h-screen pauli-perspective">
        <div className="h-[calc(100vh-176px)] flex items-center justify-center px-4">
          <div key={currentSlide} className={`pauli-book-page w-full max-w-2xl h-full glass-card rounded-3xl shadow-2xl shadow-black/50 overflow-hidden ${flipDirection === "next" ? "pauli-page-flip-next" : flipDirection === "prev" ? "pauli-page-flip-prev" : ""}`}>
            <CurrentSlide clientName={CONFIG.client.name} siteUrl={CONFIG.client.siteUrl} onShare={() => setShowShareModal(true)} />
          </div>
        </div>
      </main>

      <footer className="fixed bottom-0 left-0 right-0 p-4 flex justify-between items-center bg-black/60 backdrop-blur-xl border-t border-white/5">
        <button onClick={prevSlide} disabled={currentSlide === 0} className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all ${currentSlide === 0 ? "bg-gray-800/50 text-gray-600" : "bg-gray-800 text-white hover:bg-gray-700"}`}><Icons.ChevronLeft /><span className="hidden sm:inline">Previous</span></button>
        <div className="flex gap-1.5">{slides.map((_, i) => (<button key={i} onClick={() => goToSlide(i, i > currentSlide ? "next" : "prev")} className={`w-2 h-2 rounded-full transition-all ${i === currentSlide ? "w-5 bg-emerald-500" : "bg-gray-700 hover:bg-gray-600"}`} />))}</div>
        <button onClick={nextSlide} disabled={currentSlide === slides.length - 1} className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all ${currentSlide === slides.length - 1 ? "bg-gray-800/50 text-gray-600" : "bg-gradient-to-r from-emerald-500 to-cyan-500 text-black hover:opacity-90 liquid-highlight"}`}><span className="hidden sm:inline">{currentSlide === slides.length - 2 ? "Reveal" : "Next"}</span><Icons.ChevronRight /></button>
      </footer>

      {showShareModal && <SocialShareCard clientName={CONFIG.client.name} siteUrl={CONFIG.client.siteUrl} onClose={() => setShowShareModal(false)} />}
    </div>
  );
}
