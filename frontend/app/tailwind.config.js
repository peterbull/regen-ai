/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        "custom-blue": "#05386B",
        "custom-teal": "#379683",
        "custom-mint": "#5CDB95",
        "custom-light-green": "#8EE4AF",
        "custom-off-white": "#EDF5E1",
      },
    },
  },
  plugins: [],
};
