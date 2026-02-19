import { useState, useEffect, useRef } from "react";

// ============================================================================
// THE PAULI EFFECT - CLIENT DELIVERY EXPERIENCE
// "You got sent for." - AI for people with purpose.
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
};

// Pauli mascot as base64 placeholder (replace with actual image import)
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
};

// ============================================================================
// STYLES (Injected)
// ============================================================================
const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=DM+Sans:wght@400;500;600;700&display=swap');
  
  .font-corleone {
    font-family: "Cinzel", "Cormorant Garamond", serif;
    letter-spacing: 0.04em;
  }
  
  .font-body {
    font-family: "DM Sans", system-ui, sans-serif;
  }
  
  .pauli-perspective {
    perspective: 2000px;
  }
  
  .pauli-book-page {
    transform-origin: left center;
    transform-style: preserve-3d;
  }
  
  .pauli-page-flip-next {
    animation: pauliPageFlipNext 0.6s ease-out;
  }
  
  .pauli-page-flip-prev {
    animation: pauliPageFlipPrev 0.6s ease-out;
  }
  
  @keyframes pauliPageFlipNext {
    0% { transform: rotateY(0deg) translateZ(0); box-shadow: 0 0 0 rgba(0,0,0,0); }
    35% { transform: rotateY(-14deg) translateZ(20px) scale(0.99); box-shadow: 0 20px 40px rgba(0,0,0,0.6); }
    100% { transform: rotateY(0deg) translateZ(0); box-shadow: 0 10px 30px rgba(0,0,0,0.4); }
  }
  
  @keyframes pauliPageFlipPrev {
    0% { transform: rotateY(0deg) translateZ(0); box-shadow: 0 0 0 rgba(0,0,0,0); }
    35% { transform: rotateY(14deg) translateZ(20px) scale(0.99); box-shadow: 0 20px 40px rgba(0,0,0,0.6); }
    100% { transform: rotateY(0deg) translateZ(0); box-shadow: 0 10px 30px rgba(0,0,0,0.4); }
  }
  
  @keyframes pulse-ring {
    0% { transform: scale(0.8); opacity: 0.8; }
    50% { transform: scale(1.2); opacity: 0.4; }
    100% { transform: scale(0.8); opacity: 0.8; }
  }
  
  @keyframes float {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-10px) rotate(2deg); }
  }
  
  .animate-pulse-ring {
    animation: pulse-ring 2s ease-in-out infinite;
  }
  
  .animate-float {
    animation: float 4s ease-in-out infinite;
  }
  
  .glass-card {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.08);
  }
  
  .gradient-text {
    background: linear-gradient(135deg, #22c55e 0%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .glow-emerald {
    box-shadow: 0 0 40px rgba(34, 197, 94, 0.3), 0 0 80px rgba(34, 197, 94, 0.1);
  }
`;

// ============================================================================
// UTILITIES
// ============================================================================
const FadeIn = ({ children, delay = 0, className = "" }) => {
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setVisible(true), delay);
    return () => clearTimeout(t);
  }, [delay]);
  return (
    <div className={`transition-all duration-700 ${visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"} ${className}`}>
      {children}
    </div>
  );
};

