import { useState, useEffect, useRef } from "react";

// CONFIG
const CONFIG = {
  company: { name: "The Pauli Effect", tagline: "AI for people with purpose." },
  client: { name: "Veronika N. Dimitrova", businessName: "Strategic Business Partner", siteUrl: "https://veronika-site.vercel.app" },
  urgency: { deadline: "December 31, 2024", deadlineShort: "NYE 2024" }
};

// ICONS
const Icons = {
  ChevronLeft: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><path d="M15 18l-6-6 6-6"/></svg>,
  ChevronRight: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><path d="M9 18l6-6-6-6"/></svg>,
  Rocket: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-6 h-6"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/></svg>,
  Brain: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-6 h-6"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-1.54z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-1.54z"/></svg>,
  Shield: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-6 h-6"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>,
  Sparkles: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>,
  Link: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>,
  Share: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>,
  Code: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-6 h-6"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>,
  Users: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-6 h-6"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>,
  Gift: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><polyline points="20 12 20 22 4 22 4 12"/><rect x="2" y="7" width="20" height="5"/><line x1="12" y1="22" x2="12" y2="7"/></svg>,
  Clock: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-6 h-6"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>,
  Check: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><polyline points="20 6 9 17 4 12"/></svg>,
  Server: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/></svg>,
  Target: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-6 h-6"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>,
  AlertCircle: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>,
  Heart: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/></svg>,
};

// UTILITIES
const FadeIn = ({ children, delay = 0, className = "" }) => {
  const [visible, setVisible] = useState(false);
  useEffect(() => { const t = setTimeout(() => setVisible(true), delay); return () => clearTimeout(t); }, [delay]);
  return <div className={`transition-all duration-700 ${visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"} ${className}`}>{children}</div>;
};

const LiquidBlob = ({ className = "", color = "emerald", size = "w-64 h-64", delay = 0 }) => {
  const colors = { emerald: "bg-emerald-500/20", cyan: "bg-cyan-500/20", purple: "bg-purple-500/20" };
  return <div className={`absolute rounded-full blur-3xl ${colors[color]} ${size} ${className}`} style={{ animation: `blob 8s ease-in-out infinite`, animationDelay: `${delay}s` }} />;
};

// SLIDES
const TitleSlide = ({ clientName }) => (
  <div className="flex flex-col items-center justify-center h-full text-center px-6">
    <FadeIn><div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/10 rounded-full text-emerald-400 text-sm font-medium mb-6 border border-emerald-500/20"><Icons.Sparkles /><span>{CONFIG.company.name}</span></div></FadeIn>
    <FadeIn delay={200}><h1 className="text-4xl font-bold text-white mb-4">Your <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">purpose-driven site</span><br />is ready.</h1></FadeIn>
    <FadeIn delay={400}><p className="text-gray-400 max-w-lg mb-6">Built by a crew that only works with people who actually have a purpose. You own the code. You own the data. You own the future.</p></FadeIn>
    <FadeIn delay={600}><p className="text-sm text-gray-600">Delivered for <span className="text-white font-medium">{clientName}</span></p></FadeIn>
  </div>
);

