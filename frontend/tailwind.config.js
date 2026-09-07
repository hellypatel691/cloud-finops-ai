/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // ── Base surfaces ──────────────────────────────────────────────
        bg:        '#161618',
        surface:   '#1e1e20',
        card:      '#242426',
        border:    '#2e2e32',
        // ── Text ──────────────────────────────────────────────────────
        primary:   '#f0f0f0',
        secondary: '#9ca3af',
        muted:     '#555558',
        // ── Accents ───────────────────────────────────────────────────
        accent:    '#7B6EF6',
        'accent-light': '#9d93f8',
        success:   '#4ade80',
        warning:   '#f59e0b',
        danger:    '#f87171',
        info:      '#38bdf8',
        // ── Chart palette ─────────────────────────────────────────────
        'chart-1': '#7B6EF6',
        'chart-2': '#4ade80',
        'chart-3': '#f59e0b',
        'chart-4': '#f97316',
        'chart-5': '#a855f7',
        'chart-6': '#38bdf8',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
        mono: ['JetBrains Mono', 'ui-monospace'],
      },
      borderRadius: {
        xl:  '0.875rem',
        '2xl': '1.125rem',
      },
      boxShadow: {
        card: '0 1px 3px 0 rgba(0,0,0,0.4)',
        glow: '0 0 20px rgba(123,110,246,0.15)',
      },
    },
  },
  plugins: [],
}