// ============================================================================
// INTRO SCREEN - "YOU GOT SENT FOR"
// ============================================================================
const IntroScreen = ({ onGoSeePauli, onRunHide }) => (
  <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-950 via-black to-gray-900 text-white relative overflow-hidden font-body">
    {/* Background effects */}
    <div className="pointer-events-none absolute inset-0">
      <div className="absolute -left-40 -top-40 w-96 h-96 bg-emerald-500/10 blur-3xl rounded-full" />
      <div className="absolute -right-40 bottom-0 w-96 h-96 bg-cyan-500/10 blur-3xl rounded-full" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] border border-emerald-500/5 rounded-full animate-pulse-ring" />
    </div>

    <div className="max-w-5xl w-full px-6 relative z-10 flex flex-col md:flex-row items-center gap-12">
      {/* Pauli Image */}
      <div className="flex-1 flex justify-center">
        <FadeIn>
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 rounded-3xl blur-2xl scale-110" />
            <div className="relative glass-card rounded-3xl p-6 glow-emerald">
              <div className="w-48 md:w-64 aspect-[3/4] bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl flex items-center justify-center overflow-hidden animate-float">
                <div className="text-8xl">🧔</div>
              </div>
              <div className="absolute -bottom-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-emerald-500 rounded-full text-xs font-semibold text-black">
                PAULI
              </div>
            </div>
          </div>
        </FadeIn>
      </div>

      {/* Content */}
      <div className="flex-1 text-center md:text-left">
        <FadeIn>
          <p className="text-xs tracking-[0.4em] uppercase text-emerald-400 mb-4 font-semibold">
            {CONFIG.company.name}
          </p>
        </FadeIn>
        
        <FadeIn delay={150}>
          <h1 className="font-corleone text-4xl md:text-6xl leading-tight mb-2">
            <span className="block text-gray-400 text-lg md:text-xl tracking-[0.3em] uppercase mb-2">
              You got sent for.
            </span>
            <span className="block text-white">
              PAULI WANTS<br />TO SEE YOU.
            </span>
          </h1>
        </FadeIn>
        
        <FadeIn delay={300}>
          <p className="text-sm md:text-base text-gray-400 mb-8 max-w-md leading-relaxed">
            A purpose-driven AI crew for social good organizations, nonprofits, and forward-thinking humans 
            ready to cross the AI bridge—with code and ownership intact.
          </p>
        </FadeIn>
        
        <FadeIn delay={450}>
          <div className="flex flex-col sm:flex-row gap-4 justify-center md:justify-start">
            <button
              onClick={onGoSeePauli}
              className="px-8 py-4 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 text-sm font-bold shadow-lg shadow-emerald-500/30 hover:shadow-emerald-500/50 hover:scale-105 transition-all duration-300 text-black"
            >
              Go See Pauli
            </button>
            <button
              onClick={onRunHide}
              className="px-8 py-4 rounded-xl border border-white/10 bg-white/5 text-sm font-semibold text-gray-100 hover:bg-white/10 hover:border-white/20 transition-all duration-300"
            >
              Run & Hide
            </button>
          </div>
        </FadeIn>
        
        <FadeIn delay={600}>
          <p className="text-xs text-gray-600 mt-6">
            Delivered for <span className="text-gray-400">{CONFIG.client.name}</span>
          </p>
        </FadeIn>
      </div>
    </div>
  </div>
);

