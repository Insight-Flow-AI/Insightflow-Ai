/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#534AB7',
        'primary-light': '#6B5AC9',
        'primary-dark': '#3D3485',
        dark: {
          bg: '#0F1419',
          card: '#1A1F2E',
          border: '#2D3748',
        },
        accent: '#F59E0B',
      },
      backgroundColor: {
        'dark-bg': '#0F1419',
        'dark-card': '#1A1F2E',
      },
    },
  },
  plugins: [],
}
