/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      height: {
        '48': '48px',
      },
      borderRadius: {
        '12': '12px',
      },
      fontFamily: {
        sans: ['"IBM Plex Sans Arabic"', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
