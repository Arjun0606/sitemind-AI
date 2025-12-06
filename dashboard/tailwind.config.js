/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Construction/Industrial theme
        primary: {
          50: '#fef7ee',
          100: '#fdedd6',
          200: '#fad6ac',
          300: '#f6b978',
          400: '#f19241',
          500: '#ed7620',  // Main orange - construction
          600: '#de5c13',
          700: '#b84312',
          800: '#933617',
          900: '#772f16',
        },
        slate: {
          850: '#172033',
          950: '#0a0f1a',
        },
      },
      fontFamily: {
        sans: ['Inter var', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}

