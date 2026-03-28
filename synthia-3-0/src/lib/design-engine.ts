/**
 * SYNTHIA 3.0 — Design Engine
 * Converts an AI-generated DesignSpec JSON into an HTML preview string.
 */

export interface ColorToken {
  primary: string
  secondary: string
  background: string
  surface: string
  text: string
  textSecondary: string
  border: string
  accent?: string
}

export interface TypographySpec {
  fontFamily: string
  heading: { size: string; weight: string; lineHeight: string }
  body:    { size: string; weight: string; lineHeight: string }
  small:   { size: string; weight: string; lineHeight: string }
}

export interface ComponentSpec {
  type: 'button' | 'card' | 'input' | 'badge' | 'hero' | 'nav' | 'footer'
  label?: string
  variant?: string
  content?: string
  items?: string[]
}

export interface DesignSpec {
  projectName: string
  description: string
  industry: string
  audience: string
  colors: ColorToken
  typography: TypographySpec
  components: ComponentSpec[]
  layout: 'landing' | 'dashboard' | 'portfolio' | 'ecommerce'
  udecScore: number
  reasoning: string
}

// ── Renderers ────────────────────────────────────────────────────────────────

function renderNav(spec: DesignSpec): string {
  return `
  <nav style="display:flex;align-items:center;justify-content:space-between;padding:16px 32px;background:${spec.colors.surface};border-bottom:1px solid ${spec.colors.border};">
    <span style="font-family:${spec.typography.fontFamily};font-size:16px;font-weight:700;color:${spec.colors.primary};">
      ${spec.projectName}
    </span>
    <div style="display:flex;gap:24px;font-family:${spec.typography.fontFamily};font-size:14px;color:${spec.colors.text};">
      <a href="#" style="color:${spec.colors.text};text-decoration:none;">Inicio</a>
      <a href="#" style="color:${spec.colors.text};text-decoration:none;">Servicios</a>
      <a href="#" style="color:${spec.colors.text};text-decoration:none;">Precios</a>
      <a href="#" style="color:${spec.colors.text};text-decoration:none;">Contacto</a>
    </div>
    <button style="background:${spec.colors.primary};color:#fff;border:none;padding:8px 20px;border-radius:8px;font-family:${spec.typography.fontFamily};font-size:14px;font-weight:600;cursor:pointer;">
      Comenzar
    </button>
  </nav>`
}

function renderHero(spec: DesignSpec): string {
  return `
  <section style="background:${spec.colors.background};padding:80px 32px 64px;text-align:center;">
    <h1 style="font-family:${spec.typography.fontFamily};font-size:${spec.typography.heading.size};font-weight:${spec.typography.heading.weight};color:${spec.colors.text};margin:0 0 16px;line-height:${spec.typography.heading.lineHeight};">
      ${spec.projectName}
    </h1>
    <p style="font-family:${spec.typography.fontFamily};font-size:${spec.typography.body.size};color:${spec.colors.textSecondary};max-width:540px;margin:0 auto 32px;line-height:${spec.typography.body.lineHeight};">
      ${spec.description}
    </p>
    <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;">
      <button style="background:${spec.colors.primary};color:#fff;border:none;padding:12px 28px;border-radius:8px;font-family:${spec.typography.fontFamily};font-size:15px;font-weight:600;cursor:pointer;">
        Comenzar gratis
      </button>
      <button style="background:transparent;color:${spec.colors.primary};border:1px solid ${spec.colors.primary};padding:12px 28px;border-radius:8px;font-family:${spec.typography.fontFamily};font-size:15px;font-weight:500;cursor:pointer;">
        Ver demo
      </button>
    </div>
  </section>`
}

function renderCard(comp: ComponentSpec, spec: DesignSpec): string {
  return `
  <div style="background:${spec.colors.surface};border:1px solid ${spec.colors.border};border-radius:12px;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
    <h3 style="font-family:${spec.typography.fontFamily};font-size:16px;font-weight:600;color:${spec.colors.text};margin:0 0 8px;">${comp.label ?? 'Función'}</h3>
    <p style="font-family:${spec.typography.fontFamily};font-size:14px;color:${spec.colors.textSecondary};margin:0;line-height:1.6;">${comp.content ?? ''}</p>
  </div>`
}

function renderCards(spec: DesignSpec): string {
  const cards = spec.components.filter((c) => c.type === 'card')
  if (cards.length === 0) return ''
  return `
  <section style="background:${spec.colors.background};padding:64px 32px;">
    <div style="max-width:960px;margin:0 auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:24px;">
      ${cards.map((c) => renderCard(c, spec)).join('\n')}
    </div>
  </section>`
}

function renderFooter(spec: DesignSpec): string {
  return `
  <footer style="background:${spec.colors.surface};border-top:1px solid ${spec.colors.border};padding:32px;text-align:center;">
    <span style="font-family:${spec.typography.fontFamily};font-size:13px;color:${spec.colors.textSecondary};">
      © ${new Date().getFullYear()} ${spec.projectName} — Diseñado con SYNTHIA™ 3.0
    </span>
  </footer>`
}

// ── Public API ────────────────────────────────────────────────────────────────

export function renderDesignToHTML(spec: DesignSpec): string {
  const bodyParts = [
    renderNav(spec),
    renderHero(spec),
    renderCards(spec),
    renderFooter(spec),
  ]

  return `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${spec.projectName}</title>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>*{box-sizing:border-box;margin:0;padding:0;}body{background:${spec.colors.background};}</style>
</head>
<body>
${bodyParts.join('\n')}
</body>
</html>`
}

export function defaultDesignSpec(projectName: string): DesignSpec {
  return {
    projectName,
    description: 'Soluciones de diseño inteligente para emprendedoras.',
    industry: 'general',
    audience: 'Emprendedoras LATAM',
    colors: {
      primary:       '#7c3aed',
      secondary:     '#6d28d9',
      background:    '#ffffff',
      surface:       '#f9f8fc',
      text:          '#13111a',
      textSecondary: '#5a5570',
      border:        '#e4e1f0',
    },
    typography: {
      fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif",
      heading: { size: '40px', weight: '700', lineHeight: '1.2' },
      body:    { size: '16px', weight: '400', lineHeight: '1.65' },
      small:   { size: '13px', weight: '400', lineHeight: '1.5' },
    },
    components: [],
    layout: 'landing',
    udecScore: 0,
    reasoning: '',
  }
}
