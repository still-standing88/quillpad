
import { defineConfig } from 'vite';

export default defineConfig({
  root: 'src',
  server: {
    port: 9000,
    open: true,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true, },
      '/media': { target: 'http://localhost:8000', changeOrigin: true, }
    }
  },
  build: {
    outDir: '../dist',
    emptyOutDir: true,
    rollupOptions: { input: '/index.html' }
  },
});
