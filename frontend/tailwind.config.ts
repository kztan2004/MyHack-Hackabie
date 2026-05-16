import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17212b",
        panel: "#f7f8fb",
        line: "#d9dee8",
        pine: "#0f766e",
        saffron: "#d97706",
        berry: "#be3455"
      }
    }
  },
  plugins: []
};

export default config;
