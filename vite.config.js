import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  // GitHub Pages（https://<owner>.github.io/test-project/）で公開するためのベースパス
  base: '/test-project/',
  plugins: [react()],
})
