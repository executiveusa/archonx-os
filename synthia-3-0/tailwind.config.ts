import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#f5f3ff',
          100: '#ede9fe',
          500: '#7c3aed',
          600: '#6d28d9',
          700: '#5b21b6',
          900: '#2e1065',
        },
        surface: {
          0: '#ffffff',
          1: '#f9f8fc',
          2: '#f0eef8',
          border: '#e4e1f0',
        },
        ink: {
          primary:   '#13111a',
          secondary: '#5a5570',
          muted:     '#9490a8',
        },
        success: '#16a34a',
        warning: '#d97706',
        error:   '#dc2626',
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        card:   '12px',
        button: '8px',
        sm:     '4px',
      },
      boxShadow: {
        card: '0 2px 8px rgba(0,0,0,0.07)',
        focused: '0 0 0 3px rgba(124,58,237,0.2)',
      },
      spacing: {
        '4.5': '18px',
      },
    },
  },
  plugins: [],
}

export default config
