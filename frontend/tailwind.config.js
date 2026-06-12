/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        // Website default — applied everywhere via Tailwind's base styles.
        sans: [
          '"Plus Jakarta Sans"',
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          '"Helvetica Neue"',
          "Arial",
          "sans-serif",
        ],
        // Exam screen — a neutral, widely-available stack that mirrors the
        // look of real computer-based test interfaces. Opt in with `font-exam`.
        exam: [
          "Arial",
          '"Helvetica Neue"',
          "Helvetica",
          '"Segoe UI"',
          "Roboto",
          "sans-serif",
        ],
      },
      colors: {
        // Single source of truth for the primary action color. Maps to the
        // existing blue scale so swapping to brand colors later is one edit.
        brand: {
          light: "#3b82f6", // blue-500
          DEFAULT: "#2563eb", // blue-600
          dark: "#1d4ed8", // blue-700
          darker: "#1e40af", // blue-800
        },
      },
    },
  },
  plugins: [],
};