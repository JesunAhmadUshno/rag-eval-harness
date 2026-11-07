import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
// The site reads the repo's result files (../level-*, ../real-data, ../model-metrics) at build time,
// so every number on the page is generated, never typed.
export default defineConfig({
  base: '/rag-eval-harness/',
  plugins: [react()],
  server: { fs: { allow: ['..'] } },
  build: { chunkSizeWarningLimit: 1600 },
});
