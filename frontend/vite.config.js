import { defineConfig } from 'vite';
export default defineConfig({
  base: '/ui/',
  build: { outDir: '../backend/static/react', emptyOutDir: true },
  server: { proxy: { '/ask': 'http://127.0.0.1:8000', '/docs': 'http://127.0.0.1:8000', '/openapi.json': 'http://127.0.0.1:8000' } }
});
