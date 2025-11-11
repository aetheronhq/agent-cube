/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "cube-dark": "#1a1a1a",
        "cube-gray": "#2a2a2a",
        "cube-light": "#3a3a3a",
      },
    },
  },
  plugins: [],
}

