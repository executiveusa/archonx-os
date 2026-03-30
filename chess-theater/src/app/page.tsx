'use client'

import dynamic from 'next/dynamic'
import Link from 'next/link'
import { useEffect, useState } from 'react'

const ChessTheater = dynamic(() => import('@/components/ChessTheater'), { ssr: false })

const FEATURES = [
  { title: '64 Autonomous Agents', desc: 'White & Black crews operating 24/7 without human oversight.' },
  { title: 'BMAD Phase Gates', desc: 'Every task validated through Plan → Implement → Test → Evaluate loops.' },
  { title: 'Hermes Council', desc: 'Multi-model consensus at ≥85% convergence before acting.' },
  { title: 'Self-Deploying', desc: 'ZTE protocol: Write → Test → Fix → Commit → Deploy → Verify → Notify.' },
]

const HOW_IT_WORKS = [
  { step: '01', label: 'Define a goal', desc: 'Drop a mission brief. ARCHON-X decomposes it into a task graph.' },
  { step: '02', label: 'Agents execute', desc: '64 AI agents pick up tasks autonomously. No hand-holding required.' },
  { step: '03', label: 'Reward model scores', desc: 'Every output is evaluated on completion, quality, cost and safety.' },
  { step: '04', label: 'System improves', desc: 'Alignment scores feed back into agent selection for future tasks.' },
]

// Minimal live feed from WebSocket (degrades gracefully if API is down)
function ActivityFeed() {
  const [events, setEvents] = useState<string[]>([
    'HERMES_ALPHA → consensus reached (0.92)',
    'POPEBOT → Slack notification sent',
    'CHESSCLOCK → task graph updated',
    'BMAD → phase IMPLEMENT entered',
    'SOUL_LOADER → 38 souls active',
  ])

  useEffect(() => {
    const wsUrl = process.env.NEXT_PUBLIC_ARCHONX_WS_URL
    if (!wsUrl) return
    let ws: WebSocket
    try {
      ws = new WebSocket(wsUrl)
      ws.onmessage = (e) => {
        const data = JSON.parse(e.data)
        if (data.type === 'agent_event') {
          setEvents(prev => [`${data.agent} → ${data.message}`, ...prev.slice(0, 7)])
        }
      }
    } catch {}
    return () => ws?.close()
  }, [])

  return (
    <div className="font-mono text-xs text-green-400 bg-black border border-green-900 rounded p-4 h-36 overflow-hidden">
      {events.map((e, i) => (
        <p key={i} className="opacity-90 hover:opacity-100 truncate leading-6"
           style={{ opacity: 1 - i * 0.12 }}>
          <span className="text-green-600 mr-2">&gt;</span>{e}
        </p>
      ))}
    </div>
  )
}

