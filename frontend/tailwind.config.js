/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#2563eb",
        secondary: "#64748b",
        accent: "#f8fafc",
        sidebar: "#ffffff",
        border: "#e2e8f0"
      }
    },
  },
  plugins: [],
}
