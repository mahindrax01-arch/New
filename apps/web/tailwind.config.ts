import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class'],
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './lib/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: '#0a0a0f',
        panel: '#11131a',
        accent: '#6d7cff',
        muted: '#8b90a6'
      },
      boxShadow: {
        panel: '0 20px 80px rgba(12, 13, 18, 0.35)'
      },
      borderRadius: {
        xl: '1rem',
        '2xl': '1.5rem'
      }
    }
  },
  plugins: []
}

export default config
