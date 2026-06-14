import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
    // Nginx terminates HTTPS, request masuk lewat reverse proxy.
    hmr: {
      protocol: 'wss',
      clientPort: 443
    },
    // Izinkan host dari nginx (container name) & LAN IP
    allowedHosts: true
  }
});
