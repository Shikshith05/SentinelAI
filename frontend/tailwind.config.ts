import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          500: "#7c3aed",
          400: "#a78bfa"
        }
      }
    }
  },
  plugins: []
};

export default config;
