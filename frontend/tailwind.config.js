/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        radar: {
          bg: "#03110a",
          grid: "#0e3324",
          sweep: "#22d38a",
        },
      },
    },
  },
  plugins: [],
};
