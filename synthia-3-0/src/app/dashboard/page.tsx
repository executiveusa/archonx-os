'use client'

/**
 * SYNTHIA 3.0 — Design Canvas (DesignWorkspace)
 * 
 * Workflow:
 *   1. User types project name + Spanish prompt
 *   2. POST /api/design → returns DesignSpec JSON + HTML preview
 *   3. User sees the HTML preview in an iframe + JSON inspector
 *   4. User can re-generate or export HTML
 *
 * Uncodixfy: Linear aesthetic, no gradients, no glass, 12px max radius on cards.
 */

import { useState, useRef } from 'react'
import type { DesignSpec } from '@/lib/design-engine'

interface DesignResult {
  spec: DesignSpec
  html: string
}

type Tab = 'preview' | 'json' | 'reasoning'

export default function DashboardPage() {
  const [projectName, setProjectName] = useState('')
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<DesignResult | null>(null)
  const [tab, setTab] = useState<Tab>('preview')
  const iframeRef = useRef<HTMLIFrameElement>(null)

  async function handleGenerate(e: React.FormEvent) {
    e.preventDefault()
    if (!prompt.trim()) return
    setLoading(true)
    setError(null)

    try {
      const res = await fetch('/api/design', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ prompt, projectName: projectName || 'Mi Proyecto' }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error ?? 'Error del servidor')
      setResult(data)
      setTab('preview')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  function handleExport() {
    if (!result) return
    const blob = new Blob([result.html], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${result.spec.projectName.replace(/\s+/g, '-').toLowerCase()}-synthia.html`
    a.click()
    URL.revokeObjectURL(url)
  }

  function handleExportJSON() {
    if (!result) return
    const blob = new Blob([JSON.stringify(result.spec, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${result.spec.projectName.replace(/\s+/g, '-').toLowerCase()}-spec.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div style={{ fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif", display: 'flex', height: '100vh', background: '#fff', color: '#13111a' }}>

      {/* Sidebar */}
      <aside style={{
        width: 260, minWidth: 260, background: '#f9f8fc',
        borderRight: '1px solid #e4e1f0', display: 'flex',
        flexDirection: 'column', padding: '20px 16px', gap: 24,
      }}>
        <div>
          <span style={{ fontWeight: 700, fontSize: 15, color: '#7c3aed' }}>SYNTHIA™ 3.0</span>
          <div style={{ fontSize: 11, color: '#9490a8', marginTop: 2 }}>Diseño con IA</div>
        </div>

        <form onSubmit={handleGenerate} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div>
            <label style={{ fontSize: 12, fontWeight: 600, color: '#5a5570', display: 'block', marginBottom: 4 }}>
              Nombre del proyecto
            </label>
            <input
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="Ej. Kupuri Studio"
              style={{
                width: '100%', padding: '8px 10px', fontSize: 13,
                border: '1px solid #e4e1f0', borderRadius: 8,
                background: '#fff', color: '#13111a', outline: 'none',
              }}
            />
          </div>

          <div>
            <label style={{ fontSize: 12, fontWeight: 600, color: '#5a5570', display: 'block', marginBottom: 4 }}>
              Describe tu proyecto
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Soy diseñadora gráfica y quiero una página para mostrar mi portafolio a clientes de México y Colombia..."
              rows={6}
              style={{
                width: '100%', padding: '8px 10px', fontSize: 13,
                border: '1px solid #e4e1f0', borderRadius: 8,
                background: '#fff', color: '#13111a', outline: 'none',
                resize: 'vertical', lineHeight: 1.5,
              }}
            />
          </div>

          <button
            type="submit"
            disabled={loading || !prompt.trim()}
            style={{
              background: loading || !prompt.trim() ? '#ede9fe' : '#7c3aed',
              color: loading || !prompt.trim() ? '#9490a8' : '#fff',
              border: 'none', padding: '10px 16px', borderRadius: 8,
              fontSize: 14, fontWeight: 600, cursor: loading ? 'wait' : 'pointer',
              width: '100%',
            }}
          >
            {loading ? 'Diseñando…' : 'Generar diseño'}
          </button>
        </form>

        {error && (
          <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, padding: '10px 12px', fontSize: 12, color: '#dc2626' }}>
            {error}
          </div>
        )}

        {result && (
          <div style={{ borderTop: '1px solid #e4e1f0', paddingTop: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: '#5a5570', marginBottom: 4 }}>Exportar</div>
            <button onClick={handleExport} style={{
              background: '#fff', border: '1px solid #e4e1f0', borderRadius: 8,
              padding: '8px 12px', fontSize: 13, fontWeight: 500, cursor: 'pointer', color: '#13111a', width: '100%',
            }}>
              Descargar HTML
            </button>
            <button onClick={handleExportJSON} style={{
              background: '#fff', border: '1px solid #e4e1f0', borderRadius: 8,
              padding: '8px 12px', fontSize: 13, fontWeight: 500, cursor: 'pointer', color: '#13111a', width: '100%',
            }}>
              Descargar JSON
            </button>
          </div>
        )}
      </aside>

      {/* Main canvas */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

        {/* Tab bar */}
        {result && (
          <div style={{ borderBottom: '1px solid #e4e1f0', padding: '0 24px', display: 'flex', gap: 0 }}>
            {(['preview', 'json', 'reasoning'] as Tab[]).map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                style={{
                  background: 'none', border: 'none', padding: '12px 16px',
                  fontSize: 13, fontWeight: tab === t ? 600 : 400,
                  color: tab === t ? '#7c3aed' : '#5a5570',
                  borderBottom: tab === t ? '2px solid #7c3aed' : '2px solid transparent',
                  cursor: 'pointer',
                  marginBottom: -1,
                }}
              >
                {t === 'preview' ? 'Previsualización' : t === 'json' ? 'JSON' : 'Razonamiento'}
              </button>
            ))}

            {/* UDEC badge */}
            <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: 12, color: '#5a5570' }}>UDEC</span>
              <span style={{
                background: result.spec.udecScore >= 8.5 ? '#dcfce7' : '#fef9c3',
                color: result.spec.udecScore >= 8.5 ? '#16a34a' : '#ca8a04',
                fontSize: 12, fontWeight: 700, padding: '2px 8px', borderRadius: 4,
                border: `1px solid ${result.spec.udecScore >= 8.5 ? '#bbf7d0' : '#fef08a'}`,
              }}>
                {result.spec.udecScore.toFixed(1)}/10
              </span>
            </div>
          </div>
        )}

        {/* Content area */}
        <div style={{ flex: 1, overflow: 'auto' }}>
          {!result && !loading && (
            <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 12, color: '#9490a8' }}>
              <div style={{ fontSize: 40 }}>✦</div>
              <div style={{ fontSize: 15, fontWeight: 500 }}>Describe tu proyecto para generar un diseño</div>
              <div style={{ fontSize: 13 }}>SYNTHIA te mostrará una previsualización lista para usar</div>
            </div>
          )}

          {loading && (
            <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 12, color: '#9490a8' }}>
              <div style={{ fontSize: 13 }}>Generando diseño…</div>
            </div>
          )}

          {result && tab === 'preview' && (
            <iframe
              ref={iframeRef}
              srcDoc={result.html}
              sandbox="allow-same-origin"
              title="Design preview"
              style={{ width: '100%', height: '100%', border: 'none' }}
            />
          )}

          {result && tab === 'json' && (
            <pre style={{
              padding: 24, margin: 0, fontSize: 12, lineHeight: 1.6,
              fontFamily: "'JetBrains Mono', monospace", color: '#13111a',
              background: '#f9f8fc', height: '100%', overflow: 'auto',
            }}>
              {JSON.stringify(result.spec, null, 2)}
            </pre>
          )}

          {result && tab === 'reasoning' && (
            <div style={{ padding: 32, maxWidth: 640 }}>
              <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Razonamiento de diseño</h2>
              <p style={{ fontSize: 14, color: '#5a5570', lineHeight: 1.7 }}>{result.spec.reasoning || 'Sin razonamiento disponible.'}</p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
