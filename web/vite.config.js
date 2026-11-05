import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Project site on GitHub Pages: assets must resolve under the repo path.
export default defineConfig({
  plugins: [react()],
  base: '/rag-eval-harness/',
})
