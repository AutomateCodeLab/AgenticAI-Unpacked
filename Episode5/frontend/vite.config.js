import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxies /api -> the FastAPI backend (uvicorn server:app --port 8000) so the
// browser never needs CORS and the frontend can just call fetch("/api/...").
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
