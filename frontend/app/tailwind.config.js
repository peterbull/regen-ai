/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        electric: "#3cc47c",
        "electric-dark": "#1c5c3a",
        forest: "#1e392a",
        light: "#e9c893",
        tin: "#828081",
      },
    },
  },
  plugins: [],
};
