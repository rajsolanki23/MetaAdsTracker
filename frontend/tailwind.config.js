/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#090d16',
        surface: '#0f172a',
        'surface-hover': '#1e293b',
        card: '#111827',
        'card-border': '#1f293d',
        accent: {
          emerald: '#10b981',
          gold: '#f59e0b',
          ruby: '#ef4444',
          cyan: '#06b6d4',
          purple: '#8b5cf6',
          blue: '#3b82f6',
        },
        win: {
          DEFAULT: '#10b981',
          glow: 'rgba(16, 185, 129, 0.25)',
          bg: 'rgba(16, 185, 129, 0.12)',
          border: 'rgba(16, 185, 129, 0.3)',
        },
        loss: {
          DEFAULT: '#f43f5e',
          glow: 'rgba(244, 63, 94, 0.25)',
          bg: 'rgba(244, 63, 94, 0.12)',
          border: 'rgba(244, 63, 94, 0.3)',
        },
        testing: {
          DEFAULT: '#06b6d4',
          glow: 'rgba(6, 182, 212, 0.25)',
          bg: 'rgba(6, 182, 212, 0.12)',
          border: 'rgba(6, 182, 212, 0.3)',
        },
        paused: {
          DEFAULT: '#64748b',
          glow: 'rgba(100, 116, 139, 0.15)',
          bg: 'rgba(100, 116, 139, 0.12)',
          border: 'rgba(100, 116, 139, 0.25)',
        },
        podium: {
          gold: '#fbbf24',
          silver: '#cbd5e1',
          bronze: '#d97706',
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      boxShadow: {
        'glow-emerald': '0 0 20px -5px rgba(16, 185, 129, 0.4)',
        'glow-gold': '0 0 20px -5px rgba(245, 158, 11, 0.4)',
        'glow-ruby': '0 0 20px -5px rgba(239, 68, 68, 0.4)',
        'glow-cyan': '0 0 20px -5px rgba(6, 182, 212, 0.4)',
        'glow-purple': '0 0 20px -5px rgba(139, 92, 246, 0.4)',
      },
      keyframes: {
        pulseFlame: {
          '0%, 100%': { transform: 'scale(1)', filter: 'drop-shadow(0 0 4px rgba(249, 115, 22, 0.6))' },
          '50%': { transform: 'scale(1.12)', filter: 'drop-shadow(0 0 8px rgba(239, 68, 68, 0.9))' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        }
      },
      animation: {
        'pulse-flame': 'pulseFlame 1.8s ease-in-out infinite',
        'shimmer': 'shimmer 2.5s infinite linear',
      }
    },
  },
  plugins: [],
}
