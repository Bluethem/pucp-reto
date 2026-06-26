import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-poppins)', 'system-ui', 'sans-serif'],
      },
      colors: {
        navy: {
          50:  '#f0f2f8',
          100: '#d9dff0',
          200: '#b3bfe1',
          300: '#8d9fd2',
          400: '#677fc3',
          500: '#4160b4',
          600: '#334d90',
          700: '#25396c',
          800: '#1b2547',
          900: '#0f1528',
          950: '#080b14',
        },
        teal: {
          400: '#2dd4bf',
          500: '#14b8a6',
          600: '#0d9488',
          700: '#0f766e',
        },
      },
    },
  },
  plugins: [],
}

export default config
