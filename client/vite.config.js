import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    proxy: {
      "/api-local": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api-local/, ""),
      },
      "/api-remote": {
        target: "https://clear-alignment-api.herokuapp.com",
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api-remote/, ""),
      },
    },
  },
});

// export default defineConfig({
//   server: {
//     proxy: {
//       "/api": {
//         target: "https://apiservice.com",
//         changeOrigin: true,
//         secure: false,
//         rewrite: (path) => path.replace(/^\/api/, ""),
//       },
//     },
//   },
//   plugins: [vue()],
// })
