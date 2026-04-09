import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        vinschool: {
          blue: "#003087",
          light: "#0057B8",
          gold: "#F5A623",
        },
      },
    },
  },
  plugins: [],
};
export default config;
