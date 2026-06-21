import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./features/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#0B1220",
        card: "#111827",
        success: "#22C55E",
        warning: "#F59E0B",
        critical: "#EF4444",
        info: "#3B82F6",
      },
      boxShadow: {
        glow: "0 0 28px rgba(59, 130, 246, 0.20)",
        critical: "0 0 28px rgba(239, 68, 68, 0.20)",
      },
    },
  },
  plugins: [],
};

export default config;