export default function HomePage() {
  return (
    <div className="bg-black text-white min-h-screen font-sans">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-black/80 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <span className="text-white font-semibold tracking-wide">ARCHON-X OS</span>
          <div className="flex items-center gap-6 text-sm text-white/60">
            <a href="#how-it-works" className="hover:text-white transition-colors">How it works</a>
            <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
            <a href="https://github.com/executiveusa/archonx-os" target="_blank" rel="noreferrer"
               className="hover:text-white transition-colors">GitHub</a>
            <a href="#waitlist"
               className="px-4 py-1.5 bg-white text-black text-sm font-medium rounded hover:bg-white/90 transition-colors">
              Get access
            </a>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative pt-32 pb-24 px-6 max-w-6xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Text */}
          <div>
            <p className="text-xs font-mono text-white/40 uppercase tracking-widest mb-4">
              ARCHON-X OS · Production
            </p>
            <h1 className="text-5xl lg:text-6xl font-bold leading-tight tracking-tight mb-6">
              Your autonomous<br />
              <span className="text-white/50">agent operating</span><br />
              system.
            </h1>
            <p className="text-white/60 text-lg mb-8 leading-relaxed max-w-md">
              64 AI agents. Dual-crew architecture. Goal-aligned by design.
              Deploy missions and walk away.
            </p>
            <div className="flex flex-wrap gap-3">
              <a href="#waitlist"
                 className="px-6 py-3 bg-white text-black font-medium rounded hover:bg-white/90 transition-colors">
                Request access
              </a>
              <a href="#how-it-works"
                 className="px-6 py-3 border border-white/20 text-white rounded hover:border-white/40 transition-colors">
                See how it works
              </a>
            </div>
          </div>

          {/* Live feed + 3D preview */}
          <div className="space-y-4">
            <p className="text-xs font-mono text-white/30 uppercase tracking-wider">Live agent activity</p>
            <ActivityFeed />
            <div className="h-64 rounded overflow-hidden border border-white/10">
              <ChessTheater />
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="border-t border-white/10 py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl font-semibold mb-12 text-white/80">Built different</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {FEATURES.map(f => (
              <div key={f.title} className="border border-white/10 rounded p-6 hover:border-white/20 transition-colors">
                <h3 className="font-medium mb-2">{f.title}</h3>
                <p className="text-sm text-white/50 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="border-t border-white/10 py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl font-semibold mb-12 text-white/80">How it works</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {HOW_IT_WORKS.map(s => (
              <div key={s.step}>
                <p className="text-4xl font-bold text-white/10 mb-3">{s.step}</p>
                <h3 className="font-medium mb-2">{s.label}</h3>
                <p className="text-sm text-white/50 leading-relaxed">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="border-t border-white/10 py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl font-semibold mb-12 text-white/80">Pricing</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { name: 'Starter', price: '$49', period: '/mo', agents: '8 agents', tasks: '500 tasks/mo', highlight: false },
              { name: 'Pro', price: '$199', period: '/mo', agents: '32 agents', tasks: '5,000 tasks/mo', highlight: true },
              { name: 'Enterprise', price: 'Custom', period: '', agents: '64 agents', tasks: 'Unlimited', highlight: false },
            ].map(plan => (
              <div key={plan.name}
                   className={`rounded border p-8 flex flex-col gap-4 ${plan.highlight ? 'border-white/40 bg-white/5' : 'border-white/10'}`}>
                <div>
                  <p className="text-sm text-white/50 mb-1">{plan.name}</p>
                  <p className="text-4xl font-bold">
                    {plan.price}<span className="text-white/40 text-base font-normal">{plan.period}</span>
                  </p>
                </div>
                <ul className="space-y-2 text-sm text-white/60">
                  <li>{plan.agents}</li>
                  <li>{plan.tasks}</li>
                  <li>BMAD phase gates</li>
                  <li>Hermes Council</li>
                  {plan.highlight && <li className="text-white">Priority support</li>}
                </ul>
                <a href="#waitlist"
                   className={`mt-auto py-2.5 rounded text-sm font-medium text-center transition-colors ${plan.highlight ? 'bg-white text-black hover:bg-white/90' : 'border border-white/20 hover:border-white/40'}`}>
                  Get started
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Waitlist CTA */}
      <section id="waitlist" className="border-t border-white/10 py-24 px-6">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Join the waitlist</h2>
          <p className="text-white/50 mb-8">ARCHON-X OS is invite-only during beta. Drop your email and we&rsquo;ll reach out.</p>
          <form className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto"
                onSubmit={e => { e.preventDefault(); alert('You\'re on the list.') }}>
            <input
              type="email"
              required
              placeholder="you@company.com"
              className="flex-1 bg-white/5 border border-white/20 rounded px-4 py-3 text-sm placeholder-white/30 focus:outline-none focus:border-white/50"
            />
            <button type="submit"
                    className="px-6 py-3 bg-white text-black text-sm font-medium rounded hover:bg-white/90 transition-colors whitespace-nowrap">
              Request access
            </button>
          </form>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8 px-6">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-4 text-sm text-white/30">
          <span>© 2025 ARCHON-X OS. All rights reserved.</span>
          <div className="flex gap-6">
            <a href="https://github.com/executiveusa/archonx-os" target="_blank" rel="noreferrer"
               className="hover:text-white/60 transition-colors">GitHub</a>
            <Link href="/privacy" className="hover:text-white/60 transition-colors">Privacy</Link>
            <Link href="/terms" className="hover:text-white/60 transition-colors">Terms</Link>
          </div>
        </div>
      </footer>
    </div>
  )
}
