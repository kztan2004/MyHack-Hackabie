/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        brand: {
          50:  '#f0f0ff',
          100: '#e5e4ff',
          200: '#ceccff',
          300: '#b0acff',
          400: '#9080ff',
          500: '#7c5cfc',
          600: '#6d3ff3',
          700: '#5d2fd0',
          800: '#4c28aa',
          900: '#3f2588',
        },
        dark: {
          50:  '#f8f8fc',
          100: '#f0f0f8',
          200: '#d8d8f0',
          300: '#a8a8d0',
          400: '#7878a8',
          500: '#484878',
          600: '#303058',
          700: '#1e1e3a',
          800: '#141428',
          900: '#0a0a18',
          950: '#050510',
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-brand': 'linear-gradient(135deg, #7c5cfc 0%, #c084fc 100%)',
        'gradient-dark': 'linear-gradient(135deg, #141428 0%, #0a0a18 100%)',
      },
      boxShadow: {
        'glow': '0 0 20px rgba(124, 92, 252, 0.3)',
        'glow-lg': '0 0 40px rgba(124, 92, 252, 0.4)',
        'glass': '0 8px 32px rgba(0, 0, 0, 0.4)',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-up': 'slideUp 0.5s ease-out',
        'fade-in': 'fadeIn 0.4s ease-out',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