// ============================================================================
// RUN & HIDE SCREEN - Easter Egg
// ============================================================================
const RunHideScreen = ({ onCaught }) => {
  const crew = [
    { name: "Pauli", role: "The Don", emoji: "🧔" },
    { name: "The Strategist", role: "Planning", emoji: "🧠" },
    { name: "The Builder", role: "Development", emoji: "🛠️" },
    { name: "The Guardian", role: "Security", emoji: "🛡️" },
    { name: "The Storyteller", role: "Content", emoji: "📜" },
  ];

  useEffect(() => {
    const timer = setTimeout(onCaught, 5000);
    return () => clearTimeout(timer);
  }, [onCaught]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-black via-gray-950 to-black text-white relative overflow-hidden font-body">
      {/* Radar effect */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-64 h-64 rounded-full border border-emerald-500/20 animate-ping" style={{ animationDuration: '3s' }} />
        <div className="absolute w-48 h-48 rounded-full border border-emerald-500/30 animate-ping" style={{ animationDuration: '2s', animationDelay: '0.5s' }} />
      </div>

      <div className="relative z-10 flex flex-col items-center gap-8 px-6">
        <FadeIn>
          <p className="text-xs tracking-[0.4em] uppercase text-gray-500 font-semibold">
            Nice try.
          </p>
        </FadeIn>
        
        <FadeIn delay={150}>
          <h2 className="font-corleone text-3xl md:text-4xl text-center leading-tight">
            You can't run from<br />
            <span className="gradient-text">a purpose-driven crew.</span>
          </h2>
        </FadeIn>

        <FadeIn delay={300}>
          <div className="relative w-72 h-72 md:w-80 md:h-80">
            {crew.map((member, i) => {
              const angle = (i / crew.length) * Math.PI * 2 - Math.PI / 2;
              const radius = 110;
              const x = 140 + Math.cos(angle) * radius;
              const y = 140 + Math.sin(angle) * radius;
              return (
                <div
                  key={member.name}
                  className="absolute flex flex-col items-center"
                  style={{
                    left: x,
                    top: y,
                    transform: "translate(-50%, -50%)",
                    animation: `float ${3 + i * 0.5}s ease-in-out infinite`,
                    animationDelay: `${i * 0.2}s`
                  }}
                >
                  <div className="w-14 h-14 rounded-full glass-card flex items-center justify-center text-2xl border border-white/10">
                    {member.emoji}
                  </div>
                  <span className="mt-2 text-xs text-white font-medium">{member.name}</span>
                  <span className="text-[10px] text-gray-500">{member.role}</span>
                </div>
              );
            })}
            
            {/* Center message */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-28 h-28 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center">
                <p className="text-[10px] text-emerald-200 text-center px-3 leading-relaxed">
                  We surround you<br />with good systems,<br />not pressure.
                </p>
              </div>
            </div>
          </div>
        </FadeIn>

        <FadeIn delay={500}>
          <p className="text-xs text-gray-600 animate-pulse">
            Redirecting you to Pauli...
          </p>
        </FadeIn>
      </div>
    </div>
  );
};

// ============================================================================
// SHAREABLE SOCIAL CARD - "I GOT SENT FOR"
// ============================================================================
const SocialShareCard = ({ clientName, siteUrl, onClose }) => {
  const [copied, setCopied] = useState(false);
  
  const shareText = `I got sent for by @ThePauliEffect 🧔\n\nMy new AI-powered site just dropped. Built by a purpose-driven crew that actually lets you own your code.\n\n${siteUrl}\n\n#ThePauliEffect #AIForGood`;
  
  const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}`;
  const linkedInUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(siteUrl)}`;
  
  const copyToClipboard = () => {
    navigator.clipboard.writeText(shareText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4 font-body">
      <FadeIn>
        <div className="max-w-md w-full glass-card rounded-3xl p-6 border border-emerald-500/20">
          <div className="flex justify-between items-start mb-6">
            <div>
              <p className="text-xs text-emerald-400 tracking-wider uppercase font-semibold">Share Your Win</p>
              <h3 className="font-corleone text-2xl text-white mt-1">I Got Sent For.</h3>
            </div>
            <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors text-2xl leading-none">&times;</button>
          </div>
          
          {/* Preview Card */}
          <div className="bg-gradient-to-br from-gray-900 to-black rounded-2xl p-5 mb-6 border border-white/5">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center text-xl">🧔</div>
              <div>
                <p className="text-white font-semibold text-sm">{clientName}</p>
                <p className="text-gray-500 text-xs">just got sent for</p>
              </div>
            </div>
            <p className="text-gray-300 text-sm mb-3">
              My new AI-powered site just dropped. Built by a purpose-driven crew that actually lets you own your code. 🚀
            </p>
            <div className="flex items-center gap-2 text-emerald-400 text-xs">
              <Icons.Link />
              <span className="truncate">{siteUrl}</span>
            </div>
          </div>
          
          {/* Share Buttons */}
          <div className="space-y-3">
            <a
              href={twitterUrl}
              target="_blank"
              rel="noreferrer"
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-black rounded-xl text-white font-medium text-sm hover:bg-gray-900 transition-colors border border-white/10"
            >
              <Icons.Twitter />
              Share on X / Twitter
            </a>
            
            <a
              href={linkedInUrl}
              target="_blank"
              rel="noreferrer"
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-[#0077B5] rounded-xl text-white font-medium text-sm hover:bg-[#006399] transition-colors"
            >
              <Icons.LinkedIn />
              Share on LinkedIn
            </a>
            
            <button
              onClick={copyToClipboard}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 glass-card rounded-xl text-white font-medium text-sm hover:bg-white/10 transition-colors"
            >
              {copied ? <Icons.Check /> : <Icons.Share />}
              {copied ? "Copied!" : "Copy to Clipboard"}
            </button>
          </div>
          
          <p className="text-center text-xs text-gray-600 mt-4">
            Help us help more purpose-driven projects. 💚
          </p>
        </div>
      </FadeIn>
    </div>
  );
};

// ============================================================================
// SLIDES
// ============================================================================
const TitleSlide = ({ clientName }) => (
  <div className="flex flex-col items-center justify-center h-full text-center px-6">
    <FadeIn>
      <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/10 rounded-full text-emerald-400 text-sm font-medium mb-6 border border-emerald-500/20">
        <Icons.Sparkles />
        <span>{CONFIG.company.name}</span>
      </div>
    </FadeIn>
    <FadeIn delay={200}>
      <h1 className="font-corleone text-4xl md:text-5xl text-white mb-4 leading-tight">
        Your <span className="gradient-text">purpose-driven site</span>
        <br />is ready.
      </h1>
    </FadeIn>
    <FadeIn delay={400}>
      <p className="text-base text-gray-400 max-w-lg mb-6 leading-relaxed">
        Built by a crew that only works with people and organizations that actually have a purpose. 
        You own the code. You own the data. You own the future.
      </p>
    </FadeIn>
    <FadeIn delay={600}>
      <p className="text-sm text-gray-600">
        Delivered for <span className="text-white font-medium">{clientName}</span>
      </p>
    </FadeIn>
  </div>
);

const ProblemSlide = () => (
  <div className="h-full px-6 py-8 overflow-auto">
    <FadeIn>
      <span className="text-red-400 text-xs font-semibold uppercase tracking-wider">The Problem</span>
      <h2 className="font-corleone text-3xl text-white mt-2 mb-6">
        Why Pauli had to<br />get involved.
      </h2>
    </FadeIn>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl">
      {[
        { icon: Icons.Clock, title: "Websites Wait", desc: "They just sit there hoping someone cares enough to visit." },
        { icon: Icons.Users, title: "Visitors Vanish", desc: "97% leave with no follow-up, no nurturing, no path forward." },
        { icon: Icons.Code, title: "Code Hostage", desc: "You rent tools that lock your data and creativity in forever." },
        { icon: Icons.Brain, title: "AI Gap", desc: "The bridge to AI feels impossible without giving up control." },
      ].map((item, i) => (
        <FadeIn key={i} delay={200 + i * 100}>
          <div className="glass-card rounded-xl p-4 border-red-500/10">
            <div className="text-red-400 mb-2"><item.icon /></div>
            <h3 className="text-white font-semibold text-sm mb-1">{item.title}</h3>
            <p className="text-gray-500 text-xs">{item.desc}</p>
          </div>
        </FadeIn>
      ))}
    </div>
  </div>
);

const SolutionSlide = () => (
  <div className="h-full px-6 py-8 overflow-auto">
    <FadeIn>
      <span className="text-emerald-400 text-xs font-semibold uppercase tracking-wider">The Solution</span>
      <h2 className="font-corleone text-3xl text-white mt-2 mb-6">
        What Pauli built<br />for you.
      </h2>
    </FadeIn>
    <div className="space-y-4 max-w-xl">
      {[
        { icon: Icons.Brain, title: "AI-Powered Agents", desc: "24/7 lead qualification, support, and nurturing.", gradient: "from-purple-500 to-pink-500" },
        { icon: Icons.Rocket, title: "Proactive Outreach", desc: "Your site hunts instead of waiting for visitors.", gradient: "from-cyan-500 to-blue-500" },
        { icon: Icons.Shield, title: "Full Ownership", desc: "Every line of code is yours. No lock-in. Ever.", gradient: "from-emerald-500 to-teal-500" },
      ].map((item, i) => (
        <FadeIn key={i} delay={200 + i * 150}>
          <div className="flex items-start gap-4 glass-card rounded-xl p-4">
            <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${item.gradient} flex items-center justify-center text-white flex-shrink-0`}>
              <item.icon />
            </div>
            <div>
              <h3 className="text-white font-semibold text-sm mb-1">{item.title}</h3>
              <p className="text-gray-400 text-xs">{item.desc}</p>
            </div>
          </div>
        </FadeIn>
      ))}
    </div>
  </div>
);

const ProcessSlide = () => (
  <div className="h-full px-6 py-8 overflow-auto">
    <FadeIn>
      <span className="text-cyan-400 text-xs font-semibold uppercase tracking-wider">The Process</span>
      <h2 className="font-corleone text-3xl text-white mt-2 mb-6">
        Your 30-day<br />live run.
      </h2>
    </FadeIn>
    <div className="grid grid-cols-2 gap-4 max-w-lg">
      {[
        { num: "01", title: "We Build", desc: "AI-powered site + agent dashboard", color: "emerald" },
        { num: "02", title: "You Test", desc: "30 days on our hosting, free", color: "cyan" },
        { num: "03", title: "You Choose", desc: "Partner, Self-Host, or Static", color: "purple" },
        { num: "04", title: "We Deliver", desc: "Full codebase transferred to you", color: "yellow" },
      ].map((step, i) => {
        const colors = {
          emerald: "text-emerald-400 border-emerald-500/30",
          cyan: "text-cyan-400 border-cyan-500/30",
          purple: "text-purple-400 border-purple-500/30",
          yellow: "text-yellow-400 border-yellow-500/30",
        };
        return (
          <FadeIn key={i} delay={200 + i * 100}>
            <div className={`glass-card rounded-xl p-4 border ${colors[step.color]}`}>
              <span className={`text-xs font-mono ${colors[step.color].split(' ')[0]}`}>{step.num}</span>
              <h3 className="text-white font-semibold text-sm mt-2 mb-1">{step.title}</h3>
              <p className="text-gray-500 text-xs">{step.desc}</p>
            </div>
          </FadeIn>
        );
      })}
    </div>
  </div>
);

const PricingSlide = () => (
  <div className="h-full px-6 py-6 overflow-auto">
    <FadeIn>
      <span className="text-yellow-400 text-xs font-semibold uppercase tracking-wider">Investment</span>
      <h2 className="font-corleone text-2xl text-white mt-2 mb-4">The offer.</h2>
    </FadeIn>
    <div className="grid grid-cols-2 gap-4 max-w-xl">
      <FadeIn delay={200}>
        <div className="glass-card rounded-xl p-4">
          <h3 className="text-white font-bold text-xs mb-3">Value Stack:</h3>
          <div className="space-y-2 text-xs">
            {[
              ["Smart Site", "$8K"],
              ["AI Agents", "$5K"],
              ["Dashboard", "$3K"],
              ["Source Code", "$5K"],
              ["Setup", "$3K"]
            ].map(([item, val], i) => (
              <div key={i} className="flex justify-between">
                <span className="text-gray-300 flex items-center gap-1">
                  <span className="text-emerald-400">✓</span>{item}
                </span>
                <span className="text-gray-600 line-through">{val}</span>
              </div>
            ))}
          </div>
          <div className="mt-3 pt-3 border-t border-white/10 flex justify-between text-sm">
            <span className="text-gray-400">Value:</span>
            <span className="text-gray-500 line-through">$24K</span>
          </div>
        </div>
      </FadeIn>
      <FadeIn delay={400}>
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 rounded-xl blur-xl" />
          <div className="relative glass-card rounded-xl p-4 border border-emerald-500/30">
            <div className="text-center mb-3">
              <div className="inline-flex items-center gap-1 px-2 py-0.5 bg-emerald-500/20 rounded-full text-emerald-400 text-xs">
                <Icons.Star /> Partner Rate
              </div>
              <div className="text-3xl font-bold text-white mt-2">$4,997</div>
              <p className="text-emerald-400 text-xs">One-time build</p>
            </div>
            <div className="space-y-2 text-xs">
              <div className="flex items-center gap-2 text-gray-300">
                <Icons.Gift /> <span>30 days free hosting</span>
              </div>
              <div className="flex items-center gap-2 text-gray-300">
                <Icons.Server /> <span>$997/yr optional hosting</span>
              </div>
              <div className="flex items-center gap-2 text-gray-300">
                <Icons.Refresh /> <span>$2,497/yr retainer</span>
              </div>
            </div>
          </div>
        </div>
      </FadeIn>
    </div>
  </div>
);

const OwnershipSlide = () => (
  <div className="h-full px-6 py-8 overflow-auto">
    <FadeIn>
      <span className="text-emerald-400 text-xs font-semibold uppercase tracking-wider">Your Rights</span>
      <h2 className="font-corleone text-3xl text-white mt-2 mb-6">
        You own<br />everything.
      </h2>
    </FadeIn>
    <div className="space-y-3 max-w-md">
      {[
        { icon: Icons.Code, title: "Full Source Code", desc: "Every line is yours. Forever. No exceptions." },
        { icon: Icons.Shield, title: "Zero Lock-In", desc: "Take it anywhere. Any developer can work on it." },
        { icon: Icons.Server, title: "Host Anywhere", desc: "Our servers, yours, Vercel, AWS—your choice." },
        { icon: Icons.Heart, title: "Backup with Permission", desc: "We keep a secure copy. Just in case." },
      ].map((item, i) => (
        <FadeIn key={i} delay={200 + i * 100}>
          <div className="flex items-start gap-4 glass-card rounded-xl p-4">
            <div className="w-9 h-9 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-400 flex-shrink-0">
              <item.icon />
            </div>
            <div>
              <h3 className="text-white font-semibold text-sm mb-0.5">{item.title}</h3>
              <p className="text-gray-500 text-xs">{item.desc}</p>
            </div>
          </div>
        </FadeIn>
      ))}
    </div>
  </div>
);

const ScratchRevealSlide = ({ clientName, siteUrl, onShare }) => {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const isDrawingRef = useRef(false);
  const [hasScratched, setHasScratched] = useState(false);
  const [scratchPercent, setScratchPercent] = useState(0);

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
    
    // Dark overlay
    ctx.fillStyle = "#0a0a0f";
    ctx.fillRect(0, 0, rect.width, rect.height);
    
    // Gradient overlay
    const gradient = ctx.createLinearGradient(0, 0, rect.width, rect.height);
    gradient.addColorStop(0, "#22c55e");
    gradient.addColorStop(1, "#06b6d4");
    ctx.globalAlpha = 0.9;
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, rect.width, rect.height);
    ctx.globalAlpha = 1;
    
    // Scratch text
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
    for (let i = 3; i < pixels.length; i += 4) {
      if (pixels[i] < 128) transparent++;
    }
    const percent = (transparent / (pixels.length / 4)) * 100;
    setScratchPercent(percent);
    if (percent > 30 && !hasScratched) setHasScratched(true);
  };

  const scratchAt = (clientX, clientY) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    const x = (clientX - rect.left);
    const y = (clientY - rect.top);
    
    ctx.globalCompositeOperation = "destination-out";
    ctx.beginPath();
    ctx.arc(x, y, 30, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalCompositeOperation = "source-over";
    
    checkScratchPercent();
  };

  const handlePointerDown = (e) => {
    isDrawingRef.current = true;
    const point = e.touches ? e.touches[0] : e;
    scratchAt(point.clientX, point.clientY);
  };
  
  const handlePointerMove = (e) => {
    if (!isDrawingRef.current) return;
    const point = e.touches ? e.touches[0] : e;
    scratchAt(point.clientX, point.clientY);
  };
  
  const handlePointerUp = () => {
    isDrawingRef.current = false;
  };

  return (
    <div className="h-full px-6 py-6 flex flex-col items-center justify-center text-center overflow-auto">
      <FadeIn>
        <span className="text-emerald-400 text-xs font-semibold uppercase tracking-wider">The Reveal</span>
      </FadeIn>
      <FadeIn delay={200}>
        <h2 className="font-corleone text-2xl text-white mt-2 mb-4">
          Ready to see it, {clientName.split(' ')[0]}?
        </h2>
      </FadeIn>

      <FadeIn delay={350}>
        <div
          ref={containerRef}
          className="relative w-full max-w-sm aspect-video mx-auto mb-4 rounded-2xl overflow-hidden border border-white/10"
        >
          {/* Revealed content */}
          <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-gray-950 to-black flex flex-col items-center justify-center p-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-500/20 rounded-full text-xs text-emerald-300 mb-3">
              <Icons.Sparkles />
              <span>Your site is live</span>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">{CONFIG.client.businessName}</h3>
            <p className="text-xs text-gray-400 max-w-xs mb-3">
              Built to serve your community, not an algorithm.
            </p>
            <div className="flex items-center gap-1 text-emerald-400 text-xs">
              <Icons.Link />
              <span className="truncate max-w-[200px]">{siteUrl}</span>
            </div>
          </div>

          {/* Scratch canvas */}
          <canvas
            ref={canvasRef}
            className="absolute inset-0 touch-none cursor-pointer"
            onMouseDown={handlePointerDown}
            onMouseMove={handlePointerMove}
            onMouseUp={handlePointerUp}
            onMouseLeave={handlePointerUp}
            onTouchStart={handlePointerDown}
            onTouchMove={handlePointerMove}
            onTouchEnd={handlePointerUp}
          />
        </div>
      </FadeIn>

      <FadeIn delay={500}>
        <div className="flex flex-col items-center gap-3 w-full max-w-sm">
          <a
            href={hasScratched ? siteUrl : undefined}
            target="_blank"
            rel="noreferrer"
            className={`w-full flex items-center justify-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold transition-all ${
              hasScratched
                ? "bg-gradient-to-r from-emerald-500 to-cyan-500 text-black hover:opacity-90"
                : "bg-gray-800 text-gray-500 cursor-not-allowed"
            }`}
          >
            <Icons.Link />
            <span>{hasScratched ? "Visit My Live Site" : "Scratch to unlock"}</span>
          </a>
          
          {hasScratched && (
            <button
              onClick={onShare}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 glass-card rounded-xl text-sm font-semibold text-white hover:bg-white/10 transition-colors"
            >
              <Icons.Share />
              <span>Share: "I Got Sent For"</span>
            </button>
          )}
        </div>
      </FadeIn>

      <FadeIn delay={700}>
        <div className="mt-4 flex flex-col items-center gap-2 text-xs text-gray-500">
          <p>Support more purpose-driven projects:</p>
          <div className="flex gap-4">
            <a href={CONFIG.company.url} target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:text-emerald-400 transition-colors">
              <Icons.Link /> {CONFIG.company.name}
            </a>
            <a href={CONFIG.company.donationUrl} target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:text-emerald-400 transition-colors">
              <Icons.Heart /> Buy us a coffee
            </a>
          </div>
        </div>
      </FadeIn>
    </div>
  );
};

// ============================================================================
// MAIN APP
// ============================================================================
export default function PauliEffectDelivery() {
  const [mode, setMode] = useState("intro"); // intro | runHide | deck
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

  const goToSlide = (index, dir) => {
    if (index < 0 || index >= slides.length) return;
    setFlipDirection(dir);
    setCurrentSlide(index);
    setTimeout(() => setFlipDirection(null), 650);
  };

  const nextSlide = () => {
    if (currentSlide < slides.length - 1) goToSlide(currentSlide + 1, "next");
  };

  const prevSlide = () => {
    if (currentSlide > 0) goToSlide(currentSlide - 1, "prev");
  };

  useEffect(() => {
    if (mode !== "deck") return;
    const handleKeyDown = (e) => {
      if (e.key === "ArrowRight" || e.key === " ") { e.preventDefault(); nextSlide(); }
      else if (e.key === "ArrowLeft") { e.preventDefault(); prevSlide(); }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [mode, currentSlide]);

  // Inject styles
  useEffect(() => {
    const styleEl = document.createElement("style");
    styleEl.textContent = styles;
    document.head.appendChild(styleEl);
    return () => document.head.removeChild(styleEl);
  }, []);

  if (mode === "intro") {
    return <IntroScreen onGoSeePauli={() => setMode("deck")} onRunHide={() => setMode("runHide")} />;
  }

  if (mode === "runHide") {
    return <RunHideScreen onCaught={() => setMode("deck")} />;
  }

  const CurrentSlide = slides[currentSlide].component;

  return (
    <div className="min-h-screen bg-gray-950 text-white font-body">
      {/* Background */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/4 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl" />
      </div>

      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-40 p-4 flex justify-between items-center bg-black/60 backdrop-blur-xl border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center text-lg shadow-lg shadow-emerald-500/30">
            🧔
          </div>
          <div className="hidden sm:block">
            <p className="font-corleone text-sm text-white">{CONFIG.company.name}</p>
            <p className="text-[10px] text-gray-500">{CONFIG.company.tagline}</p>
          </div>
        </div>

        <div className="flex gap-1.5">
          {slides.map((_, i) => (
            <div
              key={i}
              className={`h-1.5 rounded-full transition-all duration-300 ${
                i <= currentSlide ? "w-5 bg-gradient-to-r from-emerald-500 to-cyan-500" : "w-2 bg-gray-700"
              }`}
            />
          ))}
        </div>

        <div className="text-xs text-gray-500 font-mono">
          {String(currentSlide + 1).padStart(2, "0")} / {String(slides.length).padStart(2, "0")}
        </div>
      </header>

      {/* Main Content */}
      <main className="pt-20 pb-24 min-h-screen pauli-perspective">
        <div className="h-[calc(100vh-176px)] flex items-center justify-center px-4">
          <div
            key={currentSlide}
            className={`pauli-book-page w-full max-w-2xl h-full glass-card rounded-3xl shadow-2xl shadow-black/50 overflow-hidden ${
              flipDirection === "next" ? "pauli-page-flip-next" : flipDirection === "prev" ? "pauli-page-flip-prev" : ""
            }`}
          >
            <CurrentSlide
              clientName={CONFIG.client.name}
              siteUrl={CONFIG.client.siteUrl}
              onShare={() => setShowShareModal(true)}
            />
          </div>
        </div>
      </main>

      {/* Footer Nav */}
      <footer className="fixed bottom-0 left-0 right-0 p-4 flex justify-between items-center bg-black/60 backdrop-blur-xl border-t border-white/5">
        <button
          onClick={prevSlide}
          disabled={currentSlide === 0}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all ${
            currentSlide === 0 ? "bg-gray-800/50 text-gray-600" : "bg-gray-800 text-white hover:bg-gray-700"
          }`}
        >
          <Icons.ChevronLeft />
          <span className="hidden sm:inline">Previous</span>
        </button>

        <div className="flex gap-1.5">
          {slides.map((_, i) => (
            <button
              key={i}
              onClick={() => goToSlide(i, i > currentSlide ? "next" : "prev")}
              className={`w-2 h-2 rounded-full transition-all ${
                i === currentSlide ? "w-5 bg-emerald-500" : "bg-gray-700 hover:bg-gray-600"
              }`}
            />
          ))}
        </div>

        <button
          onClick={nextSlide}
          disabled={currentSlide === slides.length - 1}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all ${
            currentSlide === slides.length - 1
              ? "bg-gray-800/50 text-gray-600"
              : "bg-gradient-to-r from-emerald-500 to-cyan-500 text-black hover:opacity-90"
          }`}
        >
          <span className="hidden sm:inline">{currentSlide === slides.length - 2 ? "Reveal" : "Next"}</span>
          <Icons.ChevronRight />
        </button>
      </footer>

      {/* Share Modal */}
      {showShareModal && (
        <SocialShareCard
          clientName={CONFIG.client.name}
          siteUrl={CONFIG.client.siteUrl}
          onClose={() => setShowShareModal(false)}
        />
      )}
    </div>
  );
}
