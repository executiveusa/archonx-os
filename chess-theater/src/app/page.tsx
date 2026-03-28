'use client'

import dynamic from 'next/dynamic'

// Three.js canvas must not SSR
const ChessTheater = dynamic(() => import('@/components/ChessTheater'), { ssr: false })

export default function HomePage() {
  return (
    <main className="w-full h-screen bg-black">
      <ChessTheater />
    </main>
  )
}
