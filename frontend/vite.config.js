import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/documents': 'http://localhost:8000',
      '/query': 'http://localhost:8000',
    }
  },
  build: {
    outDir: 'dist'
  }
})
