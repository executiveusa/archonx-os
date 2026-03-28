import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'SYNTHIA™ 3.0 — Diseño con IA',
  description: 'La IA de diseño para emprendedoras latinoamericanas.',
  openGraph: {
    title: 'SYNTHIA™ 3.0',
    description: 'Diseña tu marca y producto con inteligencia artificial.',
    locale: 'es_MX',
    type: 'website',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  )
}
