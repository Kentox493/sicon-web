/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: {
          primary: "#000000",        // Pure black
          secondary: "#0c1a10",      // Dark green tint
          tertiary: "#142619",       // Lighter green tint for hover
        },
        accent: {
          primary: "#25D366",        // WhatsApp Green
          secondary: "#128C7E",      // WhatsApp Teal
        },
        status: {
          success: "#25D366",
          warning: "#F7B928",
          danger: "#DC3545",
        },
        text: {
          primary: "#ffffff",
          secondary: "#9ca3af",
          accent: "#25D366",
        },
        border: {
          DEFAULT: "#1f2937",
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'glow': '0 0 10px rgba(37, 211, 102, 0.5)',
      }
    },
  },
  plugins: [],
}
