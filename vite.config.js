import { defineConfig, loadEnv } from 'vite';
import path from 'path';

export default defineConfig(({ command, mode }) => {
  // Load env vars based on mode (development, production)
  // Load .env files based on the mode and command
  const env = loadEnv(mode, path.resolve(process.cwd(), '../../'), ''); // Load from root if possible

  return {
    root: 'src', // Set root to 'src' where index.html resides
    envDir: '../../', // Look for .env files in the project root
    server: {
      host: '0.0.0.0', // Bind to all interfaces
      port: 9000,
      hmr: {
        // Attempt to configure clientPort for Replit/proxied environments
        clientPort: env.REPL_ID || env.CODESPACE_NAME ? 443 : 9000, // Use 443 if common cloud IDE env vars exist
      },
      proxy: {
        '/api': { target: 'http://localhost:8000', changeOrigin: true, secure: false },
        '/media': { target: 'http://localhost:8000', changeOrigin: true, secure: false }
      }
    },
    build: {
      outDir: '../../dist', // Output relative to project root (since root is 'src')
      emptyOutDir: true,
      rollupOptions: {
        input: '/index.html' // Relative to root ('src')
      }
    },
  }
});