const ProblemSlide = () => (
  <div className="h-full px-6 py-6 overflow-auto">
    <FadeIn><span className="text-red-400 text-xs font-semibold uppercase tracking-wider">The Problem</span><h2 className="text-2xl font-bold text-white mt-2 mb-4">Why Pauli had to get involved.</h2></FadeIn>
    
    <FadeIn delay={100}>
      <div className="mb-4 p-4 rounded-xl border-2 border-emerald-500/30 bg-gradient-to-br from-emerald-500/10 to-cyan-500/5">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-400"><Icons.Target /></div>
          <div>
            <h3 className="text-white font-bold text-base mb-1">You Have a Purpose.</h3>
            <p className="text-emerald-200/80 text-sm">In a world drowning in noise and algorithm chasing, you actually stand for something. That's rare. That's powerful. That's why we only work with people like you.</p>
          </div>
        </div>
      </div>
    </FadeIn>
    
    <div className="grid grid-cols-2 gap-3">
      {[
        { icon: Icons.Clock, title: "Websites Wait", desc: "They sit hoping someone visits." },
        { icon: Icons.Users, title: "Visitors Vanish", desc: "97% leave with no follow-up." },
        { icon: Icons.Code, title: "Code Hostage", desc: "You rent tools that lock you in." },
        { icon: Icons.Brain, title: "AI Gap", desc: "The bridge feels impossible." },
      ].map((item, i) => (
        <FadeIn key={i} delay={200 + i * 100}>
          <div className="bg-white/5 backdrop-blur rounded-xl p-3 border border-red-500/10">
            <div className="text-red-400 mb-1"><item.icon /></div>
            <h3 className="text-white font-semibold text-xs mb-0.5">{item.title}</h3>
            <p className="text-gray-500 text-[10px]">{item.desc}</p>
          </div>
        </FadeIn>
      ))}
    </div>
  </div>
);

