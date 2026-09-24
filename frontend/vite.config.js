import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/query': 'http://127.0.0.1:8000',
      '/part1': 'http://127.0.0.1:8000',
      '/part2': 'http://127.0.0.1:8000',
      '/part3': 'http://127.0.0.1:8000',
      '/part4': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
    }
  }
})
