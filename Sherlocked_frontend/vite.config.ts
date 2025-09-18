import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  define: {
    'process.env': JSON.stringify({}),
    'process.platform': JSON.stringify('browser'),
    'process.version': JSON.stringify(''),
  },
  resolve: {
    alias: {
      process: "process/browser"
    }
  }
})