const SolutionSlide = () => (
  <div className="h-full px-6 py-6 overflow-auto">
    <FadeIn><span className="text-emerald-400 text-xs font-semibold uppercase tracking-wider">The Solution</span><h2 className="text-2xl font-bold text-white mt-2 mb-5">What Team Pauli <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">built for you.</span></h2></FadeIn>
    <div className="space-y-3">
      {[
        { icon: Icons.Brain, title: "AI-Powered Agents", desc: "24/7 lead qualification, support, and nurturing.", gradient: "from-purple-500 to-pink-500" },
        { icon: Icons.Rocket, title: "Proactive Outreach", desc: "Your site hunts instead of waiting.", gradient: "from-cyan-500 to-blue-500" },
        { icon: Icons.Shield, title: "Full Code Ownership", desc: "Every line is yours. No lock-in. Ever.", gradient: "from-emerald-500 to-teal-500" },
      ].map((item, i) => (
        <FadeIn key={i} delay={200 + i * 150}>
          <div className="flex items-start gap-4 bg-white/5 backdrop-blur rounded-xl p-4 border border-white/10">
            <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${item.gradient} flex items-center justify-center text-white`}><item.icon /></div>
            <div><h3 className="text-white font-semibold text-sm mb-1">{item.title}</h3><p className="text-gray-400 text-xs">{item.desc}</p></div>
          </div>
        </FadeIn>
      ))}
    </div>
  </div>
);

const ProcessSlide = () => (
  <div className="h-full px-6 py-6 overflow-auto">
    <FadeIn><span className="text-cyan-400 text-xs font-semibold uppercase tracking-wider">The Process</span><h2 className="text-2xl font-bold text-white mt-2 mb-5">Your 30-day live run.</h2></FadeIn>
    <div className="grid grid-cols-2 gap-3">
      {[
        { num: "01", title: "We Build", desc: "AI-powered site + dashboard", color: "emerald" },
        { num: "02", title: "You Test", desc: "30 days free hosting", color: "cyan" },
        { num: "03", title: "You Choose", desc: "Partner, Self-Host, or Static", color: "purple" },
        { num: "04", title: "We Deliver", desc: "Full codebase transferred", color: "yellow" },
      ].map((step, i) => {
        const colors = { emerald: "text-emerald-400 border-emerald-500/30", cyan: "text-cyan-400 border-cyan-500/30", purple: "text-purple-400 border-purple-500/30", yellow: "text-yellow-400 border-yellow-500/30" };
        return (
          <FadeIn key={i} delay={200 + i * 100}>
            <div className={`bg-white/5 backdrop-blur rounded-xl p-3 border ${colors[step.color]}`}>
              <span className={`text-xs font-mono ${colors[step.color].split(' ')[0]}`}>{step.num}</span>
              <h3 className="text-white font-semibold text-sm mt-1">{step.title}</h3>
              <p className="text-gray-500 text-[10px]">{step.desc}</p>
            </div>
          </FadeIn>
        );
      })}
    </div>
  </div>
);

// PRICING SLIDE - HORMOZI 3-TIER VALUE STACK
const PricingSlide = () => {
  const [selectedTier, setSelectedTier] = useState(1);
  
  const tiers = [
    { id: 0, name: "Starter", subtitle: "DIY Path", price: "$1,997", totalValue: "$7,000",
      valueStack: [{ item: "Smart Site Template", value: "$3,000" }, { item: "Setup Guide", value: "$500" }, { item: "1 AI Agent", value: "$1,000" }, { item: "Community", value: "$500" }, { item: "Source Code", value: "$2,000" }],
      color: "gray", badge: null },
    { id: 1, name: "Partner", subtitle: "Done With You", price: "$4,997", totalValue: "$25,000",
      valueStack: [{ item: "Custom Smart Site", value: "$8,000" }, { item: "3 AI Agents", value: "$5,000" }, { item: "Agent Dashboard", value: "$3,000" }, { item: "Full Source Code", value: "$5,000" }, { item: "30-Day Live Run", value: "$2,000" }, { item: "Setup + Onboarding", value: "$1,500" }, { item: "Strategy Session", value: "$500" }],
      extras: ["$997/yr hosting", "$2,497/yr retainer"], color: "emerald", badge: "MOST POPULAR", recommended: true },
    { id: 2, name: "Enterprise", subtitle: "Done For You", price: "$12,997", totalValue: "$58,000",
      valueStack: [{ item: "Everything in Partner", value: "$25,000" }, { item: "Unlimited Agents", value: "$15,000" }, { item: "Custom Integrations", value: "$8,000" }, { item: "Dedicated Support", value: "$5,000" }, { item: "Quarterly Strategy", value: "$4,000" }, { item: "First Year Hosting", value: "$997" }],
      color: "purple", badge: "BEST VALUE" },
  ];

  return (
    <div className="h-full px-4 py-4 overflow-auto">
      <FadeIn>
        <div className="text-center mb-3">
          <span className="text-yellow-400 text-xs font-semibold uppercase tracking-wider">The Investment</span>
          <h2 className="text-2xl font-bold text-white mt-1">Here's an Offer You Can Refuse.</h2>
          <p className="text-gray-500 text-xs mt-1 italic">(but you probably shouldn't)</p>
        </div>
      </FadeIn>

      <FadeIn delay={100}>
        <div className="bg-gradient-to-r from-red-500 to-orange-500 rounded-lg px-3 py-2 mb-3 flex items-center justify-center gap-2" style={{ animation: "pulse 2s ease-in-out infinite" }}>
          <Icons.AlertCircle />
          <span className="text-white text-xs font-bold">⏰ Expires {CONFIG.urgency.deadlineShort} • Prices increase Jan 1st</span>
        </div>
      </FadeIn>

      <div className="grid grid-cols-3 gap-2 mb-3">
        {tiers.map((tier, i) => {
          const isRecommended = tier.recommended;
          const colorMap = { gray: "border-gray-700 bg-gray-900/50", emerald: "border-emerald-500/50 bg-emerald-500/5", purple: "border-purple-500/30 bg-purple-500/5" };
          return (
            <FadeIn key={tier.id} delay={200 + i * 100}>
              <div 
                className={`relative rounded-xl p-2.5 cursor-pointer transition-all border ${colorMap[tier.color]} ${isRecommended ? "scale-105 z-10 ring-2 ring-emerald-500" : ""} ${selectedTier === tier.id ? "ring-2 ring-cyan-400" : ""}`}
                onClick={() => setSelectedTier(tier.id)}
              >
                {tier.badge && <div className={`absolute -top-2 left-1/2 -translate-x-1/2 px-2 py-0.5 rounded-full text-[7px] font-bold ${isRecommended ? "bg-emerald-500 text-black" : "bg-purple-500 text-white"}`}>{tier.badge}</div>}
                <div className="text-center mb-1.5 pt-1">
                  <h3 className={`font-bold text-xs ${isRecommended ? "text-emerald-400" : "text-white"}`}>{tier.name}</h3>
                  <p className="text-gray-500 text-[8px]">{tier.subtitle}</p>
                </div>
                <div className="text-center mb-1.5">
                  <div className={`text-lg font-bold ${isRecommended ? "text-white" : "text-gray-300"}`}>{tier.price}</div>
                  <div className="text-[8px] text-gray-500">one-time</div>
                </div>
                <div className="text-center py-0.5 rounded bg-black/30">
                  <span className="text-[8px] text-gray-500">Value: </span>
                  <span className="text-[9px] text-gray-400 line-through">{tier.totalValue}</span>
                </div>
                <div className="mt-1.5 space-y-0.5">
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
        <div className="bg-white/5 backdrop-blur rounded-xl p-3 border border-emerald-500/20">
          <div className="flex items-center justify-between mb-2">
            <div>
              <span className="text-emerald-400 text-xs font-semibold">{tiers[selectedTier].name} Package</span>
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
                <div key={idx} className="flex items-center gap-1 text-[8px] text-gray-500"><Icons.Gift />{extra}</div>
              ))}
            </div>
          )}
        </div>
      </FadeIn>
    </div>
  );
};

const OwnershipSlide = () => (
  <div className="h-full px-6 py-6 overflow-auto">
    <FadeIn><span className="text-emerald-400 text-xs font-semibold uppercase tracking-wider">Your Rights</span><h2 className="text-2xl font-bold text-white mt-2 mb-5">You own everything.</h2></FadeIn>
    <div className="space-y-3">
      {[
        { icon: Icons.Code, title: "Full Source Code", desc: "Every line is yours. Forever." },
        { icon: Icons.Shield, title: "Zero Lock-In", desc: "Take it anywhere. Any developer can work on it." },
        { icon: Icons.Server, title: "Host Anywhere", desc: "Our servers, yours, Vercel, AWS—your choice." },
        { icon: Icons.Heart, title: "Backup with Permission", desc: "We keep a secure copy. Just in case." },
      ].map((item, i) => (
        <FadeIn key={i} delay={200 + i * 100}>
          <div className="flex items-start gap-4 bg-white/5 backdrop-blur rounded-xl p-4 border border-white/10">
            <div className="w-9 h-9 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-400"><item.icon /></div>
            <div><h3 className="text-white font-semibold text-sm">{item.title}</h3><p className="text-gray-500 text-xs">{item.desc}</p></div>
          </div>
        </FadeIn>
      ))}
    </div>
  </div>
);

const RevealSlide = ({ siteUrl, onShare }) => {
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
    canvas.width = rect.width * 2;
    canvas.height = rect.height * 2;
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;
    ctx.scale(2, 2);
    const gradient = ctx.createLinearGradient(0, 0, rect.width, rect.height);
    gradient.addColorStop(0, "#22c55e");
    gradient.addColorStop(1, "#06b6d4");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, rect.width, rect.height);
    ctx.fillStyle = "rgba(0,0,0,0.3)";
    ctx.font = "bold 14px system-ui";
    ctx.textAlign = "center";
    ctx.fillText("✨ SCRATCH TO REVEAL ✨", rect.width / 2, rect.height / 2);
  }, []);

  const scratchAt = (clientX, clientY) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const rect = canvas.getBoundingClientRect();
    ctx.globalCompositeOperation = "destination-out";
    ctx.beginPath();
    ctx.arc(clientX - rect.left, clientY - rect.top, 25, 0, Math.PI * 2);
    ctx.fill();
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    let transparent = 0;
    for (let i = 3; i < imageData.data.length; i += 4) if (imageData.data[i] < 128) transparent++;
    if ((transparent / (imageData.data.length / 4)) * 100 > 25) setHasScratched(true);
  };

  return (
    <div className="h-full px-6 py-5 overflow-auto">
      <FadeIn><span className="text-emerald-400 text-xs font-semibold uppercase tracking-wider">Your Site</span><h2 className="text-xl font-bold text-white mt-1 mb-3">Scratch to reveal.</h2></FadeIn>
      <FadeIn delay={200}>
        <div ref={containerRef} className="relative w-full max-w-sm mx-auto aspect-video rounded-2xl overflow-hidden shadow-2xl">
          <div className="absolute inset-0 bg-gradient-to-br from-gray-900 to-black flex flex-col items-center justify-center p-4">
            <div className="inline-flex items-center gap-1 px-2 py-1 bg-emerald-500/20 rounded-full text-emerald-400 text-[10px] font-medium mb-3"><Icons.Sparkles className="w-3 h-3" />Live</div>
            <h3 className="text-white font-semibold text-sm text-center mb-1">{CONFIG.client.businessName}</h3>
            <p className="text-gray-500 text-xs mb-3">Built to serve your community.</p>
            <div className="flex items-center gap-1 text-emerald-400 text-xs"><Icons.Link className="w-3 h-3" /><span className="truncate max-w-[150px]">{siteUrl}</span></div>
          </div>
          <canvas ref={canvasRef} className="absolute inset-0 cursor-crosshair touch-none" onPointerDown={(e) => { isDrawingRef.current = true; scratchAt(e.clientX, e.clientY); }} onPointerMove={(e) => isDrawingRef.current && scratchAt(e.clientX, e.clientY)} onPointerUp={() => isDrawingRef.current = false} onPointerLeave={() => isDrawingRef.current = false} />
        </div>
      </FadeIn>
      {hasScratched && (
        <FadeIn>
          <div className="flex flex-col gap-2 mt-3 max-w-sm mx-auto">
            <a href={siteUrl} target="_blank" rel="noreferrer" className="w-full py-2.5 px-4 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-xl text-black font-semibold text-sm text-center">Visit My Live Site</a>
            <button onClick={onShare} className="w-full py-2.5 px-4 bg-white/5 backdrop-blur rounded-xl text-white font-medium text-sm flex items-center justify-center gap-2 border border-white/10"><Icons.Share />Share: I Got Sent For</button>
          </div>
        </FadeIn>
      )}
      <FadeIn delay={400}>
        <div className="mt-4 text-center max-w-sm mx-auto">
          <div className="bg-white/5 backdrop-blur rounded-xl p-4 border border-emerald-500/20">
            <p className="text-gray-500 text-xs mb-1">But wait... how do I find Pauli?</p>
            <p className="text-white font-semibold text-sm mb-1">You don't.</p>
            <p className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent font-bold text-lg">Pauli finds you.</p>
            <div className="mt-3 pt-3 border-t border-white/5">
              <p className="text-gray-400 text-xs">We'll be in touch. <span className="text-emerald-400">Enjoy your site.</span> 🧔</p>
            </div>
          </div>
        </div>
      </FadeIn>
    </div>
  );
};

// MAIN
export default function PauliDelivery() {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [showShare, setShowShare] = useState(false);
  const slides = [TitleSlide, ProblemSlide, SolutionSlide, ProcessSlide, PricingSlide, OwnershipSlide, RevealSlide];
  const CurrentSlide = slides[currentSlide];

  return (
    <div className="min-h-screen bg-gray-950 text-white font-sans">
      <style>{`
        @keyframes blob { 0%, 100% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; } 50% { border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%; } }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.8; } }
      `}</style>
      
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <LiquidBlob color="emerald" className="top-0 left-1/4 w-64 h-64" />
        <LiquidBlob color="cyan" className="bottom-0 right-1/4 w-64 h-64" delay={2} />
        <LiquidBlob color="purple" className="top-1/2 right-0 w-48 h-48" delay={4} />
      </div>

      <header className="fixed top-0 left-0 right-0 z-40 p-4 flex justify-between items-center bg-black/60 backdrop-blur-xl border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center text-lg shadow-lg">🧔</div>
          <div className="hidden sm:block"><p className="text-sm font-semibold text-white">{CONFIG.company.name}</p><p className="text-[10px] text-gray-500">{CONFIG.company.tagline}</p></div>
        </div>
        <div className="flex gap-1.5">{slides.map((_, i) => <div key={i} className={`h-1.5 rounded-full transition-all ${i <= currentSlide ? "w-5 bg-gradient-to-r from-emerald-500 to-cyan-500" : "w-2 bg-gray-700"}`} />)}</div>
        <div className="text-xs text-gray-500 font-mono">{String(currentSlide + 1).padStart(2, "0")} / {String(slides.length).padStart(2, "0")}</div>
      </header>

      <main className="pt-20 pb-24 min-h-screen">
        <div className="h-[calc(100vh-176px)] flex items-center justify-center px-4">
          <div className="w-full max-w-2xl h-full bg-white/5 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/10 overflow-hidden">
            <CurrentSlide clientName={CONFIG.client.name} siteUrl={CONFIG.client.siteUrl} onShare={() => setShowShare(true)} />
          </div>
        </div>
      </main>

      <footer className="fixed bottom-0 left-0 right-0 p-4 flex justify-between items-center bg-black/60 backdrop-blur-xl border-t border-white/5">
        <button onClick={() => currentSlide > 0 && setCurrentSlide(currentSlide - 1)} disabled={currentSlide === 0} className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium ${currentSlide === 0 ? "bg-gray-800/50 text-gray-600" : "bg-gray-800 text-white hover:bg-gray-700"}`}><Icons.ChevronLeft /><span className="hidden sm:inline">Previous</span></button>
        <div className="flex gap-1.5">{slides.map((_, i) => <button key={i} onClick={() => setCurrentSlide(i)} className={`w-2 h-2 rounded-full ${i === currentSlide ? "w-5 bg-emerald-500" : "bg-gray-700 hover:bg-gray-600"}`} />)}</div>
        <button onClick={() => currentSlide < slides.length - 1 && setCurrentSlide(currentSlide + 1)} disabled={currentSlide === slides.length - 1} className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium ${currentSlide === slides.length - 1 ? "bg-gray-800/50 text-gray-600" : "bg-gradient-to-r from-emerald-500 to-cyan-500 text-black hover:opacity-90"}`}><span className="hidden sm:inline">{currentSlide === slides.length - 2 ? "Reveal" : "Next"}</span><Icons.ChevronRight /></button>
      </footer>

      {showShare && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="max-w-md w-full bg-white/5 backdrop-blur-xl rounded-3xl p-6 border border-emerald-500/20">
            <div className="flex justify-between items-start mb-4">
              <div><p className="text-xs text-emerald-400 uppercase font-semibold">Share Your Win</p><h3 className="text-2xl font-bold text-white mt-1">I Got Sent For.</h3></div>
              <button onClick={() => setShowShare(false)} className="text-gray-500 hover:text-white text-2xl">&times;</button>
            </div>
            <div className="bg-black/30 rounded-xl p-4 mb-4">
              <p className="text-gray-300 text-sm">My new AI-powered site just dropped. Built by a purpose-driven crew that actually lets you own your code. 🚀</p>
            </div>
            <div className="space-y-2">
              <a href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(`I got sent for by @ThePauliEffect 🧔\n\nMy new AI-powered site just dropped.\n\n${CONFIG.client.siteUrl}\n\n#ThePauliEffect`)}`} target="_blank" rel="noreferrer" className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-black rounded-xl text-white font-medium text-sm border border-white/10">Share on X</a>
              <button onClick={() => { navigator.clipboard.writeText(`I got sent for by @ThePauliEffect! ${CONFIG.client.siteUrl}`); }} className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-white/10 rounded-xl text-white font-medium text-sm"><Icons.Check />Copy to Clipboard</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
