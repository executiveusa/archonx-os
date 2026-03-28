/**
 * SYNTHIA 3.0 — Landing page (Spanish-first)
 * Uncodixfy-compliant: Linear aesthetic, no gradients, no glass.
 */
import Link from 'next/link'

const TIERS = [
  {
    name: 'Gratis',
    price: '$0 MXN',
    period: '',
    features: ['5 diseños por mes', 'Exportar JSON', 'Paletas básicas'],
    cta: 'Comenzar gratis',
    href: '/dashboard',
    highlighted: false,
  },
  {
    name: 'Pro',
    price: '$299 MXN',
    period: '/mes',
    features: ['50 diseños por mes', 'Exportar HTML + JSON', 'Revisión UDEC automática', 'Historial completo'],
    cta: 'Prueba 14 días',
    href: '/dashboard?plan=pro',
    highlighted: true,
  },
  {
    name: 'Premium',
    price: '$799 MXN',
    period: '/mes',
    features: ['Diseños ilimitados', 'API access', 'Soporte prioritario', 'Kit de marca completo'],
    cta: 'Hablar con ventas',
    href: '/dashboard?plan=premium',
    highlighted: false,
  },
]

export default function HomePage() {
  return (
    <div style={{ fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif", background: '#fff', color: '#13111a' }}>
      {/* Nav */}
      <nav style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '16px 32px', borderBottom: '1px solid #e4e1f0', background: '#fff',
        position: 'sticky', top: 0, zIndex: 40,
      }}>
        <span style={{ fontWeight: 700, fontSize: 16, color: '#7c3aed' }}>SYNTHIA™ 3.0</span>
        <div style={{ display: 'flex', gap: 24, fontSize: 14, color: '#5a5570' }}>
          <a href="#precios" style={{ color: 'inherit', textDecoration: 'none' }}>Precios</a>
          <a href="#funciones" style={{ color: 'inherit', textDecoration: 'none' }}>Funciones</a>
        </div>
        <Link href="/dashboard" style={{
          background: '#7c3aed', color: '#fff', padding: '8px 20px',
          borderRadius: 8, fontSize: 14, fontWeight: 600, textDecoration: 'none',
        }}>
          Comenzar
        </Link>
      </nav>

      {/* Hero */}
      <section style={{ padding: '80px 32px 64px', maxWidth: 760, margin: '0 auto', textAlign: 'center' }}>
        <div style={{
          display: 'inline-block', background: '#f5f3ff', color: '#7c3aed',
          fontSize: 12, fontWeight: 600, letterSpacing: '0.04em',
          padding: '4px 12px', borderRadius: 4, marginBottom: 20,
          border: '1px solid #ddd6fe',
        }}>
          NUEVA VERSIÓN — SYNTHIA 3.0
        </div>
        <h1 style={{ fontSize: 44, fontWeight: 700, lineHeight: 1.15, margin: '0 0 20px', color: '#13111a' }}>
          Diseño inteligente para<br />emprendedoras latinas
        </h1>
        <p style={{ fontSize: 17, color: '#5a5570', lineHeight: 1.65, margin: '0 auto 36px', maxWidth: 520 }}>
          Describe tu proyecto. SYNTHIA diseña tu marca, paleta y estructura visual en segundos.
          Sin conocimientos técnicos.
        </p>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link href="/dashboard" style={{
            background: '#7c3aed', color: '#fff', padding: '12px 28px',
            borderRadius: 8, fontSize: 15, fontWeight: 600, textDecoration: 'none',
          }}>
            Diseñar ahora
          </Link>
          <a href="#funciones" style={{
            background: '#fff', color: '#7c3aed', padding: '12px 28px',
            borderRadius: 8, fontSize: 15, fontWeight: 500, textDecoration: 'none',
            border: '1px solid #7c3aed',
          }}>
            Ver cómo funciona
          </a>
        </div>
      </section>

      {/* Features */}
      <section id="funciones" style={{ background: '#f9f8fc', padding: '64px 32px', borderTop: '1px solid #e4e1f0' }}>
        <div style={{ maxWidth: 960, margin: '0 auto' }}>
          <h2 style={{ fontSize: 28, fontWeight: 700, textAlign: 'center', marginBottom: 48 }}>
            Todo lo que necesitas para lanzar
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 24 }}>
            {[
              { title: 'IA en español', body: 'Describe tu proyecto en español. SYNTHIA entiende el contexto LATAM.' },
              { title: 'Paleta + tipografía', body: 'Sistema de color y tipografía coherente, listo para usar en diseño o código.' },
              { title: 'Exportar HTML', body: 'Obtén una previsualización HTML de tu diseño. Compártela o úsala como referencia.' },
              { title: 'Calificación UDEC', body: 'Cada diseño incluye una puntuación UDEC 14-ejes. Mínimo 8.5/10 garantizado.' },
              { title: 'Historial completo', body: 'Todos tus diseños guardados. Regresa, edita y re-exporta cuando quieras.' },
              { title: 'Sin código', body: 'No necesitas saber de diseño ni de programación. Solo describe y SYNTHIA hace el resto.' },
            ].map((f) => (
              <div key={f.title} style={{
                background: '#fff', border: '1px solid #e4e1f0', borderRadius: 12,
                padding: 24, boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
              }}>
                <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 8 }}>{f.title}</h3>
                <p style={{ fontSize: 14, color: '#5a5570', lineHeight: 1.6, margin: 0 }}>{f.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="precios" style={{ padding: '64px 32px' }}>
        <div style={{ maxWidth: 960, margin: '0 auto' }}>
          <h2 style={{ fontSize: 28, fontWeight: 700, textAlign: 'center', marginBottom: 8 }}>Precios en pesos mexicanos</h2>
          <p style={{ fontSize: 15, color: '#5a5570', textAlign: 'center', marginBottom: 48 }}>Sin contratos. Cancela cuando quieras.</p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 24 }}>
            {TIERS.map((t) => (
              <div key={t.name} style={{
                background: t.highlighted ? '#7c3aed' : '#fff',
                color: t.highlighted ? '#fff' : '#13111a',
                border: `1px solid ${t.highlighted ? '#7c3aed' : '#e4e1f0'}`,
                borderRadius: 12, padding: 32,
                boxShadow: t.highlighted ? '0 4px 20px rgba(124,58,237,0.25)' : '0 2px 8px rgba(0,0,0,0.05)',
              }}>
                <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 12, opacity: 0.7 }}>{t.name.toUpperCase()}</div>
                <div style={{ fontSize: 36, fontWeight: 700, marginBottom: 4 }}>
                  {t.price}<span style={{ fontSize: 15, fontWeight: 400, opacity: 0.7 }}>{t.period}</span>
                </div>
                <ul style={{ listStyle: 'none', padding: 0, margin: '24px 0', display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {t.features.map((f) => (
                    <li key={f} style={{ fontSize: 14, display: 'flex', alignItems: 'center', gap: 8, opacity: 0.9 }}>
                      <span style={{ fontSize: 16 }}>✓</span> {f}
                    </li>
                  ))}
                </ul>
                <Link href={t.href} style={{
                  display: 'block', textAlign: 'center', textDecoration: 'none',
                  background: t.highlighted ? '#fff' : '#7c3aed',
                  color: t.highlighted ? '#7c3aed' : '#fff',
                  padding: '10px 20px', borderRadius: 8, fontSize: 14, fontWeight: 600,
                }}>
                  {t.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid #e4e1f0', padding: '32px', textAlign: 'center' }}>
        <span style={{ fontSize: 13, color: '#9490a8' }}>
          © {new Date().getFullYear()} SYNTHIA™ 3.0 · Pauli Digital · Hecho en México
        </span>
      </footer>
    </div>
  )
}
