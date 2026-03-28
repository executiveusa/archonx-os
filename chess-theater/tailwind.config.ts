import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'board-dark': '#1a1a2e',
        'board-light': '#16213e',
        'gold': '#FFD700',
        'white-crew': '#E8E8F0',
        'black-crew': '#1A0A2E',
        'aura-cyan': '#00BFFF',
        'aura-magenta': '#FF00FF',
        'thinking-orange': '#FF8C00',
        'error-red': '#FF0000',
        'active-green': '#00ff88',
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}

export default config
