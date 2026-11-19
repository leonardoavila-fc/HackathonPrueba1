/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        field:   { DEFAULT: "#0d3b1e", light: "#145a2e" },
        slate:   { 850: "#1a2235" },
        accent:  { DEFAULT: "#22c55e", dim: "#15803d" },
        danger:  "#ef4444",
        warning: "#f59e0b",
      },
    },
  },
  plugins: [],
};
