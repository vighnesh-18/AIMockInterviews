// vite.config.js  ←  FINAL VERSION (copy-paste this entire file)
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],

  server: {
    port: 5173,
    open: true,
    host: true,
    middlewareMode: false,
  },

  // Exclude pdfjs from optimization to allow ?url imports
  optimizeDeps: {
    exclude: ["pdfjs-dist"],
  },

  // Optional: silence large chunk warning (pdfjs is big)
  build: {
    chunkSizeWarningLimit: 1500,
  },
});